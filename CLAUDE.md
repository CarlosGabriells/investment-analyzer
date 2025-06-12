# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (Python/FastAPI)
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run development server
cd backend
python main.py

# Test configuration
python testar_configuracao.py

# Test API with curl
cd teste
./testar_curl.sh
```

### Frontend (Next.js)
```bash
# Install dependencies
cd frontend
npm install

# Development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

### Full Stack
```bash
# Run with Docker
docker-compose up

# API health check
curl http://localhost:8000/health
```

## Architecture Overview

This is a **FII (Real Estate Investment Fund) PDF Analyzer** with three main components:

### 1. Backend API (FastAPI)
- **Entry Point**: `backend/main.py` - Starts uvicorn server with environment validation
- **API Endpoints**: `backend/api/endpoints.py` - Simple REST API with CORS
- **Core Analysis**: `backend/analysis/pdf_analyzer.py` - PDF text extraction + Groq AI analysis
- **Database**: SQLite with SQLAlchemy models for caching analysis results
- **Cache System**: In-memory cache (`backend/database/simple_cache.py`) for performance

### 2. Frontend (Next.js)
- **Main Page**: `frontend/src/app/page.tsx` - Dashboard with ranking table
- **Components**: Reusable UI components for tables, buttons, file uploads
- **Styling**: Tailwind CSS with custom dark theme

### 3. Analysis Pipeline
```
PDF Upload → Text Extraction (PyPDF2) → AI Analysis (Groq) → Database Storage → Frontend Display
```

## Key API Endpoints

- `POST /analyze` - Upload PDF and get analysis with session-based caching
- `GET /ranking/{criteria}` - Get rankings by dividend_yield or pvp
- `GET /analysis/{session_id}` - List all analyses for a session
- `GET /health` - Health check

## Environment Configuration

Required environment variables (check `.env.example`):
- `GROQ_API_KEY` - Required for AI analysis
- `API_HOST` / `API_PORT` - Server configuration (default: 0.0.0.0:8000)
- `DATABASE_URL` - SQLite database path
- `MAX_FILE_SIZE` - PDF upload limit in bytes

## Data Models

The system uses two main database models:
- `FIIAnalysis` - Stores complete PDF analysis results with session-based grouping
- `SimpleRanking` - Stores ranking calculations by different criteria

Analysis results are structured with:
- `fund_info` - Basic fund information (ticker, name, CNPJ, etc.)
- `financial_metrics` - Financial data (dividend yield, P/VP, revenues, etc.)
- `detailed_analysis` - AI-generated comprehensive analysis

## Testing & Validation

- Use `python testar_configuracao.py` to validate API keys and environment
- Use `cd teste && ./testar_curl.sh` to test complete upload workflow
- Check `fii_analyzer.log` for detailed application logs

## Session Management

The system uses session IDs to group multiple PDF analyses together, enabling:
- Cached results for repeat requests
- Comparative rankings across multiple funds
- Organized data retrieval by session