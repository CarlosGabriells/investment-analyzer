#!/usr/bin/env python3
"""
Script para testar configurações das APIs
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Adicionar backend ao path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_groq_api():
    """Testa a configuração da API Groq"""
    print("🤖 Testando Groq API...")
    
    try:
        from config import settings
        
        if not settings.GROQ_API_KEY:
            print("❌ GROQ_API_KEY não configurada")
            return False
        
        if settings.GROQ_API_KEY in ["sua_chave_groq_aqui", "gsk-placeholder-key-change-this"]:
            print("❌ GROQ_API_KEY contém valor placeholder")
            return False
        
        # Teste básico de inicialização
        from groq import Groq
        client = Groq(api_key=settings.GROQ_API_KEY)
        print("✅ Groq API configurada corretamente")
        return True
        
    except ImportError:
        print("❌ Biblioteca groq não instalada")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar Groq: {e}")
        return False

def test_brapi_api():
    """Testa a configuração da API brapi.dev"""
    print("📊 Testando brapi.dev API...")
    
    try:
        from config import settings
        import requests
        
        if not settings.BRAPI_API_KEY:
            print("⚠️  BRAPI_API_KEY não configurada - dados de mercado limitados")
            return False
        
        # Teste real da API
        url = "https://brapi.dev/api/quote/PETR4"
        headers = {'Authorization': f'Bearer {settings.BRAPI_API_KEY}'}
        params = {'token': settings.BRAPI_API_KEY}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and data['results']:
                print("✅ brapi.dev API funcionando corretamente")
                return True
            else:
                print("❌ brapi.dev retornou dados vazios")
                return False
        elif response.status_code == 401:
            print("❌ brapi.dev: Token inválido ou expirado")
            return False
        elif response.status_code == 402:
            print("❌ brapi.dev: Limite de requisições atingido")
            return False
        else:
            print(f"❌ brapi.dev: Erro HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar brapi.dev: {e}")
        return False

async def test_market_data():
    """Testa o sistema de dados de mercado"""
    print("📈 Testando sistema de dados de mercado...")
    
    try:
        from market_data import MarketDataProvider
        
        provider = MarketDataProvider()
        result = await provider.get_fii_data("HGLG11")
        
        if "error" in result:
            print(f"⚠️  Dados de mercado com limitações: {result['error']}")
            return False
        else:
            print("✅ Sistema de dados de mercado funcionando")
            return True
            
    except Exception as e:
        print(f"❌ Erro no sistema de dados de mercado: {e}")
        return False

def test_pdf_analyzer():
    """Testa o analisador de PDF"""
    print("📄 Testando analisador de PDF...")
    
    try:
        from pdf_analyzer import PDFAnalyzer
        
        analyzer = PDFAnalyzer()
        print("✅ PDFAnalyzer inicializado corretamente")
        return True
        
    except Exception as e:
        print(f"❌ Erro no PDFAnalyzer: {e}")
        return False

async def main():
    """Função principal de teste"""
    print("🧪 TESTE DE CONFIGURAÇÃO DO SISTEMA")
    print("=" * 50)
    
    tests = [
        ("Configuração Groq", test_groq_api),
        ("Configuração brapi.dev", test_brapi_api),
        ("Analisador PDF", test_pdf_analyzer),
    ]
    
    results = []
    
    # Testes síncronos
    for name, test_func in tests:
        print(f"\n{name}:")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            results.append((name, False))
    
    # Teste assíncrono
    print(f"\nSistema de Dados de Mercado:")
    try:
        market_result = await test_market_data()
        results.append(("Dados de Mercado", market_result))
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        results.append(("Dados de Mercado", False))
    
    # Resumo
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES:")
    
    success_count = 0
    for name, success in results:
        status = "✅ OK" if success else "❌ ERRO"
        print(f"  {status} {name}")
        if success:
            success_count += 1
    
    print(f"\n🎯 Resultado: {success_count}/{len(results)} testes passaram")
    
    if success_count == len(results):
        print("🎉 Sistema totalmente configurado!")
    elif success_count >= len(results) - 1:
        print("⚠️  Sistema quase pronto - verifique configurações opcionais")
    else:
        print("🚨 Sistema precisa de configuração - consulte CONFIGURACAO_APIS.md")
    
    print("\n💡 Dicas:")
    print("  - Para resolver problemas, consulte: CONFIGURACAO_APIS.md")
    print("  - Logs detalhados estão em: fii_analyzer.log")
    print("  - Teste a API completa com: cd teste && ./testar_curl.sh")

if __name__ == "__main__":
    # Configurar logging básico
    logging.basicConfig(level=logging.WARNING)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        sys.exit(1)
