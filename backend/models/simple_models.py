from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from datetime import datetime
from .base import Base

class FIIAnalysis(Base):
    """Análise detalhada de FII"""
    __tablename__ = "fii_analysis"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), index=True)  # Para cache por sessão
    fii_code = Column(String(10), index=True)     # BRCR11, etc.
    fii_name = Column(String(255))
    
    # Dados básicos do fundo
    fund_info = Column(JSON)          # Informações básicas (ticker, nome, CNPJ, etc.)
    
    # Métricas financeiras
    financial_metrics = Column(JSON)  # DY, P/VP, receitas, despesas, etc.
    
    # Análise detalhada estruturada
    detailed_analysis = Column(JSON)  # Análise dos 14 pontos estruturados
    
    # Metadados
    pdf_filename = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())

class SimpleRanking(Base):
    """Ranking simples por critério"""
    __tablename__ = "simple_ranking"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), index=True)
    criteria = Column(String(50))     # 'dividend_yield', 'pvp', etc.
    fii_code = Column(String(10))
    position = Column(Integer)        # 1, 2, 3...
    score = Column(String(50))        # Valor da métrica
    created_at = Column(DateTime, server_default=func.now())