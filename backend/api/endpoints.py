"""
API simplificada para análise de PDFs de FIIs
Endpoint único para upload e análise com IA
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import tempfile
import uuid
import hashlib
from typing import Optional, Dict, Any, List
import logging

from backend.analysis.pdf_analyzer import PDFAnalyzer, sync_quick_pdf_analysis
from backend.analysis.embeddings import embeddings_manager
from backend.analysis.ranking import ranking_system
from backend.models.fii_models import FIIAnalysis, FIIRanking, UserSession
from backend.models.base import get_db, init_db
from backend.database.cache_manager import session_manager
from sqlalchemy.orm import Session

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(
    title="FII PDF Analyzer",
    description="API para análise inteligente de relatórios de Fundos Imobiliários via upload de PDF",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância global do analisador
pdf_analyzer = PDFAnalyzer()

# Inicializar banco de dados ao iniciar a aplicação
@app.on_event("startup")
async def startup_event():
    """Inicializar recursos ao iniciar a aplicação"""
    try:
        logger.info("Inicializando banco de dados...")
        init_db()
        logger.info("Banco de dados inicializado com sucesso")
        
        # Verificar se o modelo de embeddings está disponível
        logger.info("Verificando modelo de embeddings...")
        stats = embeddings_manager.get_stats()
        logger.info(f"Modelo de embeddings carregado: {stats['model_name']}")
        
    except Exception as e:
        logger.error(f"Erro durante inicialização: {e}")
        raise e

@app.post("/analyze-pdf")
async def analyze_pdf_report(
    pdf_file: UploadFile = File(..., description="Arquivo PDF do relatório do FII"),
    include_market_comparison: bool = Form(default=True, description="Incluir comparação com mercado"),
    include_portfolio: bool = Form(default=True, description="Incluir análise da carteira"),
    session_id: str = Form(default=None, description="ID da sessão do usuário"),
    db: Session = Depends(get_db)
):
    """
    Endpoint principal para análise de PDF de relatório de FII
    
    - **pdf_file**: Arquivo PDF do relatório (obrigatório)
    - **include_market_comparison**: Se deve incluir comparação com médias de mercado
    - **include_portfolio**: Se deve incluir análise da composição da carteira
    - **session_id**: ID da sessão para persistência de dados
    
    Retorna análise completa com:
    - Informações básicas do fundo
    - Métricas financeiras extraídas
    - Análise de investimento com IA
    - Comparação com mercado (opcional)
    - Composição da carteira (opcional)
    - Embeddings para ranking de similaridade
    """
    
    # Validar arquivo
    if not pdf_file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Arquivo deve ser um PDF válido"
        )
    
    temp_file_path = None
    try:
        logger.info(f"Iniciando análise do arquivo: {pdf_file.filename}")
        
        # Ler conteúdo do arquivo
        pdf_content = await pdf_file.read()
        
        # Gerar hash do arquivo para cache
        file_hash = hashlib.md5(pdf_content).hexdigest()
        
        # Criar ou recuperar sessão
        if not session_id:
            session_id = str(uuid.uuid4())
        
        session = session_manager.get_or_create_session(session_id, db)
        
        # Verificar cache
        cache_key = f"pdf_analysis_{file_hash}"
        cached_result = session_manager.get_cached_data(cache_key, db)
        
        if cached_result:
            logger.info(f"Resultado encontrado em cache para {pdf_file.filename}")
            result = cached_result
        else:
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            # Análise principal com dados de mercado
            result = await pdf_analyzer.analyze_pdf_report(
                temp_file_path, 
                include_market_data=include_market_comparison,
                include_portfolio=include_portfolio
            )
            
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
            
            # Salvar resultado em cache
            session_manager.set_cached_data(cache_key, result, ttl_hours=24, db=db)
        
        # Criar representação textual para embeddings
        text_representation = embeddings_manager.create_text_representation(
            result.get("fund_info", {}),
            result.get("financial_metrics", {}),
            result.get("market_data", {}),
            result.get("ai_analysis", {}).get("investment_summary", "")
        )
        
        # Gerar embeddings
        embedding = embeddings_manager.generate_embedding(text_representation)
        
        # Salvar análise no banco de dados
        fii_analysis = FIIAnalysis(
            session_id=session_id,
            fii_code=result.get("fund_info", {}).get("fund_code", ""),
            fund_name=result.get("fund_info", {}).get("fund_name", ""),
            financial_metrics=result.get("financial_metrics", {}),
            market_data=result.get("market_data", {}),
            analysis_summary=result.get("ai_analysis", {}).get("investment_summary", ""),
            embedding_vector=embedding.tolist() if embedding is not None else None,
            text_representation=text_representation,
            pdf_filename=pdf_file.filename,
            file_hash=file_hash
        )
        
        db.add(fii_analysis)
        db.commit()
        db.refresh(fii_analysis)
        
        # Adicionar metadados da requisição
        result["request_info"] = {
            "filename": pdf_file.filename,
            "file_size": len(pdf_content),
            "include_market_comparison": include_market_comparison,
            "include_portfolio": include_portfolio,
            "session_id": session_id,
            "analysis_id": fii_analysis.id,
            "cached": cached_result is not None
        }
        
        logger.info(f"Análise concluída para {pdf_file.filename}")
        return JSONResponse(content=result)
            
    except Exception as e:
        logger.error(f"Erro durante análise: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno durante análise: {str(e)}"
        )
    finally:
        # Limpar arquivo temporário, se foi criado
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.post("/quick-analysis")
async def quick_pdf_analysis(pdf_file: UploadFile = File(...)):
    """
    Análise rápida - apenas informações básicas e métricas
    Útil para quando você quer uma visão geral rápida do FII
    """
    
    if not pdf_file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser um PDF")
    
    temp_file_path = None
    try:
        pdf_content = await pdf_file.read()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_content)
            temp_file_path = temp_file.name
        
        # Extrair apenas o básico
        pdf_text = pdf_analyzer.extract_text_from_pdf(temp_file_path)
        
        if pdf_text.startswith("Erro:"): # Check for specific error message from extract_text_from_pdf
            raise HTTPException(status_code=400, detail=pdf_text)

        fund_info = pdf_analyzer.identify_fund_info(pdf_text)
        metrics = pdf_analyzer.extract_financial_metrics(pdf_text)
        
        result = {
            "filename": pdf_file.filename,
            "fund_info": fund_info,
            "financial_metrics": metrics,
            "success": True
        }
        
        return JSONResponse(content=result)
            
    except Exception as e:
        logger.error(f"Erro na análise rápida: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.get("/health")
async def health_check():
    """Verificação de saúde da API"""
    return {
        "status": "healthy",
        "message": "FII PDF Analyzer API está funcionando",
        "endpoints": {
            "analyze-pdf": "POST - Análise completa de PDF",
            "quick-analysis": "POST - Análise rápida de PDF",
            "ranking": "GET - Ranking de FIIs por critério",
            "similar-fiis": "GET - FIIs similares por embeddings", 
            "session-fiis": "GET - FIIs analisados na sessão",
            "health": "GET - Status da API"
        }
    }

@app.get("/ranking/{criteria}")
async def get_fii_ranking(
    criteria: str,
    session_id: str = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Obter ranking de FIIs por critério específico
    
    - **criteria**: Critério de ranking (dividend_yield, pvp_ratio, liquidity, similarity, comprehensive)
    - **session_id**: ID da sessão (opcional, se não fornecido considera todos os FIIs)
    - **limit**: Número máximo de resultados
    """
    try:
        # Buscar análises da sessão ou todas
        query = db.query(FIIAnalysis)
        if session_id:
            query = query.filter(FIIAnalysis.session_id == session_id)
        
        analyses = query.all()
        
        if not analyses:
            return JSONResponse(content={
                "ranking": [],
                "message": "Nenhuma análise encontrada para ranking",
                "criteria": criteria,
                "total_fiis": 0
            })
        
        # Gerar ranking
        ranking_results = ranking_system.rank_fiis(analyses, criteria)
        
        # Salvar ranking no banco
        for result in ranking_results[:limit]:
            existing_ranking = db.query(FIIRanking).filter(
                FIIRanking.fii_code == result["fii_code"],
                FIIRanking.ranking_criteria == criteria
            ).first()
            
            if not existing_ranking:
                fii_ranking = FIIRanking(
                    fii_code=result["fii_code"],
                    ranking_criteria=criteria,
                    score=result["score"],
                    position=result["position"],
                    brief_description=result["brief_description"]
                )
                db.add(fii_ranking)
        
        db.commit()
        
        return JSONResponse(content={
            "ranking": ranking_results[:limit],
            "criteria": criteria,
            "total_fiis": len(analyses),
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/similar-fiis/{fii_code}")
async def get_similar_fiis(
    fii_code: str,
    session_id: str = None,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Encontrar FIIs similares usando embeddings
    
    - **fii_code**: Código do FII de referência
    - **session_id**: ID da sessão (opcional)
    - **limit**: Número máximo de FIIs similares
    """
    try:
        # Buscar análise de referência
        query = db.query(FIIAnalysis).filter(FIIAnalysis.fii_code == fii_code)
        if session_id:
            query = query.filter(FIIAnalysis.session_id == session_id)
        
        reference_analysis = query.first()
        if not reference_analysis or not reference_analysis.embedding_vector:
            raise HTTPException(
                status_code=404, 
                detail=f"FII {fii_code} não encontrado ou sem embeddings"
            )
        
        # Buscar todas as outras análises
        query = db.query(FIIAnalysis).filter(
            FIIAnalysis.fii_code != fii_code,
            FIIAnalysis.embedding_vector.isnot(None)
        )
        if session_id:
            query = query.filter(FIIAnalysis.session_id == session_id)
        
        other_analyses = query.all()
        
        if not other_analyses:
            return JSONResponse(content={
                "reference_fii": fii_code,
                "similar_fiis": [],
                "message": "Nenhum FII comparável encontrado"
            })
        
        # Calcular similaridades
        similar_fiis = embeddings_manager.find_similar_fiis(
            reference_analysis, other_analyses, top_k=limit
        )
        
        return JSONResponse(content={
            "reference_fii": fii_code,
            "reference_name": reference_analysis.fund_name,
            "similar_fiis": similar_fiis,
            "total_compared": len(other_analyses)
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar FIIs similares: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/session/{session_id}/fiis")
async def get_session_fiis(session_id: str, db: Session = Depends(get_db)):
    """
    Obter todos os FIIs analisados em uma sessão
    
    - **session_id**: ID da sessão
    """
    try:
        analyses = db.query(FIIAnalysis).filter(
            FIIAnalysis.session_id == session_id
        ).all()
        
        fiis_data = []
        for analysis in analyses:
            fiis_data.append({
                "id": analysis.id,
                "fii_code": analysis.fii_code,
                "fund_name": analysis.fund_name,
                "financial_metrics": analysis.financial_metrics,
                "analysis_summary": analysis.analysis_summary,
                "created_at": analysis.created_at.isoformat(),
                "pdf_filename": analysis.pdf_filename
            })
        
        return JSONResponse(content={
            "session_id": session_id,
            "total_fiis": len(fiis_data),
            "fiis": fiis_data
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar FIIs da sessão: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/session/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """
    Excluir uma sessão e todos os dados associados
    
    - **session_id**: ID da sessão a ser excluída
    """
    try:
        # Excluir análises da sessão
        db.query(FIIAnalysis).filter(FIIAnalysis.session_id == session_id).delete()
        
        # Excluir sessão
        session_manager.delete_session(session_id, db)
        
        db.commit()
        
        return JSONResponse(content={
            "message": f"Sessão {session_id} excluída com sucesso",
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"Erro ao excluir sessão: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """
    Obter estatísticas do sistema
    """
    try:
        total_analyses = db.query(FIIAnalysis).count()
        total_sessions = db.query(UserSession).count()
        
        # Stats de embeddings
        embeddings_stats = embeddings_manager.get_stats()
        
        return JSONResponse(content={
            "total_analyses": total_analyses,
            "total_sessions": total_sessions,
            "embeddings_model": embeddings_stats["model_name"],
            "embedding_dimension": embeddings_stats["embedding_dimension"],
            "cache_stats": session_manager.get_cache_stats(db)
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Página inicial da API"""
    return {
        "message": "FII PDF Analyzer API",
        "description": "API para análise inteligente de relatórios de Fundos Imobiliários",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Tratamento de erros global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor", "error": str(exc)}
    )

if __name__ == "__main__":
    # Verificar variáveis de ambiente necessárias
    if not os.getenv("GROQ_API_KEY"):
        logger.error("GROQ_API_KEY não encontrada nas variáveis de ambiente!")
        exit(1)
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
