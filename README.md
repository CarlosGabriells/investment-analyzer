# 📊 FII PDF Analyzer - Sistema de Análise de Relatórios de FIIs

Um sistema completo para análise inteligente de relatórios de Fundos de Investimento Imobiliário (FIIs) utilizando inteligência artificial.

## 📖 Descrição

O **FII PDF Analyzer** é uma aplicação full-stack que permite:

- **Upload de PDFs**: Upload de relatórios de FIIs em formato PDF  
- **Análise com IA**: Extração e análise inteligente dos dados usando Groq AI
- **Métricas Financeiras**: Cálculo automático de indicadores como Dividend Yield, P/VP, etc.
- **Rankings**: Comparação e ranking de FIIs por diferentes critérios
- **Dashboard Web**: Interface moderna para visualização dos resultados
- **Cache Inteligente**: Sistema de cache para otimização de performance

## ⚡ Funcionalidades

### 🧠 Análise Inteligente

- Extração automática de texto de PDFs usando PyPDF2
- Análise estruturada em 14 pontos principais usando IA (Groq)
- Identificação de métricas financeiras chave
- Avaliação de riscos e oportunidades

### 📊 Métricas Calculadas

- **Dividend Yield**: Rendimento dividendo
- **P/VP**: Preço sobre Valor Patrimonial
- **Receitas de Aluguéis**: Receitas operacionais
- **Taxa de Vacância**: Percentual de vacância
- **Alavancagem**: Nível de endividamento
- **Liquidez**: Análise de liquidez das cotas

### 🏆 Sistema de Rankings

- Ranking por Dividend Yield (maior para menor)
- Ranking por P/VP (menor para maior)
- Comparações entre múltiplos FIIs por sessão

### 🎨 Interface Moderna

- Dashboard responsivo com Tailwind CSS
- Tabelas dinâmicas com busca e filtros
- Relatórios IA com animação de digitação
- Tema escuro otimizado

## ⚙️ Instalação

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/investment-analyzer.git
cd investment-analyzer
```

### 2. Configuração do Backend
```bash
# Instalar dependências Python
pip install -r backend/requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações
```

### 3. Configuração do Frontend
```bash
# Navegar para o frontend
cd frontend

# Instalar dependências Node.js
npm install
```

### Obter Chave da API Groq
1. Acesse [console.groq.com](https://console.groq.com)
2. Crie uma conta gratuita
3. Gere uma API Key
4. Adicione no arquivo `.env`

## 🚀 Uso

#### Backend
```bash
# Inicializar banco de dados
cd backend
python init_db.py

# Iniciar servidor de desenvolvimento
python main.py
```

#### Frontend
```bash
# Em outro terminal
cd frontend
npm run dev
```

### Teste Prático
```bash
# Testar com cURL
cd teste
./testar_curl.sh
```

## 📡 API Endpoints

### 📤 Upload e Análise
```http
POST /analyze
Content-Type: multipart/form-data

Form Data:
- pdf_file: arquivo PDF
- session_id: ID da sessão (opcional)
```

### 🏆 Rankings
```http
GET /ranking/dividend_yield?session_id=SESSION_ID
GET /ranking/pvp?session_id=SESSION_ID
```

### 🔍 Consultas
```http
GET /analysis/SESSION_ID
GET /analysis/SESSION_ID/FII_CODE
GET /health
```

### 📚 Documentação Interativa
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗 Arquitetura

```
investment-analyzer/
├── backend/                 # API Python
│   ├── analysis/           # Módulos de análise
│   │   ├── pdf_analyzer.py # Análise de PDFs com IA
│   │   └── simple_ranking.py # Sistema de rankings
│   ├── api/                # Endpoints da API
│   │   └── endpoints.py    # Rotas principais
│   ├── database/           # Camada de dados
│   │   └── simple_cache.py # Cache em memória  
│   ├── models/             # Modelos de dados
│   │   ├── base.py         # Configuração SQLAlchemy
│   │   └── simple_models.py # Modelos de BD
│   ├── config.py           # Configurações
│   ├── main.py             # Entry point
│   └── requirements.txt    # Dependências Python
├── frontend/               # Interface Next.js
│   ├── src/
│   │   ├── app/           # App Router
│   │   ├── components/    # Componentes React
│   │   └── utils/         # Utilitários e tipos
│   └── package.json       # Dependências Node.js
├── teste/                 # Scripts de teste
├── Dockerfile             # Container backend
├── docker-compose.yml     # Orquestração
└── .env.example          # Configurações exemplo
```

## 💾 Banco de Dados

### Estrutura

#### Tabela `fii_analysis`
```sql
- id: PRIMARY KEY
- session_id: Agrupamento por sessão
- fii_code: Código do FII (BRCR11, etc.)
- fii_name: Nome do fundo
- fund_info: JSON com dados básicos
- financial_metrics: JSON com métricas
- detailed_analysis: JSON com análise IA
- pdf_filename: Nome do arquivo original
- created_at: Timestamp de criação
```

#### Tabela `simple_ranking`
```sql
- id: PRIMARY KEY  
- session_id: ID da sessão
- criteria: Critério do ranking
- fii_code: Código do FII
- position: Posição no ranking
- score: Pontuação/valor
- created_at: Timestamp
```