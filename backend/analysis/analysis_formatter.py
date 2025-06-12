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
    
    # Construir texto formatado em layout elegante com HTML/CSS
    formatted_text = f"""
<div class="analysis-container" style="font-family: system-ui, -apple-system, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #1f2937; color: #f9fafb; border-radius: 12px;">
  
  <!-- Header Section -->
  <div style="text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #1e40af, #7c3aed); border-radius: 10px;">
    <h1 style="margin: 0 0 10px 0; font-size: 28px; font-weight: bold; color: white;">📊 {fund_info.get('ticker', 'FII')}</h1>
    <h2 style="margin: 0; font-size: 18px; opacity: 0.9; color: #e5e7eb;">{fund_info.get('nome', 'Análise Detalhada do Fundo')}</h2>
  </div>

  <!-- Two Column Layout -->
  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px;">
    
    <!-- Left Column: Fund Info -->
    <div style="background: #374151; padding: 20px; border-radius: 10px; border: 1px solid #4b5563;">
      <h3 style="margin: 0 0 20px 0; font-size: 20px; color: #60a5fa; display: flex; align-items: center; gap: 10px;">🏢 Informações Básicas</h3>
      
      <div style="display: grid; gap: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #4b5563;">
          <span style="font-weight: 600; color: #d1d5db;">Ticker:</span>
          <span style="color: #fbbf24; font-weight: bold;">{fund_info.get('ticker', 'N/A')}</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: start; padding: 8px 0; border-bottom: 1px solid #4b5563;">
          <span style="font-weight: 600; color: #d1d5db; flex-shrink: 0; margin-right: 10px;">CNPJ:</span>
          <span style="color: #e5e7eb; text-align: right; font-size: 14px;">{fund_info.get('cnpj', 'N/A')}</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: start; padding: 8px 0; border-bottom: 1px solid #4b5563;">
          <span style="font-weight: 600; color: #d1d5db; flex-shrink: 0; margin-right: 10px;">Administrador:</span>
          <span style="color: #e5e7eb; text-align: right; font-size: 14px;">{fund_info.get('administrador', 'N/A')}</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: start; padding: 8px 0; border-bottom: 1px solid #4b5563;">
          <span style="font-weight: 600; color: #d1d5db; flex-shrink: 0; margin-right: 10px;">Gestor:</span>
          <span style="color: #e5e7eb; text-align: right; font-size: 14px;">{fund_info.get('gestor', 'N/A')}</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #4b5563;">
          <span style="font-weight: 600; color: #d1d5db;">Segmento:</span>
          <span style="color: #34d399; font-weight: 600; background: #064e3b; padding: 4px 8px; border-radius: 6px; font-size: 12px;">{fund_info.get('segmento', 'N/A')}</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0;">
          <span style="font-weight: 600; color: #d1d5db;">Data Relatório:</span>
          <span style="color: #e5e7eb; font-size: 14px;">{fund_info.get('data_relatorio', 'N/A')}</span>
        </div>
      </div>
    </div>

    <!-- Right Column: Key Indicators -->
    <div style="background: #374151; padding: 20px; border-radius: 10px; border: 1px solid #4b5563;">
      <h3 style="margin: 0 0 20px 0; font-size: 20px; color: #34d399; display: flex; align-items: center; gap: 10px;">📈 Indicadores-Chave</h3>
      
      <div style="display: grid; gap: 15px;">
        <!-- Dividend Yield Card -->
        <div style="background: linear-gradient(135deg, #065f46, #047857); padding: 15px; border-radius: 8px; text-align: center;">
          <div style="font-size: 14px; color: #d1fae5; margin-bottom: 5px;">Dividend Yield</div>
          <div style="font-size: 24px; font-weight: bold; color: white;">{format_value(financial_metrics.get('dividend_yield'), is_percentage=True)}</div>
        </div>
        
        <!-- P/VP Card -->
        <div style="background: linear-gradient(135deg, #1e40af, #3b82f6); padding: 15px; border-radius: 8px; text-align: center;">
          <div style="font-size: 14px; color: #dbeafe; margin-bottom: 5px;">P/VP</div>
          <div style="font-size: 24px; font-weight: bold; color: white;">{format_value(financial_metrics.get('p_vp'))}</div>
        </div>
        
        <!-- Taxa Vacância -->
        <div style="background: linear-gradient(135deg, #7c2d12, #dc2626); padding: 15px; border-radius: 8px; text-align: center;">
          <div style="font-size: 14px; color: #fecaca; margin-bottom: 5px;">Taxa Vacância</div>
          <div style="font-size: 24px; font-weight: bold; color: white;">{format_value(financial_metrics.get('taxa_vacancia'), is_percentage=True)}</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Financial Metrics Section -->
  <div style="background: #374151; padding: 20px; border-radius: 10px; border: 1px solid #4b5563; margin-bottom: 30px;">
    <h3 style="margin: 0 0 20px 0; font-size: 20px; color: #fbbf24; display: flex; align-items: center; gap: 10px;">💰 Métricas Financeiras</h3>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
      <!-- Left Financial Column -->
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #4b5563;">
          <span style="color: #d1d5db;">Receitas de Aluguéis</span>
          <span style="color: #34d399; font-weight: 600;">{format_value(financial_metrics.get('receitas_alugueis'), is_currency=True)}</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #4b5563;">
          <span style="color: #d1d5db;">Despesas Operacionais</span>
          <span style="color: #f87171; font-weight: 600;">{format_value(financial_metrics.get('despesas_operacionais'), is_currency=True)}</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0;">
          <span style="color: #d1d5db;">Resultado Líquido</span>
          <span style="color: #60a5fa; font-weight: 600;">{format_value(financial_metrics.get('resultado_liquido'), is_currency=True)}</span>
        </div>
      </div>
      
      <!-- Right Financial Column -->
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #4b5563;">
          <span style="color: #d1d5db;">Patrimônio Líquido</span>
          <span style="color: #a78bfa; font-weight: 600;">{format_value(financial_metrics.get('patrimonio_liquido'), is_currency=True, is_large_currency=True)}</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #4b5563;">
          <span style="color: #d1d5db;">VP por Cota</span>
          <span style="color: #fbbf24; font-weight: 600;">{format_value(financial_metrics.get('vp_por_cota'), is_currency=True)}</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0;">
          <span style="color: #d1d5db;">Número de Cotas</span>
          <span style="color: #e5e7eb; font-weight: 600;">{format_value(financial_metrics.get('numero_cotas'))}</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Analysis Section -->
  <div style="background: #374151; padding: 20px; border-radius: 10px; border: 1px solid #4b5563; margin-bottom: 20px;">
    <h3 style="margin: 0 0 20px 0; font-size: 20px; color: #a78bfa; display: flex; align-items: center; gap: 10px;">🔍 Análise Detalhada</h3>
    <div style="color: #e5e7eb; line-height: 1.6; white-space: pre-wrap;">{detailed_analysis}</div>
  </div>

  {f'''
  <!-- Segment Analysis Section -->
  <div style="background: linear-gradient(135deg, #7c2d12, #dc2626); padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #7f1d1d;">
    <h3 style="margin: 0 0 20px 0; font-size: 20px; color: white; display: flex; align-items: center; gap: 10px;">🎯 Análise do Segmento: {segment_analysis.get("segmento", "").upper()}</h3>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
      <!-- Métricas-Chave -->
      <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px;">
        <h4 style="margin: 0 0 15px 0; color: #fecaca; font-size: 16px;">📊 Métricas-Chave</h4>
        <div style="color: #fef2f2; font-size: 14px; line-height: 1.5;">
          {chr(10).join([f"<div style='margin-bottom: 8px;'>• {metrica}</div>" for metrica in segment_analysis.get("metricas_chave", [])])}
        </div>
      </div>
      
      <!-- Principais Riscos -->
      <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px;">
        <h4 style="margin: 0 0 15px 0; color: #fecaca; font-size: 16px;">⚠️ Principais Riscos</h4>
        <div style="color: #fef2f2; font-size: 14px; line-height: 1.5;">
          {chr(10).join([f"<div style='margin-bottom: 8px;'>• {risco}</div>" for risco in segment_analysis.get("riscos_principais", [])])}
        </div>
      </div>
    </div>
    
    <!-- Pontos de Atenção -->
    <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
      <h4 style="margin: 0 0 15px 0; color: #fecaca; font-size: 16px;">🔎 Pontos de Atenção</h4>
      <div style="color: #fef2f2; font-size: 14px; line-height: 1.5;">
        {chr(10).join([f"<div style='margin-bottom: 8px;'>• {ponto}</div>" for ponto in segment_analysis.get("pontos_atencao", [])])}
      </div>
    </div>
    
    <!-- Análise Específica -->
    <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px;">
      <h4 style="margin: 0 0 15px 0; color: #fecaca; font-size: 16px;">💡 Análise Específica</h4>
      <div style="color: #fef2f2; font-size: 14px; line-height: 1.6; white-space: pre-wrap;">{segment_analysis.get("analise_especifica", "")}</div>
    </div>
  </div>
  ''' if segment_analysis.get("segmento") else ""}

  <!-- Footer -->
  <div style="text-align: center; padding: 15px; background: #4b5563; border-radius: 8px; border: 1px solid #6b7280;">
    <div style="color: #34d399; font-size: 14px; font-weight: 600;">✅ Análise gerada automaticamente com base no relatório oficial do fundo</div>
  </div>

</div>
"""
    
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