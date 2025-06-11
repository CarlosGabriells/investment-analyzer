"""
Embeddings system for FII semantic analysis and similarity
Uses sentence-transformers for financial text analysis
"""

import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
import logging

from backend.models.fii_models import FIIAnalysis
from backend.models.base import SessionLocal
from backend.database.cache_manager import cache_manager

logger = logging.getLogger(__name__)

class FIIEmbeddingsManager:
    """Manages embeddings for FII analysis and similarity comparison"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with a sentence-transformer model
        all-MiniLM-L6-v2 é um modelo rápido e eficiente para português/inglês
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model with caching"""
        try:
            # Check if model is cached
            cached_model = cache_manager.get("model", model_name=self.model_name)
            
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
            # Cache model info (not the actual model, just metadata)
            cache_manager.set(
                "model", 
                {"model_name": self.model_name, "loaded_at": str(np.datetime64('now'))},
                ttl=86400,  # 24 hours
                model_name=self.model_name
            )
            
            logger.info(f"Model {self.model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {e}")
            raise
    
    def create_fii_text_representation(self, analysis_data: Dict[str, Any]) -> str:
        """
        Create a comprehensive text representation of FII for embeddings
        Combines financial metrics, analysis summary, and key characteristics
        """
        parts = []
        
        # FII basic info
        if fii_code := analysis_data.get("fii_code"):
            parts.append(f"FII {fii_code}")
        
        if fii_name := analysis_data.get("fii_name"):
            parts.append(f"Nome: {fii_name}")
        
        # Financial metrics
        metrics = analysis_data.get("financial_metrics", {})
        if metrics:
            metric_texts = []
            
            # P/VP ratio
            if pvp := metrics.get("pvp_ratio") or metrics.get("p_vp"):
                metric_texts.append(f"P/VP {pvp}")
            
            # Dividend yield
            if dy := metrics.get("dividend_yield") or metrics.get("dy"):
                metric_texts.append(f"Dividend Yield {dy}%")
            
            # Net worth / Patrimônio líquido
            if pl := metrics.get("patrimonio_liquido") or metrics.get("net_worth"):
                metric_texts.append(f"Patrimônio líquido {pl}")
            
            # Profitability / Rentabilidade
            if rent := metrics.get("rentabilidade"):
                metric_texts.append(f"Rentabilidade {rent}")
            
            # Liquidity
            if liq := metrics.get("liquidez") or metrics.get("liquidity"):
                metric_texts.append(f"Liquidez {liq}")
            
            if metric_texts:
                parts.append("Métricas: " + ", ".join(metric_texts))
        
        # Market data
        market_data = analysis_data.get("market_data", {})
        if market_data:
            market_texts = []
            
            if price := market_data.get("current_price"):
                market_texts.append(f"Preço atual R$ {price}")
            
            if volume := market_data.get("avg_volume"):
                market_texts.append(f"Volume médio {volume}")
            
            if risk := market_data.get("risk_rating"):
                market_texts.append(f"Risco {risk}")
            
            if market_texts:
                parts.append("Mercado: " + ", ".join(market_texts))
        
        # Analysis summary
        if summary := analysis_data.get("analysis_summary"):
            # Truncate long summaries to avoid embedding size issues
            summary = summary[:500] + "..." if len(summary) > 500 else summary
            parts.append(f"Análise: {summary}")
        
        # Investment recommendation
        if recommendation := analysis_data.get("investment_recommendation"):
            parts.append(f"Recomendação: {recommendation}")
        
        # Risk rating
        if risk_rating := analysis_data.get("risk_rating"):
            parts.append(f"Classificação de risco: {risk_rating}")
        
        # Join all parts
        full_text = ". ".join(parts)
        
        # Ensure text is not too long for the model
        if len(full_text) > 2000:
            full_text = full_text[:2000] + "..."
        
        return full_text
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        if not self.model:
            self._load_model()
        
        try:
            # Generate embedding
            embedding = self.model.encode([text], convert_to_tensor=False)[0]
            
            # Convert to list for JSON serialization
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def update_fii_embedding(self, analysis_id: int) -> bool:
        """Update embedding for a specific FII analysis"""
        with SessionLocal() as db:
            analysis = db.query(FIIAnalysis).filter(
                FIIAnalysis.id == analysis_id
            ).first()
            
            if not analysis:
                logger.warning(f"Analysis {analysis_id} not found")
                return False
            
            try:
                # Create text representation
                analysis_data = {
                    "fii_code": analysis.fii_code,
                    "fii_name": analysis.fii_name,
                    "financial_metrics": analysis.financial_metrics,
                    "market_data": analysis.market_data,
                    "analysis_summary": analysis.analysis_summary,
                    "investment_recommendation": analysis.investment_recommendation,
                    "risk_rating": analysis.risk_rating
                }
                
                text_repr = self.create_fii_text_representation(analysis_data)
                
                # Generate embedding
                embedding = self.generate_embedding(text_repr)
                
                # Store embedding (as JSON string)
                analysis.embedding_vector = json.dumps(embedding)
                analysis.embedding_model = self.model_name
                
                db.commit()
                
                logger.info(f"Updated embedding for analysis {analysis_id} ({analysis.fii_code})")
                return True
                
            except Exception as e:
                logger.error(f"Error updating embedding for analysis {analysis_id}: {e}")
                db.rollback()
                return False
    
    def find_similar_fiis(self, target_analysis_id: int, limit: int = 10,
                          min_similarity: float = 0.3) -> List[Dict[str, Any]]:
        """Find FIIs similar to the target analysis"""
        with SessionLocal() as db:
            target_analysis = db.query(FIIAnalysis).filter(
                FIIAnalysis.id == target_analysis_id
            ).first()
            
            if not target_analysis or not target_analysis.embedding_vector:
                logger.warning(f"Target analysis {target_analysis_id} not found or no embedding")
                return []
            
            try:
                # Get target embedding
                target_embedding = np.array(json.loads(target_analysis.embedding_vector))
                
                # Get all other analyses with embeddings
                other_analyses = db.query(FIIAnalysis).filter(
                    FIIAnalysis.id != target_analysis_id,
                    FIIAnalysis.embedding_vector.isnot(None),
                    FIIAnalysis.embedding_model == self.model_name
                ).all()
                
                similarities = []
                
                for analysis in other_analyses:
                    try:
                        other_embedding = np.array(json.loads(analysis.embedding_vector))
                        
                        # Calculate cosine similarity
                        similarity = cosine_similarity(
                            target_embedding.reshape(1, -1),
                            other_embedding.reshape(1, -1)
                        )[0][0]
                        
                        if similarity >= min_similarity:
                            similarities.append({
                                "analysis_id": analysis.id,
                                "fii_code": analysis.fii_code,
                                "fii_name": analysis.fii_name,
                                "similarity_score": float(similarity),
                                "investment_recommendation": analysis.investment_recommendation,
                                "risk_rating": analysis.risk_rating,
                                "created_at": analysis.created_at.isoformat()
                            })
                    
                    except Exception as e:
                        logger.warning(f"Error calculating similarity for analysis {analysis.id}: {e}")
                        continue
                
                # Sort by similarity and limit results
                similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
                return similarities[:limit]
                
            except Exception as e:
                logger.error(f"Error finding similar FIIs: {e}")
                return []
    
    def batch_update_embeddings(self, session_id: Optional[str] = None,
                               limit: Optional[int] = None) -> Dict[str, Any]:
        """Update embeddings for multiple analyses"""
        with SessionLocal() as db:
            query = db.query(FIIAnalysis).filter(
                FIIAnalysis.embedding_vector.is_(None)
            )
            
            if session_id:
                query = query.filter(FIIAnalysis.session_id == session_id)
            
            if limit:
                query = query.limit(limit)
            
            analyses = query.all()
            
            results = {
                "total_processed": 0,
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            for analysis in analyses:
                results["total_processed"] += 1
                
                if self.update_fii_embedding(analysis.id):
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Failed to update embedding for {analysis.fii_code}")
            
            return results
    
    def get_embedding_statistics(self) -> Dict[str, Any]:
        """Get statistics about embeddings in the database"""
        with SessionLocal() as db:
            total_analyses = db.query(FIIAnalysis).count()
            
            with_embeddings = db.query(FIIAnalysis).filter(
                FIIAnalysis.embedding_vector.isnot(None)
            ).count()
            
            by_model = {}
            models = db.query(FIIAnalysis.embedding_model).distinct().all()
            
            for (model_name,) in models:
                if model_name:
                    count = db.query(FIIAnalysis).filter(
                        FIIAnalysis.embedding_model == model_name
                    ).count()
                    by_model[model_name] = count
            
            return {
                "total_analyses": total_analyses,
                "with_embeddings": with_embeddings,
                "without_embeddings": total_analyses - with_embeddings,
                "coverage_percentage": (with_embeddings / total_analyses * 100) if total_analyses > 0 else 0,
                "by_model": by_model,
                "current_model": self.model_name
            }


# Global instance
embeddings_manager = FIIEmbeddingsManager()
