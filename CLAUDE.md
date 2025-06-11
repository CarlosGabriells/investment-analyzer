# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Brazilian Real Estate Investment Trust (FII) PDF analyzer that uses AI to extract and analyze financial data from FII reports. The system consists of a FastAPI backend and Next.js frontend, with AI-powered PDF analysis using Groq and market data integration via brapi.dev.

## Development Commands

### Backend (Python/FastAPI)
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run backend server
cd backend && python main.py

# Initialize database
cd backend && python init_db.py

# Test API configuration
python testar_configuracao.py

# Test with sample PDF
cd teste && ./testar_curl.sh
```

### Frontend (Next.js)
```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Docker
```bash
# Run entire application
docker-compose up

# Build and run in background
docker-compose up -d

# View logs
docker-compose logs -f
```

## Architecture

### Backend Structure
- **FastAPI API** (`backend/api/endpoints.py`): Main REST API with endpoints for PDF analysis, ranking, and similarity search
- **PDF Analysis Engine** (`backend/analysis/pdf_analyzer.py`): Core PDF text extraction and AI analysis using Groq
- **Market Data Integration** (`backend/analysis/market_data.py`): Real-time market data from brapi.dev and yfinance
- **Embeddings System** (`backend/analysis/embeddings.py`): Semantic similarity using sentence transformers
- **Ranking System** (`backend/analysis/ranking.py`): FII ranking by various criteria
- **Database Models** (`backend/models/`): SQLAlchemy models for FII analysis, rankings, and user sessions
- **Caching** (`backend/database/cache_manager.py`): Session and result caching

### Frontend Structure  
- **Next.js 15** with React 19 and TypeScript
- **Tailwind CSS** for styling
- **File upload interface** for PDF analysis
- **Dynamic tables** for displaying analysis results and rankings

### Data Flow
1. PDF upload → Text extraction → AI analysis (Groq)
2. Market data enrichment (brapi.dev/yfinance) 
3. Embedding generation for similarity search
4. Database storage with caching
5. Ranking and comparison features

## Key Configuration

### Required Environment Variables
```bash
# Required APIs
GROQ_API_KEY=your_groq_key_here
BRAPI_API_KEY=your_brapi_key_here

# Optional settings
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
MAX_FILE_SIZE=50
```

### API Integration
- **Groq API**: Essential for AI-powered PDF analysis and data extraction
- **brapi.dev**: Primary source for Brazilian market data (FII quotes, metrics)
- **yfinance**: Fallback for market data when brapi.dev fails

## Database Schema

The system uses SQLAlchemy with these main models:
- **FIIAnalysis**: Stores complete analysis results with embeddings
- **UserSession**: Manages user sessions for analysis persistence  
- **FIIRanking**: Caches ranking results by different criteria

## Testing

Run the configuration test before development:
```bash
python testar_configuracao.py
```

Test with sample FII PDF:
```bash
cd teste && ./testar_curl.sh
```

The system includes comprehensive error handling and fallback mechanisms for API failures.