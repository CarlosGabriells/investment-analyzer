#!/usr/bin/env python3
"""
Arquivo principal para execução da API de análise de PDFs de FIIs
"""

import sys
import os
import logging
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from config import settings
    from api.endpoints import app
    import uvicorn
except ImportError as e:
    print(f"❌ Erro ao importar dependências: {e}")
    print("💡 Execute: pip install -r requirements.txt")
    sys.exit(1)

def setup_logging():
    """Configura o logging da aplicação"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('fii_analyzer.log')
        ]
    )

def check_environment():
    """Verifica configurações do ambiente"""
    print("�� Verificando configurações...")
    
    validation = settings.validate_settings()
    
    if validation["valid"]:
        print("✅ Configurações válidas!")
        print(f"📊 Configurações: {validation['settings']}")
    else:
        print("❌ Problemas encontrados:")
        for issue in validation["issues"]:
            print(f"   - {issue}")
        print("\n📖 Exemplo de arquivo .env:")
        print("GROQ_API_KEY=sua_chave_aqui")
        print("API_PORT=8000")
        print("LOG_LEVEL=INFO")
        return False
    
    return True

def main():
    """Função principal"""
    print("🏢 FII PDF Analyzer - Sistema de Análise de Relatórios")
    print("=" * 50)
    
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Verificar ambiente
    if not check_environment():
        sys.exit(1)
    
    # Mostrar informações de inicialização
    print(f"\n🚀 Iniciando servidor...")
    print(f"📡 Host: {settings.API_HOST}")
    print(f"🔌 Porta: {settings.API_PORT}")
    print(f"🔄 Reload: {settings.API_RELOAD}")
    print(f"📁 Tamanho máximo de arquivo: {settings.MAX_FILE_SIZE // (1024*1024)}MB")
    print(f"\n📚 Documentação disponível em:")
    print(f"   - http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"   - http://{settings.API_HOST}:{settings.API_PORT}/redoc")
    print("\n" + "=" * 50)
    
    try:
        # Iniciar servidor
        uvicorn.run(
            "api.endpoints:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=settings.API_RELOAD,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
