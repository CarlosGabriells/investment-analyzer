# 🔧 Configuração das APIs

Este documento explica como configurar corretamente as APIs necessárias para o funcionamento completo do sistema.

## 📋 APIs Necessárias

### 1. 🤖 Groq API (OBRIGATÓRIA)
**Função**: IA para análise e extração de dados dos PDFs

**Como obter**:
1. Acesse [https://console.groq.com/](https://console.groq.com/)
2. Crie uma conta gratuita
3. Gere uma API key
4. Adicione no arquivo `.env`: `GROQ_API_KEY=sua_chave_aqui`

**Observações**:
- Gratuita com limitações de uso
- Essencial para extração de dados dos PDFs
- Sem ela, o sistema funcionará de forma muito limitada

### 2. 📊 brapi.dev API (RECOMENDADA)
**Função**: Dados de mercado em tempo real para FIIs brasileiros

**Como obter**:
1. Acesse [https://brapi.dev/dashboard](https://brapi.dev/dashboard)
2. Crie uma conta
3. Obtenha seu token de autenticação
4. Adicione no arquivo `.env`: `BRAPI_API_KEY=sua_chave_aqui`

**Observações**:
- Gratuita com limitações (500 requests/mês)
- Planos pagos disponíveis para uso intensivo
- Sem ela, dados de mercado não funcionarão

## ⚙️ Configuração do Arquivo .env

Crie um arquivo `.env` na raiz do projeto com:

```bash
# APIs Obrigatórias
GROQ_API_KEY=sua_chave_groq_aqui
BRAPI_API_KEY=sua_chave_brapi_aqui

# Configurações opcionais
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
MAX_FILE_SIZE=50
```

## 🔍 Como Verificar se as APIs Estão Funcionando

### Teste 1: Verificar configuração
```bash
cd backend
python -c "from config import settings; print('Groq:', bool(settings.GROQ_API_KEY)); print('brapi:', bool(settings.BRAPI_API_KEY))"
```

### Teste 2: Teste completo
```bash
cd teste
chmod +x testar_curl.sh
./testar_curl.sh
```

## 🚨 Problemas Comuns e Soluções

### Erro: "429 Too Many Requests"
**Causa**: Limite de requisições atingido
**Solução**: 
- Aguardar reset do limite (geralmente 24h)
- Considerar upgrade para plano pago
- Implementar cache local (futuro)

### Erro: "401 Unauthorized"
**Causa**: API key inválida ou não configurada
**Solução**:
- Verificar se a chave está correta no arquivo `.env`
- Regenerar a chave no dashboard da API
- Verificar se não há espaços extras na chave

### "despesas_operacionais: null"
**Causa**: IA não conseguiu extrair essa informação específica
**Soluções**:
- Verificar se o PDF contém essa informação
- Tentar com PDF mais legível (não escaneado)
- Melhorar qualidade do PDF de entrada

### Dados de mercado não funcionam
**Causa**: Problemas com APIs externas ou autenticação
**Solução**:
- Verificar BRAPI_API_KEY no arquivo `.env`
- Testar conectividade: `curl "https://brapi.dev/api/quote/PETR4?token=SUA_CHAVE"`
- Verificar logs da aplicação para detalhes do erro

## 📊 Limites das APIs Gratuitas

| API | Limite Gratuito | Observações |
|-----|----------------|-------------|
| Groq | ~15 req/min | Muito adequado para uso individual |
| brapi.dev | 500 req/mês | Suficiente para testes e uso leve |

## 🔄 Fallbacks Implementados

O sistema possui fallbacks automáticos:

1. **brapi.dev falha** → yfinance (sem autenticação)
2. **Ambas falham** → análise apenas com dados do PDF
3. **Groq falha** → extração básica sem IA

## 💡 Dicas de Otimização

1. **Cache local**: Implemente cache para reduzir calls às APIs
2. **Rate limiting**: Implemente delays entre requisições
3. **Batch processing**: Processe múltiplos PDFs em lotes
4. **Horários de menor uso**: APIs têm menos tráfego durante madrugada


