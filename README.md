# 🏢 FII PDF Analyzer - Sistema de Análise de Fundos Imobiliários

Sistema inteligente para análise automática de relatórios de Fundos de Investimento Imobiliário (FIIs) usando IA e dados de mercado em tempo real.

## 🎯 O que faz este sistema?

- **📄 Extrai dados de PDFs**: Informações do fundo, métricas financeiras e composição da carteira
- **🤖 Análise com IA**: Usa Groq AI para interpretação inteligente dos documentos
- **📊 Dados de mercado**: Integra cotações e comparações em tempo real via brapi.dev e yfinance
- **💡 Análise completa**: Gera recomendações de investimento baseadas em dados fundamentais


## 🚀 Quick Start

### 1. Clone e Configure
```bash
git clone <repository>
cd investment-analyzer
cp .env.example .env
# Edite o .env com suas API keys
```

### 2. Instale Dependências
```bash
pip install -r requirements.txt
```

### 3. Configure APIs
```bash
# Edite o arquivo .env
GROQ_API_KEY=sua_chave_groq_aqui
BRAPI_API_KEY=sua_chave_brapi_aqui
```

### 4. Teste a Configuração
```bash
python testar_configuracao.py
```

### 5. Execute o Sistema
```bash
# Opção 1: Docker (recomendado)
docker-compose up

# Opção 2: Local
cd backend
python main.py
```

### 6. Teste com PDF
```bash
cd teste
./testar_curl.sh
```

## 🔧 APIs Necessárias

| API | Status | Função | Como Obter |
|-----|--------|--------|------------|
| 🤖 **Groq** | Obrigatória | IA para análise | [console.groq.com](https://console.groq.com/) |
| 📊 **brapi.dev** | Recomendada | Dados de mercado | [brapi.dev/dashboard](https://brapi.dev/dashboard) |

📖 **Guia completo**: [CONFIGURACAO_APIS.md](CONFIGURACAO_APIS.md)

## 📊 Exemplo de Resposta

```json
{
  "fund_info": {
    "ticker": "BRCR11",
    "nome": "FII BTG Pactual Corporate Office Fund",
    "tipo": "Tijolo",
    "administrador": "BTG Pactual"
  },
  "financial_metrics": {
    "receitas_alugueis": 16.5,
    "despesas_operacionais": 2.3,  // ✅ Agora funciona!
    "dividend_yield": 12.3,
    "p_vp": 43.86
  },
  "market_data": {  // ✅ Agora funciona com brapi.dev!
    "current_price": 43.86,
    "change_percent": 1.2,
    "source": "brapi.dev"
  },
  "investment_analysis": "Análise completa com IA...",
  "portfolio_composition": {
    "principais_imoveis": ["Diamond Tower", "Eldorado"],
    "percentual_ocupacao": 95.5
  }
}
```

## 🏗️ Arquitetura do Sistema

```
📱 Frontend (Next.js)
    ↓
🔗 API Gateway (FastAPI)
    ↓
📄 PDF Analyzer (PyPDF2 + OCR)
    ↓
🤖 IA Analysis (Groq)
    ↓
📊 Market Data (brapi.dev + yfinance)
    ↓
📈 Enhanced Analysis
```

## 📁 Estrutura do Projeto

```
investment-analyzer/
├── 📄 backend/           # API Python (FastAPI)
│   ├── main.py          # Ponto de entrada
│   ├── api.py           # Endpoints da API
│   ├── pdf_analyzer.py  # Core da análise
│   ├── market_data.py   # Dados de mercado
│   └── config.py        # Configurações
├── 🎨 frontend/         # Interface (Next.js)
├── 🧪 teste/           # Scripts de teste
├── 🐳 docker-compose.yml # Deploy com Docker
└── 📚 docs/            # Documentação
```

## 🧪 Testes

### Teste Rápido
```bash
python testar_configuracao.py
```

### Teste Completo
```bash
cd teste
./testar_curl.sh
```

### Teste das APIs
```bash
# Teste Groq
curl -X POST "http://localhost:8000/health"

# Teste brapi.dev
curl "https://brapi.dev/api/quote/PETR4?token=SUA_CHAVE"
```

## 🎯 Próximas Melhorias

- [ ] Cache local para reduzir calls às APIs
- [ ] Interface web completa
- [ ] Suporte a múltiplos PDFs
- [ ] Análise comparativa entre FIIs
- [ ] Dashboard de acompanhamento
- [ ] Integração com mais fontes de dados

## 📞 Suporte

1. **Problemas de configuração**: Consulte [CONFIGURACAO_APIS.md](CONFIGURACAO_APIS.md)
2. **Teste de diagnóstico**: Execute `python testar_configuracao.py`
3. **Logs detalhados**: Verifique `fii_analyzer.log`
4. **Issues**: Abra uma issue no repositório

## 📄 Licença

MIT License - veja LICENSE para detalhes.

---

**💡 Dica**: Execute `python testar_configuracao.py` antes de usar para verificar se tudo está funcionando!
