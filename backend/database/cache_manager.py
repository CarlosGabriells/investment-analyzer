"""
Cache manager for FII analysis system
Handles caching of API responses, embeddings, and analysis results
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.models.fii_models import CacheEntry
from backend.models.base import SessionLocal


class CacheManager:
    """Manages cache entries with TTL and automatic cleanup"""
    
    def __init__(self, default_ttl: int = 3600):  # 1 hour default
        self.default_ttl = default_ttl
    
    def _generate_cache_key(self, cache_type: str, **kwargs) -> str:
        """Generate a consistent cache key from parameters"""
        # Sort kwargs for consistent key generation
        sorted_params = sorted(kwargs.items())
        param_str = json.dumps(sorted_params, sort_keys=True)
        
        # Create hash for long keys
        key_data = f"{cache_type}:{param_str}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def get(self, cache_type: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get cached data if available and not expired"""
        cache_key = self._generate_cache_key(cache_type, **kwargs)
        
        with SessionLocal() as db:
            entry = db.query(CacheEntry).filter(
                CacheEntry.cache_key == cache_key
            ).first()
            
            if not entry:
                return None
            
            # Check expiration
            if entry.is_expired:
                db.delete(entry)
                db.commit()
                return None
            
            # Update access count and timestamp
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()
            db.commit()
            
            return entry.data
    
    def set(self, cache_type: str, data: Dict[str, Any], 
            ttl: Optional[int] = None, **kwargs) -> str:
        """Store data in cache with TTL"""
        cache_key = self._generate_cache_key(cache_type, **kwargs)
        ttl = ttl or self.default_ttl
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        with SessionLocal() as db:
            # Check if entry exists
            entry = db.query(CacheEntry).filter(
                CacheEntry.cache_key == cache_key
            ).first()
            
            if entry:
                # Update existing entry
                entry.data = data
                entry.ttl_seconds = ttl
                entry.expires_at = expires_at
                entry.last_accessed = datetime.utcnow()
            else:
                # Create new entry
                entry = CacheEntry(
                    cache_key=cache_key,
                    cache_type=cache_type,
                    data=data,
                    ttl_seconds=ttl,
                    expires_at=expires_at
                )
                db.add(entry)
            
            db.commit()
            return cache_key
    
    def delete(self, cache_type: str, **kwargs) -> bool:
        """Delete specific cache entry"""
        cache_key = self._generate_cache_key(cache_type, **kwargs)
        
        with SessionLocal() as db:
            entry = db.query(CacheEntry).filter(
                CacheEntry.cache_key == cache_key
            ).first()
            
            if entry:
                db.delete(entry)
                db.commit()
                return True
            return False
    
    def cleanup_expired(self) -> int:
        """Remove all expired cache entries"""
        with SessionLocal() as db:
            current_time = datetime.utcnow()
            expired_entries = db.query(CacheEntry).filter(
                and_(
                    CacheEntry.expires_at.isnot(None),
                    CacheEntry.expires_at < current_time
                )
            )
            
            count = expired_entries.count()
            expired_entries.delete(synchronize_session=False)
            db.commit()
            
            return count
    
    def clear_cache_type(self, cache_type: str) -> int:
        """Clear all entries of a specific cache type"""
        with SessionLocal() as db:
            entries = db.query(CacheEntry).filter(
                CacheEntry.cache_type == cache_type
            )
            
            count = entries.count()
            entries.delete(synchronize_session=False)
            db.commit()
            
            return count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with SessionLocal() as db:
            total_entries = db.query(CacheEntry).count()
            
            # Get stats by cache type
            type_stats = {}
            cache_types = db.query(CacheEntry.cache_type).distinct().all()
            
            for (cache_type,) in cache_types:
                type_count = db.query(CacheEntry).filter(
                    CacheEntry.cache_type == cache_type
                ).count()
                
                expired_count = db.query(CacheEntry).filter(
                    and_(
                        CacheEntry.cache_type == cache_type,
                        CacheEntry.expires_at < datetime.utcnow()
                    )
                ).count()
                
                type_stats[cache_type] = {
                    "total": type_count,
                    "expired": expired_count,
                    "active": type_count - expired_count
                }
            
            return {
                "total_entries": total_entries,
                "by_type": type_stats,
                "last_cleanup": datetime.utcnow().isoformat()
            }


class SessionManager:
    """Manages user sessions for data persistence"""
    
    def __init__(self, session_ttl: int = 86400):  # 24 hours default
        self.session_ttl = session_ttl
    
    def create_session(self, session_id: str, user_agent: Optional[str] = None,
                      ip_address: Optional[str] = None) -> str:
        """Create or update user session"""
        from ..models.fii_models import UserSession
        
        expires_at = datetime.utcnow() + timedelta(seconds=self.session_ttl)
        
        with SessionLocal() as db:
            session_obj = db.query(UserSession).filter(
                UserSession.session_id == session_id
            ).first()
            
            if session_obj:
                # Update existing session
                session_obj.last_activity = datetime.utcnow()
                session_obj.expires_at = expires_at
                if user_agent:
                    session_obj.user_agent = user_agent
                if ip_address:
                    session_obj.ip_address = ip_address
            else:
                # Create new session
                session_obj = UserSession(
                    session_id=session_id,
                    user_agent=user_agent,
                    ip_address=ip_address,
                    expires_at=expires_at
                )
                db.add(session_obj)
            
            db.commit()
            return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data if valid"""
        from ..models.fii_models import UserSession
        
        with SessionLocal() as db:
            session_obj = db.query(UserSession).filter(
                UserSession.session_id == session_id
            ).first()
            
            if not session_obj:
                return None
            
            # Check expiration
            if session_obj.expires_at and datetime.utcnow() > session_obj.expires_at:
                db.delete(session_obj)
                db.commit()
                return None
            
            # Update last activity
            session_obj.last_activity = datetime.utcnow()
            db.commit()
            
            return {
                "session_id": session_obj.session_id,
                "total_analyses": session_obj.total_analyses,
                "preferences": session_obj.preferences or {},
                "created_at": session_obj.created_at.isoformat(),
                "last_activity": session_obj.last_activity.isoformat()
            }
    
    def update_session_stats(self, session_id: str, increment_analyses: bool = False):
        """Update session statistics"""
        from ..models.fii_models import UserSession
        
        with SessionLocal() as db:
            session_obj = db.query(UserSession).filter(
                UserSession.session_id == session_id
            ).first()
            
            if session_obj:
                session_obj.last_activity = datetime.utcnow()
                if increment_analyses:
                    session_obj.total_analyses += 1
                db.commit()
    
    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions"""
        from ..models.fii_models import UserSession
        
        with SessionLocal() as db:
            current_time = datetime.utcnow()
            expired_sessions = db.query(UserSession).filter(
                and_(
                    UserSession.expires_at.isnot(None),
                    UserSession.expires_at < current_time
                )
            )
            
            count = expired_sessions.count()
            expired_sessions.delete(synchronize_session=False)
            db.commit()
            
            return count


# Global instances
cache_manager = CacheManager()
session_manager = SessionManager()
