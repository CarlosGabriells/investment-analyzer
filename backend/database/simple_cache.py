"""Cache simples em memória"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class SimpleCache:
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def set(self, key: str, value: Any, ttl_hours: int = 24):
        """Armazena valor no cache"""
        self._cache[key] = value
        self._expiry[key] = datetime.now() + timedelta(hours=ttl_hours)
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache"""
        if key not in self._cache:
            return None
        
        if datetime.now() > self._expiry[key]:
            del self._cache[key]
            del self._expiry[key]
            return None
        
        return self._cache[key]
    
    def clear_session(self, session_id: str):
        """Limpa cache de uma sessão"""
        keys_to_remove = [k for k in self._cache.keys() if k.startswith(f"session_{session_id}")]
        for key in keys_to_remove:
            del self._cache[key]
            del self._expiry[key]

# Instância global
simple_cache = SimpleCache()