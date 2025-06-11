# Use uma imagem base Python estável e leve
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar arquivos de requirements primeiro (para otimizar cache do Docker)
COPY backend/requirements.txt ./backend/

# Atualizar pip e instalar dependências Python
RUN pip install --upgrade pip && \
    pip install -r backend/requirements.txt

# Copiar o código da aplicação
COPY backend/ ./backend/

# Criar diretório para uploads e dados
RUN mkdir -p /app/uploads /app/data /app/logs

# Copiar arquivo de configuração de exemplo (se existir)
COPY .env.example .env

# Definir o caminho Python
ENV PYTHONPATH=/app

# Expor a porta da aplicação
EXPOSE 8000

# Comando de saúde para verificar se a aplicação está funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão para iniciar a aplicação
CMD ["sh", "-c", "cd /app/backend && python init_db.py && python main.py"]
