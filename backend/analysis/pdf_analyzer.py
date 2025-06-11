"""PDF Analyzer simplificado - apenas o essencial"""

import os
import json
import tempfile
from groq import Groq
from PyPDF2 import PdfReader
from typing import Dict, Any

class SimplePDFAnalyzer:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        self.groq_client = Groq(api_key=api_key)
    
    def _clean_json_response(self, json_str: str) -> str:
        """Clean common JSON formatting issues from AI responses"""
        import re
        
        # Fix decimal numbers with commas (e.g., 12,3 -> 12.3)
        json_str = re.sub(r'(\d+),(\d+)', r'\1.\2', json_str)
        
        # Fix unquoted N/A values
        json_str = re.sub(r':\s*N/A\s*([,}])', r': "N/A"\1', json_str)
        
        # Remove trailing commas before closing braces/brackets
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Handle truncated JSON - if response ends mid-string, try to close it properly
        json_str = json_str.rstrip()
        
        # If truncated mid-string (doesn't end with " or } or ])
        if not json_str.endswith(('"', '}', ']')) and '"' in json_str:
            # Find if we're in the middle of a string value
            last_colon = json_str.rfind(':')
            last_quote = json_str.rfind('"')
            
            if last_colon > last_quote:  # We're after a colon, likely in a string value
                json_str += '"'
        
        # Count and add missing closing braces
        if json_str.count('{') > json_str.count('}'):
            missing_braces = json_str.count('{') - json_str.count('}')
            json_str += '}' * missing_braces
        
        return json_str
    
    def extract_text(self, pdf_path: str) -> str:
        """Extrai texto do PDF"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            return f"Erro: {e}"
    
    def analyze_with_ai(self, pdf_text: str) -> Dict[str, Any]:
        """Análise completa e detalhada com IA"""
        from config import settings
        
        prompt = f"""
        Você é um analista especialista em Fundos de Investimento Imobiliário (FIIs). Analise CUIDADOSAMENTE o relatório abaixo e extraia TODAS as informações solicitadas.

        IMPORTANTE: Use APENAS informações que estão EXPLICITAMENTE no documento. Se uma informação não estiver disponível, declare "N/A" ou "Não informado".

        Texto do relatório:
        {pdf_text[:settings.MAX_PDF_TEXT_LENGTH]}...

        Forneça uma análise ESTRUTURADA e COMPLETA abordando:

        **1. INFORMAÇÕES BÁSICAS DO FUNDO**
        - Ticker/Código do fundo
        - Nome completo
        - CNPJ
        - Administrador
        - Gestor
        - Data do relatório

        **2. ESTRATÉGIA E GESTÃO**
        - Qual é a estratégia/objetivo do fundo?
        - Segmento de atuação (Escritórios, Shoppings, Logística, Educacional, Hospitalar, etc.)
        - Tipo de gestão: Ativa ou Passiva?
        - Qualidade do administrador/gestor

        **3. MÉTRICAS FINANCEIRAS E BENCHMARKS**
        - Dividend Yield atual
        - P/VP atual
        - Receitas de aluguéis
        - Despesas operacionais
        - Resultado líquido
        - Patrimônio líquido
        - Valor patrimonial por cota
        - Comparação com IFIX (está acima/abaixo da média?)

        **4. TAXAS E CUSTOS**
        - Taxa de administração (% ao ano)
        - Taxa de performance (se aplicável)
        - Impacto das taxas no retorno do investidor

        **5. DISTRIBUIÇÃO DE RENDIMENTOS**
        - Padrão de distribuição nos últimos meses (crescente/constante/decrescente)
        - Distribuição está aumentando ano a ano?
        - Resultado por cota vs distribuição por cota
        - Saldo acumulado por cota
        - Saldo está sendo consumido mensalmente? Por quanto tempo duraria?
        - FFO (Funds From Operations) vs Dividend Yield
        - Se FFO < DY: há receitas extraordinárias? Há saldo acumulado suficiente?

        **6. VACÂNCIA E INADIMPLÊNCIA**
        - Vacância financeira (%)
        - Vacância física (%)
        - Taxa de inadimplência (%)
        - Impacto na receita

        **7. ALAVANCAGEM E ESTRUTURA FINANCEIRA**
        - Nível de alavancagem atual
        - Taxa média de alavancagem
        - Plano de amortização de dívidas
        - Capacidade de endividamento

        **8. COMPOSIÇÃO E ALOCAÇÃO DA CARTEIRA**
        - Alocação: % Imóveis, % FIIs, % Caixa
        - Quantidade de imóveis
        - % Contratos típicos vs atípicos
        - Vencimento médio dos contratos
        - % de contratos próximos do vencimento

        **9. CONCENTRAÇÃO E SEGMENTAÇÃO**
        - Segmentos de mercado dos inquilinos
        - % da carteira no maior setor
        - Concentração por inquilino (principal inquilino e %)
        - Situação financeira dos principais inquilinos
        - Inquilinos em período de carência?

        **10. PERFORMANCE E RESULTADOS**
        - Resultado vs período anterior (superior/inferior)
        - Motivos para variação nos resultados
        - Tendência de performance

        **11. LIQUIDEZ E COMUNICADOS**
        - Liquidez das cotas (crescendo/estável/diminuindo)
        - Comunicados importantes (compras, vendas, problemas)

        **12. RISCOS E PONTOS DE ATENÇÃO**
        - Classificação de risco: Baixo/Médio/Alto
        - Principais riscos identificados
        - Pontos de atenção para monitoramento
        - Oportunidades identificadas

        **13. CONCLUSÃO E ANÁLISE FINAL**
        - Avaliação geral do resultado do fundo
        - Pontos positivos e negativos
        - Fundo está "queimando caixa"? Por quê?
        - Sustentabilidade da distribuição (tempo estimado)
        - Justificativa para eventual desconto no preço
        - Expectativa para próximos resultados
        - Tendência: melhora ou piora?

        **14. RECOMENDAÇÃO FINAL**
        - Recomendação: Compra Forte/Compra/Manutenção/Venda/Venda Forte
        - Preço alvo (se possível estimar)
        - Perfil de investidor adequado

        IMPORTANTE: 
        - Responda APENAS com JSON válido, sem texto adicional, sem markdown, sem comentários
        - Use pontos decimais (.) não vírgulas (,) para números: 12.3 não 12,3
        - Para valores não disponíveis use "N/A" entre aspas ou null
        - FORNEÇA ANÁLISES DETALHADAS E COMPLETAS - cada campo detailed_analysis deve ter 3-5 frases explicativas com números específicos e percentuais
        - Para detailed_analysis, cada campo deve ser um parágrafo completo com dados quantitativos
        - Use este formato exato:
        {{
            "fund_info": {{
                "ticker": "",
                "nome": "",
                "cnpj": "",
                "administrador": "",
                "gestor": "",
                "data_relatorio": ""
            }},
            "financial_metrics": {{
                "dividend_yield": 0,
                "p_vp": 0,
                "receitas_alugueis": 0,
                "despesas_operacionais": 0,
                "resultado_liquido": 0,
                "patrimonio_liquido": 0,
                "vp_por_cota": 0,
                "taxa_administracao": 0,
                "taxa_performance": 0
            }},
            "detailed_analysis": {{
                "estrategia_objetivo": "",
                "segmento_gestao": "",
                "performance_financeira": "",
                "distribuicao_analise": "",
                "vacancia_situacao": "",
                "estrutura_endividamento": "",
                "carteira_composicao": "",
                "riscos_principais": "",
                "pontos_positivos": "",
                "pontos_negativos": "",
                "sustentabilidade_fundo": "",
                "recomendacao_final": ""
            }}
        }}
        """
        
        response = self.groq_client.chat.completions.create(
            model=settings.ANALYSIS_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=6000
        )
        
        try:
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response if it contains extra text
            if content.startswith('```json'):
                # Remove markdown code blocks
                content = content.replace('```json', '').replace('```', '').strip()
            elif content.startswith('```'):
                # Remove any code blocks
                content = content.replace('```', '').strip()
            
            # Find JSON object in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_content = content[start_idx:end_idx]
            else:
                json_content = content
            
            # Clean up common JSON issues from AI responses
            json_content = self._clean_json_response(json_content)
            
            return json.loads(json_content)
                
        except Exception as e:
            raw_content = response.choices[0].message.content if response.choices else "No response"
            return {
                "error": f"Erro no parsing da resposta da IA: {str(e)}",
                "raw_response": raw_content,
                "debug_info": {
                    "content_length": len(raw_content),
                    "starts_with": raw_content[:100] if raw_content else "",
                    "ends_with": raw_content[-100:] if raw_content else ""
                }
            }
    
    def analyze_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Análise completa do PDF"""
        text = self.extract_text(pdf_path)
        if text.startswith("Erro:"):
            return {"error": text}
        
        return self.analyze_with_ai(text)

# Instância global
pdf_analyzer = SimplePDFAnalyzer()