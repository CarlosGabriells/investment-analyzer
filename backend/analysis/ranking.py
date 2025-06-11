"""
FII Ranking system with multiple criteria and brief descriptions
"""

import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
import logging

from backend.models.fii_models import FIIAnalysis, FIIRanking
from backend.models.base import SessionLocal
from backend.analysis.embeddings import embeddings_manager

logger = logging.getLogger(__name__)

class FIIRankingSystem:
    """System for ranking FIIs based on various criteria"""
    
    def __init__(self):
        self.ranking_criteria = {
            "dividend_yield": {
                "name": "Dividend Yield",
                "description": "Ranking por dividend yield (maior é melhor)",
                "order": "desc"
            },
            "pvp_ratio": {
                "name": "P/VP Ratio", 
                "description": "Ranking por P/VP (menor é melhor)",
                "order": "asc"
            },
            "liquidity": {
                "name": "Liquidez",
                "description": "Ranking por liquidez (maior é melhor)", 
                "order": "desc"
            },
            "similarity": {
                "name": "Similaridade",
                "description": "Ranking por similaridade semântica",
                "order": "desc"
            },
            "profitability": {
                "name": "Rentabilidade",
                "description": "Ranking por rentabilidade (maior é melhor)",
                "order": "desc"
            },
            "comprehensive": {
                "name": "Score Geral",
                "description": "Score abrangente considerando múltiplos fatores",
                "order": "desc"
            }
        }
    
    def _extract_numeric_value(self, value: Any) -> Optional[float]:
        """Extract numeric value from various formats"""
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove common characters and convert
            clean_value = value.replace("%", "").replace(",", ".").replace("R$", "").strip()
            try:
                return float(clean_value)
            except (ValueError, TypeError):
                return None
        
        return None
    
    def _generate_fii_description(self, analysis: FIIAnalysis) -> str:
        """Generate a brief, informative description for the FII"""
        parts = []
        
        # Basic info
        if analysis.fii_name:
            parts.append(f"{analysis.fii_name}")
        
        # Key metrics
        metrics = analysis.financial_metrics or {}
        market_data = analysis.market_data or {}
        
        # Dividend yield
        dy = self._extract_numeric_value(
            metrics.get("dividend_yield") or 
            metrics.get("dy") or 
            market_data.get("dividend_yield")
        )
        if dy:
            parts.append(f"DY: {dy:.2f}%")
        
        # P/VP
        pvp = self._extract_numeric_value(
            metrics.get("pvp_ratio") or 
            metrics.get("p_vp") or 
            market_data.get("pvp_ratio")
        )
        if pvp:
            parts.append(f"P/VP: {pvp:.2f}")
        
        # Current price
        price = self._extract_numeric_value(market_data.get("current_price"))
        if price:
            parts.append(f"Preço: R$ {price:.2f}")
        
        # Risk rating
        if analysis.risk_rating:
            parts.append(f"Risco: {analysis.risk_rating}")
        
        # Investment recommendation
        if analysis.investment_recommendation:
            rec_map = {"BUY": "Compra", "SELL": "Venda", "HOLD": "Manter"}
            rec = rec_map.get(analysis.investment_recommendation, analysis.investment_recommendation)
            parts.append(f"Rec.: {rec}")
        
        # Join with separator
        if len(parts) > 1:
            return " | ".join(parts)
        elif parts:
            return parts[0]
        else:
            return f"FII {analysis.fii_code}"
    
    def rank_by_dividend_yield(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Rank FIIs by dividend yield (highest first)"""
        with SessionLocal() as db:
            # Get analyses with dividend yield data
            analyses = db.query(FIIAnalysis).filter(
                FIIAnalysis.session_id == session_id
            ).all()
            
            ranked_fiis = []
            
            for analysis in analyses:
                # Try to extract dividend yield from multiple sources
                dy = None
                
                if analysis.financial_metrics:
                    dy = self._extract_numeric_value(
                        analysis.financial_metrics.get("dividend_yield") or
                        analysis.financial_metrics.get("dy")
                    )
                
                if dy is None and analysis.market_data:
                    dy = self._extract_numeric_value(
                        analysis.market_data.get("dividend_yield")
                    )
                
                if dy is not None:
                    ranked_fiis.append({
                        "analysis": analysis,
                        "score": dy,
                        "metric_value": dy
                    })
            
            # Sort by dividend yield (descending)
            ranked_fiis.sort(key=lambda x: x["score"], reverse=True)
            
            # Create ranking entries
            rankings = []
            for i, item in enumerate(ranked_fiis[:limit]):
                analysis = item["analysis"]
                description = self._generate_fii_description(analysis)
                
                rankings.append({
                    "rank_position": i + 1,
                    "analysis_id": analysis.id,
                    "fii_code": analysis.fii_code,
                    "fii_name": analysis.fii_name,
                    "score": item["score"],
                    "description": description,
                    "metric_details": {
                        "dividend_yield": item["metric_value"]
                    }
                })
            
            return rankings
    
    def rank_by_pvp_ratio(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Rank FIIs by P/VP ratio (lowest first)"""
        with SessionLocal() as db:
            analyses = db.query(FIIAnalysis).filter(
                FIIAnalysis.session_id == session_id
            ).all()
            
            ranked_fiis = []
            
            for analysis in analyses:
                pvp = None
                
                if analysis.financial_metrics:
                    pvp = self._extract_numeric_value(
                        analysis.financial_metrics.get("pvp_ratio") or
                        analysis.financial_metrics.get("p_vp")
                    )
                
                if pvp is None and analysis.market_data:
                    pvp = self._extract_numeric_value(
                        analysis.market_data.get("pvp_ratio")
                    )
                
                if pvp is not None and pvp > 0:  # Valid P/VP ratios should be positive
                    ranked_fiis.append({
                        "analysis": analysis,
                        "score": 1 / pvp,  # Invert for ranking (lower P/VP = higher score)
                        "metric_value": pvp
                    })
            
            # Sort by score (descending, which means lowest P/VP first)
            ranked_fiis.sort(key=lambda x: x["score"], reverse=True)
            
            rankings = []
            for i, item in enumerate(ranked_fiis[:limit]):
                analysis = item["analysis"]
                description = self._generate_fii_description(analysis)
                
                rankings.append({
                    "rank_position": i + 1,
                    "analysis_id": analysis.id,
                    "fii_code": analysis.fii_code,
                    "fii_name": analysis.fii_name,
                    "score": item["metric_value"],  # Show actual P/VP, not inverted score
                    "description": description,
                    "metric_details": {
                        "pvp_ratio": item["metric_value"]
                    }
                })
            
            return rankings
    
    def rank_by_similarity(self, session_id: str, target_analysis_id: int,
                          limit: int = 20) -> List[Dict[str, Any]]:
        """Rank FIIs by similarity to a target FII"""
        similar_fiis = embeddings_manager.find_similar_fiis(
            target_analysis_id, limit=limit, min_similarity=0.1
        )
        
        rankings = []
        for i, similar_fii in enumerate(similar_fiis):
            # Get full analysis for description
            with SessionLocal() as db:
                analysis = db.query(FIIAnalysis).filter(
                    FIIAnalysis.id == similar_fii["analysis_id"]
                ).first()
                
                if analysis:
                    description = self._generate_fii_description(analysis)
                    
                    rankings.append({
                        "rank_position": i + 1,
                        "analysis_id": similar_fii["analysis_id"],
                        "fii_code": similar_fii["fii_code"],
                        "fii_name": similar_fii["fii_name"],
                        "score": similar_fii["similarity_score"],
                        "description": description,
                        "metric_details": {
                            "similarity_score": similar_fii["similarity_score"],
                            "target_recommendation": similar_fii["investment_recommendation"]
                        }
                    })
        
        return rankings
    
    def rank_comprehensive(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Comprehensive ranking considering multiple factors"""
        with SessionLocal() as db:
            analyses = db.query(FIIAnalysis).filter(
                FIIAnalysis.session_id == session_id
            ).all()
            
            scored_fiis = []
            
            for analysis in analyses:
                score_components = {}
                total_score = 0
                weight_sum = 0
                
                # Dividend Yield component (weight: 0.3)
                dy = None
                if analysis.financial_metrics:
                    dy = self._extract_numeric_value(
                        analysis.financial_metrics.get("dividend_yield") or
                        analysis.financial_metrics.get("dy")
                    )
                if dy is None and analysis.market_data:
                    dy = self._extract_numeric_value(analysis.market_data.get("dividend_yield"))
                
                if dy is not None and dy > 0:
                    # Normalize dividend yield (assume 0-15% range)
                    dy_score = min(dy / 15.0, 1.0)
                    total_score += dy_score * 0.3
                    weight_sum += 0.3
                    score_components["dividend_yield"] = dy
                
                # P/VP component (weight: 0.25) - lower is better
                pvp = None
                if analysis.financial_metrics:
                    pvp = self._extract_numeric_value(
                        analysis.financial_metrics.get("pvp_ratio") or
                        analysis.financial_metrics.get("p_vp")
                    )
                if pvp is None and analysis.market_data:
                    pvp = self._extract_numeric_value(analysis.market_data.get("pvp_ratio"))
                
                if pvp is not None and pvp > 0:
                    # Normalize P/VP (assume 0.5-2.0 range, lower is better)
                    pvp_score = max(0, (2.0 - pvp) / 1.5)
                    total_score += pvp_score * 0.25
                    weight_sum += 0.25
                    score_components["pvp_ratio"] = pvp
                
                # Liquidity component (weight: 0.2)
                liquidity = None
                if analysis.market_data:
                    liquidity = self._extract_numeric_value(
                        analysis.market_data.get("liquidity_score") or
                        analysis.market_data.get("avg_volume")
                    )
                
                if liquidity is not None and liquidity > 0:
                    # Normalize liquidity (assume log scale)
                    import math
                    liq_score = min(math.log10(liquidity + 1) / 6.0, 1.0)  # log10(1M) ≈ 6
                    total_score += liq_score * 0.2
                    weight_sum += 0.2
                    score_components["liquidity"] = liquidity
                
                # Risk rating component (weight: 0.15)
                if analysis.risk_rating:
                    risk_scores = {"LOW": 1.0, "MEDIUM": 0.7, "HIGH": 0.3}
                    risk_score = risk_scores.get(analysis.risk_rating, 0.5)
                    total_score += risk_score * 0.15
                    weight_sum += 0.15
                    score_components["risk_rating"] = analysis.risk_rating
                
                # Investment recommendation component (weight: 0.1)
                if analysis.investment_recommendation:
                    rec_scores = {"BUY": 1.0, "HOLD": 0.6, "SELL": 0.2}
                    rec_score = rec_scores.get(analysis.investment_recommendation, 0.5)
                    total_score += rec_score * 0.1
                    weight_sum += 0.1
                    score_components["recommendation"] = analysis.investment_recommendation
                
                # Normalize final score by actual weights used
                if weight_sum > 0:
                    final_score = total_score / weight_sum
                    
                    scored_fiis.append({
                        "analysis": analysis,
                        "score": final_score,
                        "components": score_components,
                        "weight_coverage": weight_sum
                    })
            
            # Sort by score (descending)
            scored_fiis.sort(key=lambda x: x["score"], reverse=True)
            
            rankings = []
            for i, item in enumerate(scored_fiis[:limit]):
                analysis = item["analysis"]
                description = self._generate_fii_description(analysis)
                
                rankings.append({
                    "rank_position": i + 1,
                    "analysis_id": analysis.id,
                    "fii_code": analysis.fii_code,
                    "fii_name": analysis.fii_name,
                    "score": round(item["score"] * 100, 2),  # Convert to percentage
                    "description": description,
                    "metric_details": {
                        "comprehensive_score": item["score"],
                        "components": item["components"],
                        "weight_coverage": item["weight_coverage"]
                    }
                })
            
            return rankings
    
    def save_ranking(self, session_id: str, ranking_type: str,
                    rankings: List[Dict[str, Any]]) -> bool:
        """Save ranking results to database"""
        try:
            with SessionLocal() as db:
                # Delete existing rankings of this type for this session
                db.query(FIIRanking).filter(
                    FIIRanking.session_id == session_id,
                    FIIRanking.ranking_type == ranking_type
                ).delete()
                
                # Create new ranking entries
                for rank_data in rankings:
                    ranking = FIIRanking(
                        session_id=session_id,
                        ranking_type=ranking_type,
                        rank_position=rank_data["rank_position"],
                        score=rank_data["score"],
                        description=rank_data["description"],
                        analysis_id=rank_data["analysis_id"],
                        comparison_metrics=rank_data.get("metric_details", {})
                    )
                    db.add(ranking)
                
                db.commit()
                logger.info(f"Saved {len(rankings)} rankings for type {ranking_type}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving rankings: {e}")
            return False
    
    def get_ranking(self, session_id: str, ranking_type: str) -> List[Dict[str, Any]]:
        """Get saved ranking from database"""
        with SessionLocal() as db:
            rankings = db.query(FIIRanking).filter(
                FIIRanking.session_id == session_id,
                FIIRanking.ranking_type == ranking_type
            ).order_by(FIIRanking.rank_position).all()
            
            result = []
            for ranking in rankings:
                result.append({
                    "rank_position": ranking.rank_position,
                    "analysis_id": ranking.analysis_id,
                    "fii_code": ranking.analysis.fii_code,
                    "fii_name": ranking.analysis.fii_name,
                    "score": ranking.score,
                    "description": ranking.description,
                    "metric_details": ranking.comparison_metrics or {},
                    "created_at": ranking.created_at.isoformat()
                })
            
            return result
    
    def generate_all_rankings(self, session_id: str) -> Dict[str, Any]:
        """Generate and save all types of rankings for a session"""
        results = {}
        
        # Dividend Yield ranking
        try:
            dy_rankings = self.rank_by_dividend_yield(session_id)
            if dy_rankings:
                self.save_ranking(session_id, "dividend_yield", dy_rankings)
                results["dividend_yield"] = len(dy_rankings)
        except Exception as e:
            logger.error(f"Error generating dividend yield ranking: {e}")
            results["dividend_yield"] = f"Error: {e}"
        
        # P/VP ranking
        try:
            pvp_rankings = self.rank_by_pvp_ratio(session_id)
            if pvp_rankings:
                self.save_ranking(session_id, "pvp_ratio", pvp_rankings)
                results["pvp_ratio"] = len(pvp_rankings)
        except Exception as e:
            logger.error(f"Error generating P/VP ranking: {e}")
            results["pvp_ratio"] = f"Error: {e}"
        
        # Comprehensive ranking
        try:
            comp_rankings = self.rank_comprehensive(session_id)
            if comp_rankings:
                self.save_ranking(session_id, "comprehensive", comp_rankings)
                results["comprehensive"] = len(comp_rankings)
        except Exception as e:
            logger.error(f"Error generating comprehensive ranking: {e}")
            results["comprehensive"] = f"Error: {e}"
        
        return results


# Global instance
ranking_system = FIIRankingSystem()
