"""
Sistema simplificado para análise de PDFs de relatórios de FIIs com IA
Baseado no Context7 para análise inteligente de documentos
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import tempfile
import json
import asyncio

from groq import Groq
from PyPDF2 import PdfReader
import pandas as pd
from dotenv import load_dotenv

# Importações para OCR
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# Importar configurações
from backend.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Importar market_data apenas quando necessário para evitar dependências circulares
try:
    from backend.analysis.market_data import enhanced_market_provider as market_provider
except ImportError as e:
    logger.warning(f"Não foi possível importar market_data: {e}. Funcionalidade de dados de mercado será limitada.")
    market_provider = None

class PDFAnalyzer:
    """Analisador de PDFs de relatórios de FIIs com IA"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key or api_key == "sua_chave_groq_aqui" or api_key == "gsk-placeholder-key-change-this":
            logger.warning("GROQ_API_KEY não configurada corretamente. Funcionalidade de IA será limitada.")
            self.groq_client = None
        else:
            try:
                self.groq_client = Groq(api_key=api_key)
                logger.info("Cliente Groq inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar cliente Groq: {e}")
                self.groq_client = None
    
    def extract_text_from_pdf(self, pdf_file_path: str) -> str:
        """
        Extrai texto de um PDF. Tenta extração direta e, se falhar, tenta OCR.
        Recebe o caminho para o arquivo PDF temporário.
        """
        text = ""
        
        # 1. Tentar extração direta com PyPDF2
        try:
            reader = PdfReader(pdf_file_path)
            for page in reader.pages:
                text += page.extract_text() or ""
            
            if text.strip(): # Se algum texto foi extraído
                logger.info(f"Texto extraído diretamente (PyPDF2): {len(text)} caracteres")
                return text
            else:
                logger.warning("PyPDF2 não extraiu texto. Tentando OCR...")
        except Exception as e:
            logger.warning(f"Erro na extração PyPDF2: {e}. Tentando OCR...")

        # 2. Tentar OCR com pdf2image e pytesseract
        try:
            images = convert_from_path(pdf_file_path)
            ocr_text = ""
            for i, image in enumerate(images):
                try:
                    page_text = pytesseract.image_to_string(image, lang='por') # 'por' para português
                    ocr_text += page_text
                    logger.debug(f"OCR da página {i+1} concluído.")
                except Exception as e:
                    logger.error(f"Erro no OCR da página {i+1}: {e}")
                    continue # Tentar próxima página mesmo se uma falhar
            
            if ocr_text.strip():
                logger.info(f"Texto extraído via OCR: {len(ocr_text)} caracteres")
                return ocr_text
            else:
                logger.error("OCR também não extraiu texto significativo.")
                return "Erro: Nenhum texto pôde ser extraído do PDF. Verifique se o arquivo é válido e contém conteúdo legível."
            
        except Exception as e:
            logger.error(f"Erro geral na extração de texto (PyPDF2 ou OCR): {e}")
            return f"Erro: Falha ao processar o PDF para extração de texto: {e}"

    def _call_groq_api(self, prompt: str, model: str, temperature: float, max_tokens: int) -> Optional[str]:
        """Função auxiliar para chamar a API Groq com tratamento de erros."""
        if not self.groq_client:
            logger.warning("Cliente Groq não disponível. Não é possível chamar a API.")
            return None
        try:
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            result = response.choices[0].message.content.strip()
            
            # Melhor limpeza de blocos de código markdown
            result = self._clean_json_response(result)
            
            return result.strip()
        except Exception as e:
            logger.error(f"Erro ao chamar a API Groq: {e}")
            return None
    
    def _clean_json_response(self, response: str) -> str:
        """Limpa resposta da IA removendo markdown e texto extra."""
        import re
        
        # Remover blocos de código markdown primeiro
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*$', '', response, flags=re.MULTILINE)
        response = re.sub(r'```.*?```', '', response, flags=re.DOTALL)
        
        # Procurar JSON válido
        json_match = re.search(r'(\{.*?\})', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            
            # Corrigir formatação de números brasileiros (26.638.202 -> 26638202)
            # Preservar decimais (16.5 permanece 16.5)
            json_str = re.sub(r'(\d+)\.(\d{3})\.(\d{3})', r'\1\2\3', json_str)  # xxx.xxx.xxx
            json_str = re.sub(r'(\d+)\.(\d{3})(?![\d.])', r'\1\2', json_str)    # xxx.xxx (não seguido por dígito ou ponto)
            
            return json_str
        
        # Se não encontrou JSON válido, retornar a resposta original
        return response

    def identify_fund_info(self, pdf_text: str) -> Dict[str, Any]:
        """Identifica informações básicas do fundo no PDF"""
        if not self.groq_client or not pdf_text.strip():
            logger.warning("Cliente Groq não disponível ou texto do PDF vazio. Retornando dados básicos 'N/A'.")
            return {
                "ticker": "N/A", "nome": "N/A", "cnpj": "N/A", 
                "administrador": "N/A", "gestor": "N/A", "tipo": "N/A", 
                "data_relatorio": "N/A"
            }
        
        # Limitar o texto enviado para a IA para evitar estouro de tokens
        truncated_pdf_text = pdf_text[:settings.MAX_PDF_TEXT_LENGTH]

        prompt = f"""
        Analise o seguinte texto extraído de um relatório de FII e extraia as seguintes informações:
        
        1. Ticker/Código do fundo (formato XXXX11)
        2. Nome completo do fundo
        3. CNPJ do fundo
        4. Administrador
        5. Gestor
        6. Tipo de fundo (Tijolo, Papel, Híbrido, Fundos de Fundos)
        7. Data do relatório
        
        Texto do PDF:
        {truncated_pdf_text}...
        
        IMPORTANTE: Responda APENAS com JSON válido, sem texto adicional, sem blocos de código markdown.
        Se uma informação não for encontrada, use "N/A".
        {{
            "ticker": "string",
            "nome": "string", 
            "cnpj": "string",
            "administrador": "string",
            "gestor": "string",
            "tipo": "string",
            "data_relatorio": "string"
        }}
        """
        
        result_str = self._call_groq_api(prompt, settings.DEFAULT_ANALYSIS_MODEL, settings.TEMPERATURE, 500)
        
        if result_str:
            try:
                parsed_json = json.loads(result_str)
                logger.info(f"Informações do fundo extraídas com sucesso: {parsed_json.get('ticker', 'N/A')}")
                return parsed_json
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao parsear JSON da IA para informações do fundo: {e}")
                logger.error(f"Resposta bruta da IA: '{result_str[:500]}...'")
        
        return {
            "ticker": "N/A", "nome": "N/A", "cnpj": "N/A", 
            "administrador": "N/A", "gestor": "N/A", "tipo": "N/A", 
            "data_relatorio": "N/A"
        }
    
    def extract_financial_metrics(self, pdf_text: str) -> Dict[str, Any]:
        """Extrai métricas financeiras do relatório com melhor precisão"""
        if not self.groq_client or not pdf_text.strip():
            logger.warning("Cliente Groq não disponível ou texto do PDF vazio. Retornando dados vazios.")
            return {}
        
        truncated_pdf_text = pdf_text[:settings.MAX_PDF_TEXT_LENGTH]

        prompt = f"""
        Você é um especialista em análise de relatórios de FIIs. Analise CUIDADOSAMENTE o texto e extraia APENAS os valores que estão EXPLICITAMENTE mencionados no documento.

        REGRAS CRÍTICAS:
        1. Use NULL apenas se o valor NÃO EXISTIR no documento
        2. NÃO calcule, estime ou invente valores
        3. Procure por variações de nomes (ex: "Receita com Locação", "Receita de Aluguéis", "Receitas de Locação")
        4. Valores em milhares devem ser convertidos (ex: 1.234 mil = 1234000)
        5. Percentuais devem estar em formato decimal (ex: 12.5% = 12.5)

        SEÇÕES A PROCURAR:
        - DRE (Demonstração do Resultado)
        - Balanço Patrimonial  
        - Demonstração dos Fluxos de Caixa
        - Informações sobre Cotas
        - Indicadores de Desempenho
        - Dados de Mercado

        MÉTRICAS FINANCEIRAS:
        1. Receitas de aluguéis/locação (valores mensais ou anuais)
        2. Despesas operacionais totais
        3. Resultado líquido do período
        4. Patrimônio líquido total 
        5. Valor patrimonial por cota (R$/cota)
        6. Dividend yield anual (%)
        7. P/VP (Price-to-Book ratio)
        8. Número total de cotas emitidas
        9. Valor/preço da cota no período
        
        MÉTRICAS AVANÇADAS:
        10. FFO (Funds From Operations)
        11. Taxa de administração (% ao ano)
        12. Taxa de performance (% ao ano)
        13. Vacância física (%)
        14. Vacância financeira (%)
        15. Taxa de inadimplência (%)
        16. Alavancagem (Dívida/Patrimônio em %)
        17. Distribuição mensal por cota (R$/cota)

        Texto do relatório:
        {truncated_pdf_text}...
        
        RESPONDA APENAS COM JSON VÁLIDO. Exemplo de estrutura:
        {{
            "receitas_alugueis": 1500000,
            "despesas_operacionais": 200000,
            "resultado_liquido": 800000, 
            "patrimonio_liquido": 50000000,
            "vp_por_cota": 85.50,
            "dividend_yield": 10.5,
            "p_vp": 0.95,
            "numero_cotas": 1000000,
            "valor_cota": 81.25,
            "ffo": 900000,
            "taxa_administracao": 0.75,
            "taxa_performance": null,
            "vacancia_fisica": 8.5,
            "vacancia_financeira": 6.2,
            "inadimplencia": 2.1,
            "alavancagem": 35.8,
            "distribuicao_cota": 0.65
        }}
        """
        
        result_str = self._call_groq_api(prompt, settings.DEFAULT_ANALYSIS_MODEL, settings.TEMPERATURE, 1200)
        
        if result_str:
            try:
                # Verificar se a resposta não está vazia
                if not result_str.strip():
                    logger.warning("IA retornou resposta vazia para métricas financeiras")
                    return {}
                
                parsed_json = json.loads(result_str)
                
                # Validar e limpar os dados
                cleaned_metrics = self._validate_and_clean_metrics(parsed_json)
                
                logger.info(f"Métricas financeiras extraídas e validadas: {len(cleaned_metrics)} campos")
                return cleaned_metrics
                
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao parsear JSON da IA para métricas financeiras: {e}")
                logger.error(f"Resposta bruta da IA: '{result_str[:500]}...'")
                # Tentar extrair manualmente do texto se o JSON falhar
                return self._extract_metrics_fallback(result_str)
        return {}
    
    def generate_investment_analysis(self, fund_info: Dict, metrics: Dict, pdf_text: str) -> str:
        """Gera análise completa de investimento (versão básica, sem dados de mercado externos)"""
        if not self.groq_client:
            return """
            **ANÁLISE LIMITADA - Cliente de IA não disponível**
            
            Para uma análise completa, configure a GROQ_API_KEY no arquivo .env
            
            **Dados Extraídos:**
            - Informações do Fundo: Disponíveis
            - Métricas Financeiras: Limitadas
            - Texto do PDF: Extraído com sucesso
            
            **Recomendação:** Configure a API key do Groq para análise completa com IA.
            """
        
        # Verificar se há dados suficientes para uma análise significativa
        if not pdf_text.strip() or (fund_info.get("ticker") == "N/A" and not metrics):
            return """
            **ANÁLISE LIMITADA - Dados Insuficientes**
            
            Não foi possível extrair informações básicas do fundo ou métricas financeiras do PDF.
            Isso pode ocorrer se o PDF for uma imagem (não textual) ou se o conteúdo não for reconhecido.
            
            Por favor, verifique o arquivo PDF e tente novamente.
            """

        truncated_pdf_text = pdf_text[:settings.MAX_PDF_TEXT_LENGTH]

        prompt = f"""
        Como um analista especialista em Fundos de Investimento Imobiliário (FIIs), faça uma análise COMPLETA e DETALHADA baseada EXCLUSIVAMENTE nos dados fornecidos abaixo.

        REGRA CRÍTICA: Use APENAS informações que estão EXPLICITAMENTE presentes nos dados fornecidos. NÃO invente, calcule ou estime valores que não estão disponíveis. Se uma informação não estiver disponível, declare explicitamente "Informação não disponível no relatório".

        **Informações do Fundo:**
        {json.dumps(fund_info, indent=2, ensure_ascii=False)}
        
        **Métricas Financeiras REAIS:**
        {json.dumps(metrics, indent=2, ensure_ascii=False)}
        
        **Dados de Mercado (se disponíveis):**
        Não disponível nesta análise básica
        
        **Comparação de Mercado:**
        Não disponível nesta análise básica
        
        **Trecho do Relatório:**
        {truncated_pdf_text[:2000]}...
        
        IMPORTANTE: Ao mencionar qualquer valor numérico (P/VP, DY, receitas, etc.), use APENAS os valores que estão nos dados JSON acima. Se um valor é null ou não está disponível, mencione que "o dado não está disponível no relatório analisado".
        
        Forneça uma análise estruturada e ABRANGENTE abordando:
        
        **1. RESUMO EXECUTIVO** (3-4 linhas principais)
        
        **2. ESTRATÉGIA E GESTÃO DO FUNDO**
        - Qual é a estratégia/objetivo do fundo?
        - Segmento de atuação (Escritórios, Shoppings, Logística, etc.)
        - Tipo de gestão (Ativa/Passiva)
        - Qualidade do administrador/gestor
        
        **3. ANÁLISE FUNDAMENTALISTA E BENCHMARKS**
        - Avaliação das métricas P/VP, DY, Vacância
        - Comparação com IFIX (acima/abaixo da média)
        - Qualidade dos ativos e diversificação
        
        **4. TAXAS E CUSTOS**
        - Taxa de administração
        - Taxa de performance (se aplicável)
        - Impacto das taxas no retorno do investidor
        
        **5. DISTRIBUIÇÃO DE RENDIMENTOS**
        - Padrão de distribuição (crescente/constante/decrescente)
        - Resultado por cota vs distribuição
        - Análise do saldo acumulado por cota
        - FFO vs DY - sustentabilidade dos dividendos
        
        **6. VACÂNCIA E INADIMPLÊNCIA**
        - Vacância financeira e física
        - Níveis de inadimplência
        - Impacto na receita do fundo
        
        **7. ALAVANCAGEM E ESTRUTURA FINANCEIRA**
        - Nível de alavancagem atual
        - Plano de amortização de dívidas
        - Capacidade de endividamento
        
        **8. COMPOSIÇÃO E ALOCAÇÃO DA CARTEIRA**
        - Alocação (% Imóveis, % FIIs, % Caixa)
        - Quantidade de imóveis
        - Contratos típicos vs atípicos
        - Vencimento médio dos contratos
        
        **9. CONCENTRAÇÃO E SEGMENTAÇÃO**
        - Segmentos de mercado dos inquilinos
        - Concentração por setor
        - Concentração por inquilino (principais locatários)
        - Situação financeira dos principais inquilinos
        
        **10. PERFORMANCE E RESULTADOS**
        - Resultado vs período anterior
        - Motivos para variação nos resultados
        - Tendência de performance
        
        **11. LIQUIDEZ E COMUNICADOS**
        - Liquidez das cotas (crescendo/estável/diminuindo)
        - Comunicados importantes (compras, vendas, problemas)
        
        **12. RISCOS E PONTOS DE ATENÇÃO**
        - Classificação de risco (Baixo/Médio/Alto)
        - Principais riscos identificados
        - Pontos de atenção para monitoramento
        - Oportunidades identificadas
        
        **13. CONCLUSÃO E ANÁLISE FINAL**
        - Avaliação geral do resultado do fundo
        - Pontos positivos e negativos
        - Sustentabilidade da distribuição
        - Expectativa para próximos resultados
        - Justificativa para eventual desconto no preço
        
        **14. RECOMENDAÇÃO FINAL**
        - Recomendação (Compra Forte/Compra/Manutenção/Venda/Venda Forte)
        - Preço alvo (se possível estimar)
        - Perfil de investidor adequado
        
        IMPORTANTE: Seja técnico, objetivo e baseie-se apenas nos dados fornecidos. Para cada seção, se a informação não estiver disponível no relatório, mencione explicitamente "Informação não disponível no relatório analisado".
        """
        
        result_str = self._call_groq_api(prompt, settings.DEFAULT_ANALYSIS_MODEL, settings.TEMPERATURE, settings.MAX_TOKENS)
        return result_str if result_str else "Erro ao gerar análise de investimento."
    
    async def analyze_pdf_report(self, pdf_file_path: str, include_market_data: bool = True, 
                                include_portfolio: bool = True) -> Dict[str, Any]:
        """Método principal para análise completa do PDF com dados de mercado"""
        logger.info("Iniciando análise completa do PDF...")
        
        # 1. Extrair texto
        pdf_text = self.extract_text_from_pdf(pdf_file_path)
        if pdf_text.startswith("Erro:"):
            return {"error": pdf_text}
        
        # 2. Identificar informações do fundo
        logger.info("Identificando informações do fundo...")
        fund_info = self.identify_fund_info(pdf_text)
        
        # 3. Extrair métricas financeiras do PDF
        logger.info("Extraindo métricas financeiras...")
        metrics = self.extract_financial_metrics(pdf_text)
        
        # 4. Extrair composição da carteira se solicitado
        portfolio_data = {}
        if include_portfolio:
            logger.info("Analisando composição da carteira...")
            portfolio_data = self.extract_portfolio_composition(pdf_text)
        
        # 5. Enriquecer com dados de mercado se solicitado
        enriched_data = {}
        if include_market_data:
            logger.info("Enriquecendo análise com dados de mercado...")
            enriched_data = await self.enrich_analysis_with_market_data(fund_info, metrics)
        
        # 6. Gerar análise completa
        logger.info("Gerando análise de investimento aprimorada...")
        if include_market_data and enriched_data:
            analysis = await self.generate_enhanced_analysis(fund_info, metrics, enriched_data, pdf_text)
        else:
            analysis = self.generate_investment_analysis(fund_info, metrics, pdf_text)
        
        # 7. Compilar resultado
        result = {
            "timestamp": datetime.now().isoformat(),
            "fund_info": fund_info,
            "financial_metrics": enriched_data.get('enhanced_metrics', metrics),
            "investment_analysis": analysis,
            "pdf_text_length": len(pdf_text),
            "success": True,
            "portfolio_composition": portfolio_data
        }
        
        # Adicionar dados de mercado se disponíveis
        if include_market_data and enriched_data:
            result["market_data"] = enriched_data.get('market_data', {})
            result["market_comparison"] = enriched_data.get('market_comparison', {})
            result["sector_analysis"] = enriched_data.get('sector_analysis', {})
        
        logger.info("Análise completa concluída com sucesso!")
        return result
    
    def compare_with_market(self, fund_metrics: Dict) -> str:
        """Compara métricas do fundo com médias de mercado"""
        if not self.groq_client or not fund_metrics:
            return "Não foi possível realizar a comparação com o mercado devido à falta de dados ou cliente de IA."

        prompt = f"""
        Compare as seguintes métricas do FII com as médias históricas do mercado de FIIs brasileiro:
        
        Métricas do Fundo:
        {json.dumps(fund_metrics, indent=2, ensure_ascii=False)}
        
        Considere as seguintes médias de mercado para comparação:
        - Dividend Yield médio: 8-12% ao ano
        - P/VP médio: 0,85-1,05
        - Taxa de vacância média: 5-15%
        
        Faça uma análise comparativa indicando se o fundo está:
        - Acima da média (vantajoso)
        - Na média (neutro)  
        - Abaixo da média (desvantajoso)
        
        Para cada métrica, explique brevemente o que isso significa para o investidor.
        """
        
        result_str = self._call_groq_api(prompt, settings.DEFAULT_ANALYSIS_MODEL, settings.TEMPERATURE, 1000)
        return result_str if result_str else "Erro na comparação com mercado."

    def extract_portfolio_composition(self, pdf_text: str) -> Dict[str, Any]:
        """Extrai composição da carteira de imóveis"""
        if not self.groq_client or not pdf_text.strip():
            logger.warning("Cliente Groq não disponível ou texto do PDF vazio. Retornando dados vazios.")
            return {}

        truncated_pdf_text = pdf_text[:settings.MAX_PDF_TEXT_LENGTH]

        prompt = f"""
        Analise o relatório e extraia informações sobre a carteira de imóveis do FII:
        
        Texto do relatório:
        {truncated_pdf_text}...
        
        IMPORTANTE: Responda APENAS com JSON válido, sem texto adicional, sem blocos de código markdown, sem explicações.
        
        Estrutura esperada:
        {{
            "principais_imoveis": ["Nome do Imóvel 1", "Nome do Imóvel 2"],
            "localizacao_geografica": ["São Paulo", "Rio de Janeiro"],
            "setores_atuacao": ["Escritórios", "Shoppings", "Logística"],
            "inquilinos_principais": ["Empresa 1", "Empresa 2"],
            "percentual_ocupacao": 95.5,
            "vencimento_medio_contratos": "3.2 anos"
        }}
        
        Se uma informação não for encontrada, use null ou array vazio [].
        """
        
        result_str = self._call_groq_api(prompt, settings.DEFAULT_ANALYSIS_MODEL, settings.TEMPERATURE, 1000)
        
        if result_str:
            try:
                # Verificar se a resposta não está vazia
                if not result_str.strip():
                    logger.warning("IA retornou resposta vazia para composição da carteira")
                    return {}
                
                parsed_json = json.loads(result_str)
                logger.info("Composição da carteira extraída com sucesso")
                return parsed_json
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao parsear JSON da IA para composição da carteira: {e}")
                logger.error(f"Resposta bruta da IA: '{result_str[:500]}...'")
                # Retornar estrutura básica se o JSON falhar
                return {
                    "error": "Não foi possível extrair composição da carteira",
                    "raw_response": result_str[:200] if result_str else "Resposta vazia"
                }
        return {}

    def _validate_and_clean_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Valida e limpa as métricas extraídas"""
        cleaned = {}
        
        # Lista de campos numéricos esperados
        numeric_fields = [
            'receitas_alugueis', 'despesas_operacionais', 'resultado_liquido',
            'patrimonio_liquido', 'vp_por_cota', 'dividend_yield', 'p_vp',
            'numero_cotas', 'valor_cota', 'ffo', 'taxa_administracao',
            'taxa_performance', 'vacancia_fisica', 'vacancia_financeira',
            'inadimplencia', 'alavancagem', 'distribuicao_cota'
        ]
        
        # Validar campos numéricos
        for field in numeric_fields:
            if field in metrics:
                value = metrics[field]
                if value is not None and str(value).strip() != '' and str(value).lower() != 'null':
                    try:
                        # Converter string para número se necessário
                        if isinstance(value, str):
                            # Remover formatação brasileira (pontos de milhares)
                            value = value.replace('.', '').replace(',', '.')
                        cleaned[field] = float(value) if '.' in str(value) else int(value)
                    except (ValueError, TypeError):
                        logger.warning(f"Valor inválido para {field}: {value}")
                        cleaned[field] = None
                else:
                    cleaned[field] = None
        
        # Campos de texto
        text_fields = ['maior_inquilino_nome']
        for field in text_fields:
            if field in metrics:
                value = metrics[field]
                if value and str(value).strip() and str(value).lower() != 'null':
                    cleaned[field] = str(value).strip()
                else:
                    cleaned[field] = None
        
        return cleaned
    
    def _extract_metrics_fallback(self, text: str) -> Dict[str, Any]:
        """Extração manual quando o JSON falha"""
        logger.info("Tentando extração manual de métricas...")
        
        # Procurar por padrões numéricos conhecidos
        import re
        
        fallback_metrics = {}
        
        # Padrões para receitas (em milhares de reais)
        receita_patterns = [
            r'receita[s]?\s+(?:de\s+)?(?:locação|alugu[éei]s?):?\s*r?\$?\s*([\d.,]+)',
            r'receitas?\s+de\s+aluguéis:?\s*r?\$?\s*([\d.,]+)',
            r'receita\s+com\s+locação:?\s*r?\$?\s*([\d.,]+)'
        ]
        
        for pattern in receita_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = match.group(1).replace('.', '').replace(',', '.')
                    fallback_metrics['receitas_alugueis'] = float(value) * 1000  # Converter para reais
                    break
                except:
                    continue
        
        # Padrões para P/VP
        pvp_patterns = [
            r'p/vp:?\s*([\d.,]+)',
            r'preço\s*/\s*vp:?\s*([\d.,]+)',
            r'preço\s+sobre\s+valor\s+patrimonial:?\s*([\d.,]+)'
        ]
        
        for pattern in pvp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = match.group(1).replace(',', '.')
                    fallback_metrics['p_vp'] = float(value)
                    break
                except:
                    continue
        
        # Padrões para Dividend Yield
        dy_patterns = [
            r'dividend\s+yield:?\s*([\d.,]+)%?',
            r'dy:?\s*([\d.,]+)%?',
            r'rendimento:?\s*([\d.,]+)%?'
        ]
        
        for pattern in dy_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = match.group(1).replace(',', '.')
                    fallback_metrics['dividend_yield'] = float(value)
                    break
                except:
                    continue
        
        logger.info(f"Extração manual encontrou {len(fallback_metrics)} métricas")
        return fallback_metrics
    
    async def enrich_analysis_with_market_data(self, fund_info: Dict, metrics: Dict) -> Dict[str, Any]:
        """Enriquece a análise com dados de mercado externos"""
        if not market_provider:
            logger.warning("Provedor de dados de mercado não disponível")
            return {}
        
        ticker = fund_info.get('ticker', 'N/A')
        if ticker == 'N/A':
            logger.warning("Ticker não identificado, pulando enriquecimento com dados de mercado")
            return {}
        
        try:
            logger.info(f"🔍 Buscando dados de mercado para {ticker}...")
            
            # Buscar dados do FII
            market_data = await market_provider.get_fii_data(ticker)
            
            # Buscar comparação de mercado
            market_comparison = await market_provider.get_market_comparison(ticker)
            
            # Buscar análise setorial
            fii_type = fund_info.get('tipo', 'Híbrido')
            sector_analysis = await market_provider.get_sector_analysis(fii_type)
            
            # Combinar métricas do PDF com dados de mercado
            enhanced_metrics = metrics.copy()
            
            # Enriquecer com dados de mercado quando PDF não tem
            if market_data and 'error' not in market_data:
                if not enhanced_metrics.get('dividend_yield') and market_data.get('dividend_yield'):
                    enhanced_metrics['dividend_yield'] = market_data['dividend_yield']
                    logger.info(f"📊 DY de mercado: {market_data['dividend_yield']}%")
                
                if not enhanced_metrics.get('p_vp') and market_data.get('p_vp'):
                    enhanced_metrics['p_vp'] = market_data['p_vp']
                    logger.info(f"📊 P/VP de mercado: {market_data['p_vp']}")
                
                # Adicionar dados de mercado
                enhanced_metrics.update({
                    'current_price_market': market_data.get('current_price', 0),
                    'volume_market': market_data.get('volume', 0),
                    'volatility_annual': market_data.get('metrics', {}).get('volatility_annual', 0),
                    'liquidity_score': market_data.get('metrics', {}).get('liquidity_score', 'N/A')
                })
            
            return {
                'enhanced_metrics': enhanced_metrics,
                'market_data': market_data,
                'market_comparison': market_comparison,
                'sector_analysis': sector_analysis
            }
            
        except Exception as e:
            logger.error(f"Erro ao enriquecer com dados de mercado: {e}")
            return {'enhanced_metrics': metrics}
    
    async def generate_enhanced_analysis(self, fund_info: Dict, metrics: Dict, 
                                       enriched_data: Dict, pdf_text: str) -> str:
        """Gera análise aprimorada com dados de mercado"""
        if not self.groq_client:
            return "Análise limitada - Cliente de IA não disponível"
        
        market_data = enriched_data.get('market_data', {})
        market_comparison = enriched_data.get('market_comparison', {})
        enhanced_metrics = enriched_data.get('enhanced_metrics', metrics)
        
        truncated_pdf_text = pdf_text[:settings.MAX_PDF_TEXT_LENGTH // 2]  # Usar menos texto para dar espaço aos dados de mercado
        
        prompt = f"""
        Como um analista especialista em FIIs, faça uma análise COMPLETA e DETALHADA usando TODOS os dados fornecidos.

        REGRA CRÍTICA: Use APENAS informações que estão EXPLICITAMENTE presentes nos dados. NÃO invente valores. Se um dado não estiver disponível, declare "não disponível nos dados analisados".

        **Informações do Fundo:**
        {json.dumps(fund_info, indent=2, ensure_ascii=False)}
        
        **Métricas Financeiras Consolidadas (PDF + Mercado):**
        {json.dumps(enhanced_metrics, indent=2, ensure_ascii=False)}
        
        **Dados de Mercado em Tempo Real:**
        {json.dumps(market_data, indent=2, ensure_ascii=False)}
        
        **Comparação com Mercado:**
        {json.dumps(market_comparison, indent=2, ensure_ascii=False)}
        
        Forneça uma análise ABRANGENTE com estas seções:
        
        **1. RESUMO EXECUTIVO**
        **2. ANÁLISE FUNDAMENTALISTA** 
        **3. COMPARAÇÃO COM MERCADO**
        **4. PERFORMANCE E LIQUIDEZ**
        **5. ANÁLISE DE RISCO**
        **6. DISTRIBUIÇÃO DE RENDIMENTOS**
        **7. RECOMENDAÇÃO FINAL**
        
        Para cada métrica mencionada, cite a fonte (PDF ou mercado) e se não estiver disponível, declare explicitamente.
        """
        
        result_str = self._call_groq_api(prompt, settings.DEFAULT_ANALYSIS_MODEL, settings.TEMPERATURE, settings.MAX_TOKENS)
        return result_str if result_str else "Erro ao gerar análise aprimorada."

# Função auxiliar para usar em outras partes do sistema
async def quick_pdf_analysis(pdf_file_path: str, include_market_data: bool = True, 
                            include_portfolio: bool = True) -> Dict[str, Any]:
    """Função de conveniência para análise rápida com dados de mercado"""
    analyzer = PDFAnalyzer()
    return await analyzer.analyze_pdf_report(pdf_file_path, include_market_data, include_portfolio)

def sync_quick_pdf_analysis(pdf_file_path: str) -> Dict[str, Any]:
    """Função síncrona para compatibilidade com código existente"""
    analyzer = PDFAnalyzer()
    # Executar de forma síncrona
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(analyzer.analyze_pdf_report(pdf_file_path, True, True))
        return result
    finally:
        loop.close()
