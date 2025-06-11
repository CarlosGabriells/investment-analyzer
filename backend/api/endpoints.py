"""API simplificada"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import uuid
import os

from analysis.pdf_analyzer import pdf_analyzer
from analysis.simple_ranking import ranking_system
from database.simple_cache import simple_cache
from models.simple_models import FIIAnalysis
from models.base import get_db, init_db

app = FastAPI(title="FII Analyzer Simplificado")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()

@app.post("/analyze")
async def analyze_pdf(
    pdf_file: UploadFile = File(...),
    session_id: str = None
):
    """Analisa PDF de FII"""
    
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Cache key
    cache_key = f"session_{session_id}_{pdf_file.filename}"
    cached = simple_cache.get(cache_key)
    if cached:
        return {"cached": True, "session_id": session_id, **cached}
    
    # Análise
    content = await pdf_file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        tmp.write(content)
        result = pdf_analyzer.analyze_pdf(tmp.name)
        os.unlink(tmp.name)
    
    if "error" in result:
        # Return the full error response for debugging instead of raising HTTPException
        return {"session_id": session_id, "status": "error", **result}
    
    # Salvar no cache e DB
    simple_cache.set(cache_key, result)
    
    # Salvar no banco (opcional)
    with next(get_db()) as db:
        analysis = FIIAnalysis(
            session_id=session_id,
            fii_code=result.get("fund_info", {}).get("ticker", ""),
            fii_name=result.get("fund_info", {}).get("nome", ""),
            fund_info=result.get("fund_info", {}),
            financial_metrics=result.get("financial_metrics", {}),
            detailed_analysis=result.get("detailed_analysis", {}),
            pdf_filename=pdf_file.filename
        )
        db.add(analysis)
        db.commit()
    
    return {"session_id": session_id, **result}

@app.get("/ranking/{criteria}")
async def get_ranking(criteria: str, session_id: str):
    """Rankings simples"""
    
    cache_key = f"ranking_{session_id}_{criteria}"
    cached = simple_cache.get(cache_key)
    if cached:
        return {"cached": True, "ranking": cached}
    
    if criteria == "dividend_yield":
        ranking = ranking_system.rank_by_dividend_yield(session_id)
    elif criteria == "pvp":
        ranking = ranking_system.rank_by_pvp(session_id)
    else:
        raise HTTPException(400, "Critério inválido")
    
    simple_cache.set(cache_key, ranking, ttl_hours=1)
    return {"ranking": ranking}

@app.get("/analysis/{session_id}")
async def get_analyses(session_id: str):
    """Lista todas as análises de uma sessão"""
    with next(get_db()) as db:
        analyses = db.query(FIIAnalysis).filter(
            FIIAnalysis.session_id == session_id
        ).all()
        
        result = []
        for analysis in analyses:
            result.append({
                "id": analysis.id,
                "fii_code": analysis.fii_code,
                "fii_name": analysis.fii_name,
                "fund_info": analysis.fund_info,
                "financial_metrics": analysis.financial_metrics,
                "detailed_analysis": analysis.detailed_analysis,
                "pdf_filename": analysis.pdf_filename,
                "created_at": analysis.created_at.isoformat()
            })
        
        return {"session_id": session_id, "analyses": result}

@app.get("/analysis/{session_id}/{fii_code}")
async def get_specific_analysis(session_id: str, fii_code: str):
    """Obtém análise específica de um FII"""
    with next(get_db()) as db:
        analysis = db.query(FIIAnalysis).filter(
            FIIAnalysis.session_id == session_id,
            FIIAnalysis.fii_code == fii_code
        ).first()
        
        if not analysis:
            raise HTTPException(404, "Análise não encontrada")
        
        return {
            "fund_info": analysis.fund_info,
            "financial_metrics": analysis.financial_metrics,
            "detailed_analysis": analysis.detailed_analysis,
            "pdf_filename": analysis.pdf_filename,
            "created_at": analysis.created_at.isoformat()
        }

@app.get("/health")
async def health():
    return {"status": "ok"}