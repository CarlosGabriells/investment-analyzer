#!/bin/bash
# 🧪 TESTE PRÁTICO - Upload via cURL

echo "🧪 TESTE PRÁTICO - Upload de PDF via cURL"
echo "=========================================="

# Verificar se a API está funcionando
echo "🔍 Verificando se a API está funcionando..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API está funcionando!"
else
    echo "❌ API não está funcionando. Execute: docker-compose up"
    exit 1
fi

# Verificar se o arquivo existe
if [ ! -f "relatorio_fii_exemplo.pdf" ]; then
    echo "❌ Arquivo relatorio_fii_exemplo.pdf não encontrado!"
    echo "💡 Execute este script na pasta teste/"
    exit 1
fi

echo ""
echo "📤 Enviando PDF para análise..."
echo "⏳ Aguarde..."

# Fazer o upload
curl -X POST "http://localhost:8000/analyze-pdf" \
     -H "accept: application/json" \
     -F "pdf_file=@relatorio_fii_exemplo.pdf" \
     -F "include_market_comparison=true" \
     -F "include_portfolio=true" \
     -o resultado_curl.json \
     -w "Status HTTP: %{http_code}\nTempo: %{time_total}s\n"

# Verificar resultado
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Upload realizado com sucesso!"
    echo "📄 Resultado salvo em: resultado_curl.json"
    echo ""
    echo "🎯 Preview do resultado:"
    if command -v jq &> /dev/null; then
        # Se jq estiver disponível, formatar JSON
        head -c 500 resultado_curl.json | jq . 2>/dev/null || head -c 500 resultado_curl.json
    else
        # Senão, mostrar texto bruto
        head -c 500 resultado_curl.json
    fi
    echo "..."
    echo ""
    echo "🎉 Teste concluído!"
else
    echo "❌ Erro no upload!"
fi

echo ""
echo "📋 Comandos úteis:"
echo "   Ver resultado completo: cat resultado_curl.json"
echo "   Formatar JSON: cat resultado_curl.json | jq ."
echo "   Testar health: curl http://localhost:8000/health"
