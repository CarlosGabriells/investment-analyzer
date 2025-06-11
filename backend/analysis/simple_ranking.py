"""Sistema de ranking simples"""

from typing import List, Dict, Any
from models.simple_models import FIIAnalysis, SimpleRanking
from models.base import SessionLocal

class SimpleRankingSystem:
    
    def rank_by_dividend_yield(self, session_id: str) -> List[Dict]:
        """Ranking por Dividend Yield"""
        with SessionLocal() as db:
            analyses = db.query(FIIAnalysis).filter(
                FIIAnalysis.session_id == session_id
            ).all()
            
            ranked = []
            for analysis in analyses:
                metrics = analysis.financial_metrics or {}
                dy = metrics.get('dividend_yield', 0)
                
                if dy and dy > 0:
                    ranked.append({
                        'fii_code': analysis.fii_code,
                        'fii_name': analysis.fii_name,
                        'score': dy,
                        'metric': f"{dy}%"
                    })
            
            # Ordenar por DY (maior primeiro)
            ranked.sort(key=lambda x: x['score'], reverse=True)
            
            # Adicionar posições
            for i, item in enumerate(ranked):
                item['position'] = i + 1
            
            return ranked
    
    def rank_by_pvp(self, session_id: str) -> List[Dict]:
        """Ranking por P/VP"""
        with SessionLocal() as db:
            analyses = db.query(FIIAnalysis).filter(
                FIIAnalysis.session_id == session_id
            ).all()
            
            ranked = []
            for analysis in analyses:
                metrics = analysis.financial_metrics or {}
                pvp = metrics.get('p_vp', 0)
                
                if pvp and pvp > 0:
                    ranked.append({
                        'fii_code': analysis.fii_code,
                        'fii_name': analysis.fii_name,
                        'score': pvp,
                        'metric': f"{pvp:.2f}"
                    })
            
            # Ordenar por P/VP (menor primeiro)
            ranked.sort(key=lambda x: x['score'])
            
            # Adicionar posições
            for i, item in enumerate(ranked):
                item['position'] = i + 1
            
            return ranked

# Instância global
ranking_system = SimpleRankingSystem()