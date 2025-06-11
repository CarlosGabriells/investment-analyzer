#!/usr/bin/env python3
"""
Script para inicializar o banco de dados do sistema de análise de FIIs
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório backend ao Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from backend.models.base import init_db, engine
from backend.models.fii_models import Base
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Inicializar banco de dados"""
    try:
        logger.info("Iniciando criação das tabelas do banco de dados...")
        
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Banco de dados inicializado com sucesso!")
        logger.info("Tabelas criadas:")
        logger.info("  - fii_analyses: Para armazenar análises de PDFs")
        logger.info("  - fii_rankings: Para armazenar rankings de FIIs")
        logger.info("  - user_sessions: Para gerenciar sessões de usuários")
        logger.info("  - cache_entries: Para cache de dados")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
