"""
Configurações da aplicação
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configurações da aplicação"""
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Configurações da API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_RELOAD: bool = os.getenv("API_RELOAD", "True").lower() == "true"
    
    # Configurações de Banco de Dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fii_analyzer.db")
    
    # Configurações de upload
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50")) * 1024 * 1024  # 50MB default
    ALLOWED_EXTENSIONS: list = [".pdf"]
    
    # Configurações de análise com IA
    ANALYSIS_MODEL: str = os.getenv("ANALYSIS_MODEL", "llama3-70b-8192")
    MAX_PDF_TEXT_LENGTH: int = int(os.getenv("MAX_PDF_TEXT_LENGTH", "25000"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate_settings(cls) -> Dict[str, Any]:
        """Valida configurações essenciais"""
        issues = []
        
        if not cls.GROQ_API_KEY:
            issues.append("GROQ_API_KEY não configurada")
        
        if cls.MAX_FILE_SIZE > 100 * 1024 * 1024:  # 100MB
            issues.append("MAX_FILE_SIZE muito grande (máximo 100MB)")
            
        if not os.path.exists(os.path.dirname(cls.DATABASE_URL.replace("sqlite:///", ""))):
            if "sqlite:///" in cls.DATABASE_URL:
                try:
                    os.makedirs(os.path.dirname(cls.DATABASE_URL.replace("sqlite:///", "")), exist_ok=True)
                except:
                    issues.append("Não foi possível criar diretório para banco de dados")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "settings": {
                "api_host": cls.API_HOST,
                "api_port": cls.API_PORT,
                "max_file_size_mb": cls.MAX_FILE_SIZE // (1024 * 1024),
                "analysis_model": cls.ANALYSIS_MODEL,
                "database_url": cls.DATABASE_URL,
                "log_level": cls.LOG_LEVEL
            }
        }

# Instância global das configurações
settings = Settings()

# Validar na importação
validation = settings.validate_settings()
if not validation["valid"]:
    print("⚠️  Problemas de configuração encontrados:")
    for issue in validation["issues"]:
        print(f"   - {issue}")
    print("📖 Consulte o README para configuração adequada")
