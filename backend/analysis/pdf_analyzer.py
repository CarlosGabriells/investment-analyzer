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
        
        # Remove any markdown formatting
        json_str = re.sub(r'```json\s*', '', json_str)
        json_str = re.sub(r'```\s*$', '', json_str)
        
        # Fix decimal numbers with commas (e.g., 12,3 -> 12.3) but preserve thousands separator in strings
        json_str = re.sub(r'(\d+),(\d{1,2})\b', r'\1.\2', json_str)
        
        # Fix unquoted values that should be strings
        json_str = re.sub(r':\s*N/A\s*([,}])', r': "N/A"\1', json_str)
        json_str = re.sub(r':\s*null\s*([,}])', r': null\1', json_str)
        json_str = re.sub(r':\s*Não informado\s*([,}])', r': "Não informado"\1', json_str)
        json_str = re.sub(r':\s*Não disponível\s*([,}])', r': "Não disponível"\1', json_str)
        
        # Fix string values that start with quotes but are broken
        json_str = re.sub(r':\s*"([^"]*?)$', r': "\1"', json_str, flags=re.MULTILINE)
        
        # Fix broken strings that have extra quotes in the middle
        json_str = re.sub(r':\s*"([^"]*)"([^",}]*)"([^",}]*)"', r': "\1 \2 \3"', json_str)
        
        # Fix newlines inside string values - replace with spaces
        json_str = re.sub(r'("\s*[^"]*?)\n([^"]*?")', r'\1 \2', json_str, flags=re.MULTILINE | re.DOTALL)
        
        # Remove trailing commas before closing braces/brackets
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix missing quotes around keys
        json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        
        # Handle truncated JSON
        json_str = json_str.rstrip()
        
        # If we're in the middle of a string, close it
        if json_str.count('"') % 2 == 1 and not json_str.endswith('"'):
            json_str += '"'
        
        # Count and balance braces
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        if open_braces > close_braces:
            missing_braces = open_braces - close_braces
            json_str += '}' * missing_braces
        
        return json_str
    
    def extract_text(self, pdf_path: str) -> str:
        """Extrai texto do PDF com melhor tratamento de erros"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            if len(reader.pages) == 0:
                return "Erro: PDF não contém páginas válidas"
            
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text() or ""
                    text += f"\n--- PÁGINA {page_num + 1} ---\n{page_text}"
                except Exception as page_error:
                    text += f"\n--- PÁGINA {page_num + 1} (ERRO: {str(page_error)}) ---\n"
                    continue
            
            if len(text.strip()) < 100:
                return "Erro: PDF não contém texto suficiente para análise"
                
            return text
        except Exception as e:
            return f"Erro ao extrair texto do PDF: {str(e)}"
    
    def analyze_with_ai(self, pdf_text: str) -> Dict[str, Any]:
        """Análise completa e detalhada com IA"""
        from config import settings
        
        prompt = f"""
Você é um analista especializado em Fundos de Investimento Imobiliário (FII). Analise este relatório de FII e forneça uma análise DETALHADA E QUALITATIVA.

RELATÓRIO:
{pdf_text[:settings.MAX_PDF_TEXT_LENGTH]}

INSTRUÇÕES ESPECÍFICAS:

1. INFORMAÇÕES BÁSICAS:
   - Ticker: código do fundo terminado em 11 (ex: RECR11, HGLG11, VGRI11)
   - Nome: denominação completa do fundo (sem aspas duplas no meio)
   - CNPJ: número de identificação completo
   - Administrador e Gestor: empresas responsáveis
   - Tipo/Segmento: identifique o tipo específico do FII

2. TIPOS DE FII - identifique qual é baseado no conteúdo:
   - Papel/CRI: investe em certificados de recebíveis imobiliários
   - FIagro: fundos de agronegócios
   - Hotel: hotéis e resorts
   - Lajes Corporativas: escritórios e edifícios comerciais
   - Logística: galpões, centros de distribuição
   - Renda Urbana: imóveis urbanos diversos
   - Residencial: apartamentos, casas
   - Shopping: shopping centers
   - Agrícola: terras e propriedades rurais
   - FOF: fundo de fundos (investe em outros FIIs)
   - Hedge: fundos com estratégias diferenciadas
   - Desenvolvimento: incorporação e desenvolvimento
   - Cemitério: cemitérios e serviços funerários
   - Educação: escolas, universidades
   - Fi-infra: infraestrutura (energia, transporte)
   - Hospital: hospitais e clínicas
   - Outros: se não se encaixar nas categorias acima

3. MÉTRICAS FINANCEIRAS (busque valores exatos no relatório):
   - Receitas de aluguéis: valor em R$ ou em milhares
   - Patrimônio líquido: total do patrimônio
   - Valor patrimonial por cota: valor individual por cota
   - Dividend Yield: % anual ou calcule se tiver distribuição mensal
   - P/VP: CALCULE SEMPRE como preço_mercado ÷ valor_patrimonial (NÃO use 1.0 como default)
   - Taxa de vacância: % de imóveis vazios
   - Número de cotas: quantidade total emitida

4. ANÁLISE DETALHADA - Forneça uma análise profunda incluindo:
   - Qualidade dos ativos e localização
   - Performance financeira e tendências
   - Estratégia de gestão e governança
   - Perfil de inquilinos e contratos
   - Riscos específicos e oportunidades
   - Comparação com benchmarks do setor
   - Perspectivas futuras e recomendações
   - Pontos de atenção para investidores
   - Vantagens competitivas do fundo

5. CÁLCULOS IMPORTANTES:
   - P/VP: procure cotação atual ou preço de mercado da cota e divida pelo valor patrimonial
   - Se não encontrar preço de mercado, deixe P/VP como null
   - Para DY: (rendimento_anual ÷ preço_da_cota) × 100

RESPONDA APENAS JSON VÁLIDO:

{{
  "fund_info": {{
    "ticker": "",
    "nome": "",
    "cnpj": "",
    "administrador": "",
    "gestor": "",
    "tipo": "",
    "segmento": "identifique: Papel/CRI, FIagro, Hotel, Lajes Corporativas, Logística, Renda Urbana, Residencial, Shopping, Agrícola, FOF, Hedge, Desenvolvimento, Cemitério, Educação, Fi-infra, Hospital ou Outros",
    "data_relatorio": ""
  }},
  "financial_metrics": {{
    "receitas_alugueis": 0.0,
    "despesas_operacionais": 0.0,
    "resultado_liquido": 0.0,
    "patrimonio_liquido": 0.0,
    "vp_por_cota": 0.0,
    "dividend_yield": 0.0,
    "p_vp": null,
    "taxa_vacancia": 0.0,
    "numero_cotas": 0,
    "valor_cota": 0.0
  }},
  "detailed_analysis": "FORNEÇA UMA ANÁLISE COMPLETA, DETALHADA E PROFISSIONAL de pelo menos 300 palavras cobrindo: performance financeira, qualidade dos ativos, gestão, riscos, oportunidades, perspectivas e recomendações específicas para este FII. Use linguagem técnica mas acessível."
}}"""
        
        try:
            response = self.groq_client.chat.completions.create(
                model=settings.ANALYSIS_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Mais criativo para análises detalhadas
                max_tokens=6000,  # Aumentado para análises mais completas
                top_p=0.95
            )
        except Exception as api_error:
            return {
                "error": f"Erro na API da Groq: {str(api_error)}",
                "debug_info": {
                    "text_length": len(pdf_text),
                    "text_preview": pdf_text[:500] if pdf_text else "Texto vazio"
                }
            }
        
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
            
            # Try to parse JSON with fallback
            try:
                result = json.loads(json_content)
            except json.JSONDecodeError as json_err:
                # Tentar extrair informações básicas do texto da IA mesmo com JSON inválido
                import re
                
                # Buscar ticker no texto
                ticker_match = re.search(r'\b[A-Z]{4}11\b', content, re.IGNORECASE)
                ticker = ticker_match.group(0) if ticker_match else "Não identificado"
                
                # Buscar nome do fundo
                nome_patterns = [
                    r'nome[:\s]*([^\n]+)',
                    r'fundo[:\s]*([^\n]+)',
                    r'denominação[:\s]*([^\n]+)'
                ]
                nome = "FII - Análise disponível"
                for pattern in nome_patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        nome = match.group(1).strip()[:50]
                        break
                
                # Se falhar, criar estrutura básica e usar o texto como análise
                return {
                    "fund_info": {
                        "ticker": ticker,
                        "nome": nome,
                        "cnpj": "N/A",
                        "administrador": "N/A", 
                        "gestor": "N/A",
                        "tipo": "FII",
                        "data_relatorio": "N/A"
                    },
                    "financial_metrics": {
                        "receitas_alugueis": None,
                        "despesas_operacionais": None,
                        "resultado_liquido": None,
                        "patrimonio_liquido": None,
                        "vp_por_cota": None,
                        "dividend_yield": None,
                        "p_vp": None,
                        "taxa_vacancia": None,
                        "numero_cotas": None,
                        "valor_cota": None
                    },
                    "detailed_analysis": content,
                    "human_readable_analysis": f"**ANÁLISE DO FII {ticker.upper()}**\n\n{content}",
                    "parsing_fallback": True,
                    "original_error": str(json_err)
                }
            
            # Validation for incomplete or invalid responses
            if not isinstance(result, dict):
                raise ValueError("Resposta não é um objeto JSON válido")
            
            # Check if we got minimal data (like just "IFIX")
            fund_info = result.get("fund_info", {})
            ticker = fund_info.get("ticker", "")
            nome = fund_info.get("nome", "")
            
            # If ticker or nome is just "IFIX" or very short, it's likely an error
            if (ticker.upper() == "IFIX" or nome.upper() == "IFIX" or 
                (len(ticker) < 3 and len(nome) < 3)):
                return {
                    "error": "IA não conseguiu extrair informações suficientes do PDF",
                    "raw_response": content,
                    "suggestion": "O PDF pode ter formatação complexa ou texto ilegível. Tente um PDF mais claro.",
                    "debug_info": {
                        "ticker_found": ticker,
                        "nome_found": nome,
                        "pdf_text_length": len(pdf_text),
                        "pdf_preview": pdf_text[:1000] if pdf_text else ""
                    }
                }
            
            # Pós-processamento para corrigir dados inconsistentes
            result = self._post_process_result(result)
            
            # Enriquecer com análise específica do segmento
            from .segment_analyzer import enhance_analysis_with_segment
            result = enhance_analysis_with_segment(result)
            
            # Adicionar análise formatada para humanos
            from .analysis_formatter import format_analysis_to_human, get_analysis_summary
            
            result["human_readable_analysis"] = format_analysis_to_human(result)
            result["summary"] = get_analysis_summary(result)
            
            return result
                
        except Exception as e:
            raw_content = response.choices[0].message.content if response.choices else "No response"
            return {
                "error": f"Erro no parsing da resposta da IA: {str(e)}",
                "raw_response": raw_content,
                "suggestion": "Tente novamente com um PDF diferente ou verifique se o arquivo está íntegro",
                "debug_info": {
                    "content_length": len(raw_content),
                    "starts_with": raw_content[:100] if raw_content else "",
                    "ends_with": raw_content[-100:] if raw_content else "",
                    "cleaned_json": json_content if 'json_content' in locals() else "N/A"
                }
            }
    
    def _post_process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Pós-processamento para corrigir dados inconsistentes"""
        
        # Corrigir fund_info
        fund_info = result.get("fund_info", {})
        
        # Limpar nome truncado com aspas
        nome = fund_info.get("nome", "")
        if nome.startswith('": "') or nome.startswith('"'):
            nome = nome.strip('"').strip(': "').strip()
            fund_info["nome"] = nome
        
        # Corrigir financial_metrics
        financial_metrics = result.get("financial_metrics", {})
        
        # Se valor_cota for 0 mas vp_por_cota existir, usar vp_por_cota
        vp_por_cota = financial_metrics.get("vp_por_cota", 0)
        valor_cota = financial_metrics.get("valor_cota", 0)
        
        if valor_cota == 0 and vp_por_cota > 0:
            financial_metrics["valor_cota"] = vp_por_cota
            valor_cota = vp_por_cota
        
        # Recalcular P/VP se necessário
        p_vp = financial_metrics.get("p_vp", 0)
        
        # Se P/VP é 0 ou 1.0 (default), tentar calcular com dados disponíveis
        if (p_vp == 0 or p_vp == 1.0) and valor_cota > 0 and vp_por_cota > 0:
            calculated_pvp = round(valor_cota / vp_por_cota, 2)
            # Só usar o calculado se for diferente de 1.0 ou se P/VP era 0
            if calculated_pvp != 1.0 or p_vp == 0:
                financial_metrics["p_vp"] = calculated_pvp
        
        # Se ainda não temos P/VP válido, deixar como None
        p_vp_final = financial_metrics.get("p_vp")
        if p_vp_final is not None and isinstance(p_vp_final, (int, float)) and p_vp_final <= 0:
            financial_metrics["p_vp"] = None
            
        # Garantir que valores não sejam negativos ou muito altos (erros de parsing)
        for key in ["receitas_alugueis", "despesas_operacionais", "resultado_liquido", 
                   "patrimonio_liquido", "vp_por_cota", "valor_cota", "numero_cotas"]:
            value = financial_metrics.get(key, 0)
            if value is not None and isinstance(value, (int, float)):
                # Valores muito pequenos para valor_cota ou vp_por_cota são provavelmente erros
                if key in ["valor_cota", "vp_por_cota"] and 0 < value < 1:
                    # Se o valor é muito pequeno, pode estar em centavos - multiplicar por 100
                    if value < 0.5:
                        financial_metrics[key] = value * 100
                # Valores negativos ou muito altos são erros
                elif value < 0 or value > 999999999999:
                    financial_metrics[key] = 0
        
        # Garantir que percentuais estejam em range válido
        for key in ["dividend_yield", "taxa_vacancia"]:
            value = financial_metrics.get(key, 0)
            if value is not None and isinstance(value, (int, float)) and (value < 0 or value > 100):
                financial_metrics[key] = 0
                
        # Garantir que P/VP esteja em range razoável (se não for None)
        p_vp = financial_metrics.get("p_vp")
        if p_vp is not None and isinstance(p_vp, (int, float)) and (p_vp < 0.1 or p_vp > 10):
            financial_metrics["p_vp"] = None  # Se fora do range, marcar como não informado
        
        return result

    def analyze_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Análise completa do PDF com tratamento robusto de erros"""
        
        # Verificar se o arquivo existe
        if not os.path.exists(pdf_path):
            return {"error": "Arquivo PDF não encontrado"}
        
        # Verificar tamanho do arquivo
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            return {"error": "Arquivo PDF está vazio"}
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            return {"error": "Arquivo PDF muito grande (máximo 50MB)"}
        
        # Extrair texto
        text = self.extract_text(pdf_path)
        if text.startswith("Erro:"):
            return {"error": text}
        
        # Verificar se temos texto suficiente
        if len(text.strip()) < 200:
            return {
                "error": "PDF não contém texto suficiente para análise",
                "debug_info": {
                    "text_length": len(text),
                    "text_preview": text[:500] if text else "Vazio"
                }
            }
        
        # Verificar se o texto parece ser de um FII - mais permissivo
        text_lower = text.lower()
        
        # Palavras-chave básicas de FII
        basic_fii_keywords = ["fii", "fundo", "cota", "patrimônio", "receita", "aluguéis", "locação"]
        basic_count = sum(1 for keyword in basic_fii_keywords if keyword in text_lower)
        
        # Códigos de FII (XXXX11)
        import re
        fii_codes_pattern = r'[a-z]{4}11'
        has_fii_code = bool(re.search(fii_codes_pattern, text_lower))
        
        # Administradores conhecidos
        known_admins = ["btg", "xp", "guide", "bnp", "santander", "itau", "bradesco", "inter"]
        has_admin = any(admin in text_lower for admin in known_admins)
        
        # Mais permissivo: aceita se tem pelo menos uma condição
        is_fii_document = (basic_count >= 1) or has_fii_code or has_admin
        
        if not is_fii_document:
            return {
                "error": "PDF não parece ser um relatório de FII válido",
                "suggestion": "Verifique se o arquivo é realmente um relatório de Fundo de Investimento Imobiliário",
                "debug_info": {
                    "basic_keywords_found": basic_count,
                    "has_fii_code": has_fii_code,
                    "has_known_admin": has_admin,
                    "text_preview": text[:1000]
                }
            }
        
        # Proceder com análise
        return self.analyze_with_ai(text)

# Instância global
pdf_analyzer = SimplePDFAnalyzer()