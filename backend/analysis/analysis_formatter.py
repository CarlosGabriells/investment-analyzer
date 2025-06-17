"""Formatador de análises para linguagem humana"""

def format_analysis_to_human(analysis_data):
    """Converte JSON da análise para linguagem humana legível"""
    
    if not analysis_data or "error" in analysis_data:
        return "Erro na análise: " + analysis_data.get("error", "Erro desconhecido")
    
    fund_info = analysis_data.get("fund_info", {})
    financial_metrics = analysis_data.get("financial_metrics", {})
    detailed_analysis = analysis_data.get("detailed_analysis", "")
    segment_analysis = analysis_data.get("segment_analysis", {})
    
    # Helper para formatar valores
    def format_value(value, is_currency=False, is_percentage=False, is_large_currency=False):
        if value is None or value == "N/A" or value == "Não informado" or value == 0:
            return "Não informado"
        
        try:
            num_value = float(value)
            
            if num_value == 0:
                return "Não informado"
            
            if is_currency:
                if is_large_currency and num_value > 1000000:
                    # Formato para valores grandes (milhões)
                    if num_value >= 1000000000:  # Bilhões
                        return f"R$ {num_value/1000000000:.2f} bi"
                    else:  # Milhões
                        return f"R$ {num_value/1000000:.2f} mi"
                else:
                    # Formato normal com separadores
                    formatted = f"{num_value:,.2f}"
                    # Trocar ponto e vírgula para formato brasileiro
                    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
                    return f"R$ {formatted}"
            elif is_percentage:
                return f"{num_value:.2f}%"
            else:
                if num_value > 1000000:
                    formatted = f"{num_value:,.0f}"
                    formatted = formatted.replace(",", ".")
                    return formatted
                else:
                    return f"{num_value:,.2f}".replace(",", ".")
        except (ValueError, TypeError):
            return str(value) if value else "Não informado"
    
    # Retornar apenas a análise textual sem HTML
    formatted_text = f"""**📊 {fund_info.get('ticker', 'FII')} - {fund_info.get('nome', 'Análise Detalhada do Fundo')}**

**🏢 Informações Básicas**
Ticker: {fund_info.get('ticker', 'N/A')}
CNPJ: {fund_info.get('cnpj', 'N/A')}
Administrador: {fund_info.get('administrador', 'N/A')}
Gestor: {fund_info.get('gestor', 'N/A')}
Segmento: {fund_info.get('segmento', 'N/A')}
Data Relatório: {fund_info.get('data_relatorio', 'N/A')}

**📈 Indicadores-Chave**
Dividend Yield: {format_value(financial_metrics.get('dividend_yield'), is_percentage=True)}
P/VP: {format_value(financial_metrics.get('p_vp'))}
Taxa Vacância: {format_value(financial_metrics.get('taxa_vacancia'), is_percentage=True)}

**💰 Métricas Financeiras**
Receitas de Aluguéis: {format_value(financial_metrics.get('receitas_alugueis'), is_currency=True)}
Despesas Operacionais: {format_value(financial_metrics.get('despesas_operacionais'), is_currency=True)}
Resultado Líquido: {format_value(financial_metrics.get('resultado_liquido'), is_currency=True)}
Patrimônio Líquido: {format_value(financial_metrics.get('patrimonio_liquido'), is_currency=True, is_large_currency=True)}
VP por Cota: {format_value(financial_metrics.get('vp_por_cota'), is_currency=True)}
Número de Cotas: {format_value(financial_metrics.get('numero_cotas'))}

**🔍 Análise Detalhada**
{detailed_analysis}

{f'''**🎯 Análise do Segmento: {segment_analysis.get("segmento", "").upper()}**

**📊 Métricas-Chave**
{chr(10).join([f"• {metrica}" for metrica in segment_analysis.get("metricas_chave", [])])}

**⚠️ Principais Riscos**
{chr(10).join([f"• {risco}" for risco in segment_analysis.get("riscos_principais", [])])}

**🔎 Pontos de Atenção**
{chr(10).join([f"• {ponto}" for ponto in segment_analysis.get("pontos_atencao", [])])}

**💡 Análise Específica**
{segment_analysis.get("analise_especifica", "")}
''' if segment_analysis.get("segmento") else ""}

✅ Análise gerada automaticamente com base no relatório oficial do fundo"""
    
    return formatted_text.strip()

def get_analysis_summary(analysis_data):
    """Gera um resumo executivo da análise"""
    
    if not analysis_data or "error" in analysis_data:
        return "❌ Erro na análise"
    
    fund_info = analysis_data.get("fund_info", {})
    financial_metrics = analysis_data.get("financial_metrics", {})
    
    ticker = fund_info.get('ticker', 'FII')
    dy = financial_metrics.get('dividend_yield')
    pvp = financial_metrics.get('p_vp')
    
    # Determinar status do P/VP
    pvp_status = ""
    if pvp:
        try:
            pvp_num = float(pvp)
            if pvp_num < 0.9:
                pvp_status = " (Com desconto)"
            elif pvp_num > 1.1:
                pvp_status = " (Com prêmio)"
            else:
                pvp_status = " (Preço justo)"
        except:
            pass
    
    # Montar resumo
    dy_text = f"{dy:.2f}%" if dy and dy != "N/A" else "N/A"
    pvp_text = f"{pvp:.2f}{pvp_status}" if pvp and pvp != "N/A" else "N/A"
    
    return f"📊 {ticker} | DY: {dy_text} | P/VP: {pvp_text}"