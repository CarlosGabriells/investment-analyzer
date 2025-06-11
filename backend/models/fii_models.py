"""
Database models for FII analysis system
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict, Any
from .base import Base

class FIIAnalysis(Base):
    """Store FII analysis results with PDF and market data"""
    __tablename__ = "fii_analysis"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    fii_code: Mapped[str] = mapped_column(String(10), index=True)  # XPLG11, HGLG11, etc.
    fii_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # PDF Analysis Data
    pdf_filename: Mapped[Optional[str]] = mapped_column(String(255))
    pdf_hash: Mapped[Optional[str]] = mapped_column(String(64))  # SHA256 hash for deduplication
    raw_text: Mapped[Optional[str]] = mapped_column(Text)
    
    # Parsed Financial Metrics (JSON field for flexibility)
    financial_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Market Data
    market_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Analysis Results
    analysis_summary: Mapped[Optional[str]] = mapped_column(Text)
    investment_recommendation: Mapped[Optional[str]] = mapped_column(String(50))  # BUY, SELL, HOLD
    risk_rating: Mapped[Optional[str]] = mapped_column(String(20))  # LOW, MEDIUM, HIGH
    
    # Embeddings for similarity search
    embedding_vector: Mapped[Optional[str]] = mapped_column(Text)  # JSON encoded vector
    embedding_model: Mapped[Optional[str]] = mapped_column(String(100))  # Model used for embeddings
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
    
    # Relationships
    rankings: Mapped[List["FIIRanking"]] = relationship("FIIRanking", back_populates="analysis")

class FIIRanking(Base):
    """Store FII rankings and comparisons"""
    __tablename__ = "fii_ranking"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(255), index=True)
    ranking_type: Mapped[str] = mapped_column(String(50))  # 'dividend_yield', 'pvp_ratio', 'similarity', etc.
    
    # Ranking data
    rank_position: Mapped[int] = mapped_column(Integer)
    score: Mapped[Optional[float]] = mapped_column(Float)
    comparison_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Brief description/comment for the FII
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Foreign key to analysis
    analysis_id: Mapped[int] = mapped_column(Integer, ForeignKey("fii_analysis.id"))
    analysis: Mapped["FIIAnalysis"] = relationship("FIIAnalysis", back_populates="rankings")
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class UserSession(Base):
    """Track user sessions for data persistence"""
    __tablename__ = "user_session"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    # Session metadata
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))  # IPv6 compatible
    
    # Session statistics
    total_analyses: Mapped[int] = mapped_column(Integer, default=0)
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
    
    # Preferences (JSON field)
    preferences: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)  # Session expiration

class CacheEntry(Base):
    """Generic cache for API responses and computations"""
    __tablename__ = "cache_entry"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    cache_type: Mapped[str] = mapped_column(String(50), index=True)  # 'market_data', 'embedding', etc.
    
    # Cache data
    data: Mapped[Dict[str, Any]] = mapped_column(JSON)
    
    # Cache metadata
    ttl_seconds: Mapped[Optional[int]] = mapped_column(Integer)  # Time to live
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_accessed: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
