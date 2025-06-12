"""Análise específica por segmento de FII"""

def get_segment_specific_analysis(segmento: str) -> dict:
    """Retorna análise e métricas específicas para cada segmento de FII"""
    
    segment_data = {
        "Papel/CRI": {
            "metricas_chave": ["Rating dos CRIs", "Prazo médio", "Inadimplência", "Diversificação"],
            "riscos_principais": ["Risco de crédito", "Concentração em poucos emissores", "Liquidez"],
            "pontos_atencao": ["Qualidade dos recebíveis", "Garantias", "Histórico dos cedentes"],
            "analise_especifica": "Para FIIs de Papel/CRI, é fundamental analisar a qualidade dos certificados de recebíveis imobiliários na carteira, o rating médio dos ativos, a diversificação por setor e emissor, e o histórico de inadimplência."
        },
        "FIagro": {
            "metricas_chave": ["Produtividade agrícola", "Contratos de arrendamento", "Preços commodities"],
            "riscos_principais": ["Clima", "Preços de commodities", "Pragas e doenças"],
            "pontos_atencao": ["Localização das terras", "Qualidade do solo", "Arrendatários"],
            "analise_especifica": "FIIs de agronegócio devem ser avaliados considerando a qualidade das terras, contratos de arrendamento, produtividade histórica e exposição aos preços de commodities."
        },
        "Hotel": {
            "metricas_chave": ["Taxa de ocupação", "Diária média", "RevPAR", "Sazonalidade"],
            "riscos_principais": ["Sazonalidade", "Crises econômicas", "Turismo"],
            "pontos_atencao": ["Localização", "Padrão do hotel", "Gestão operacional"],
            "analise_especifica": "Hotéis requerem análise da taxa de ocupação, diária média (ADR), receita por quarto disponível (RevPAR), sazonalidade e qualidade da gestão hoteleira."
        },
        "Lajes Corporativas": {
            "metricas_chave": ["Taxa de ocupação", "Preço por m²", "Contratos longos", "AAA vs BB"],
            "riscos_principais": ["Vacância", "Inadimplência", "Obsolescência"],
            "pontos_atencao": ["Localização", "Qualidade dos inquilinos", "Modernização"],
            "analise_especifica": "Lajes corporativas devem ser avaliadas pela localização, qualidade da construção, perfil dos inquilinos, duração dos contratos e necessidade de modernização."
        },
        "Logística": {
            "metricas_chave": ["Taxa de ocupação", "Contratos built-to-suit", "Localização", "E-commerce"],
            "riscos_principais": ["Mudanças no varejo", "Localização", "Obsolescência"],
            "pontos_atencao": ["Proximidade centros urbanos", "Acessos rodoviários", "Padrão construtivo"],
            "analise_especifica": "Galpões logísticos são avaliados pela localização estratégica, acessos rodoviários, proximidade de centros urbanos, contratos com grandes varejistas e crescimento do e-commerce."
        },
        "Shopping": {
            "metricas_chave": ["Vendas por m²", "Taxa de ocupação", "Fluxo de pessoas", "ABL"],
            "riscos_principais": ["E-commerce", "Mudanças de consumo", "Localização"],
            "pontos_atencao": ["Mix de lojas", "Âncoras", "Localização", "Renda da região"],
            "analise_especifica": "Shopping centers devem ser analisados pelas vendas por m², taxa de ocupação, fluxo de pessoas, mix de lojas, presença de âncoras e adaptação ao e-commerce."
        },
        "Residencial": {
            "metricas_chave": ["Taxa de ocupação", "Valor do aluguel", "Inadimplência", "Localização"],
            "riscos_principais": ["Vacância", "Inadimplência", "Desvalorização"],
            "pontos_atencao": ["Localização", "Padrão dos imóveis", "Perfil dos inquilinos"],
            "analise_especifica": "Imóveis residenciais para locação devem ser avaliados pela localização, padrão dos imóveis, taxa de ocupação, valor dos aluguéis e perfil socioeconômico dos inquilinos."
        },
        "Renda Urbana": {
            "metricas_chave": ["Diversificação", "Taxa de ocupação", "Localização", "Mix de ativos"],
            "riscos_principais": ["Concentração geográfica", "Diversificação", "Gestão"],
            "pontos_atencao": ["Diversificação por tipo", "Localização", "Qualidade dos ativos"],
            "analise_especifica": "FIIs de renda urbana diversificada devem ser avaliados pela diversificação por tipo de ativo, localização geográfica, qualidade da carteira e capacidade de gestão."
        },
        "FOF": {
            "metricas_chave": ["Diversificação", "Performance dos FIIs", "Taxa de gestão", "Liquidez"],
            "riscos_principais": ["Dupla tributação", "Gestão ativa", "Concentração"],
            "pontos_atencao": ["Critério de seleção", "Diversificação", "Custos"],
            "analise_especifica": "Fundos de fundos devem ser avaliados pela estratégia de seleção, diversificação da carteira, performance histórica, custos de gestão e liquidez dos ativos."
        },
        "Desenvolvimento": {
            "metricas_chave": ["Cronograma de obras", "Pré-locação", "VGV", "Margem"],
            "riscos_principais": ["Atraso de obras", "Custo de construção", "Vacância"],
            "pontos_atencao": ["Experiência do desenvolvedor", "Licenças", "Mercado local"],
            "analise_especifica": "FIIs de desenvolvimento requerem análise do cronograma de obras, pré-locação, valor geral de vendas (VGV), experiência do desenvolvedor e riscos de construção."
        },
        "Educação": {
            "metricas_chave": ["Taxa de ocupação", "Qualidade do ensino", "Contratos longos", "Sazonalidade"],
            "riscos_principais": ["Mudanças regulatórias", "EAD", "Demografia"],
            "pontos_atencao": ["Instituição inquilina", "Localização", "Regulamentação"],
            "analise_especifica": "Imóveis educacionais devem considerar a qualidade da instituição inquilina, estabilidade dos contratos, impacto do ensino à distância e mudanças demográficas."
        },
        "Hospital": {
            "metricas_chave": ["Taxa de ocupação", "Contratos longos", "Especialização", "Localização"],
            "riscos_principais": ["Regulamentação", "Tecnologia médica", "Demografia"],
            "pontos_atencao": ["Qualidade do operador", "Especialização", "Equipamentos"],
            "analise_especifica": "Hospitais e clínicas requerem análise da qualidade do operador de saúde, especialização médica, localização estratégica e estabilidade dos contratos de locação."
        }
    }
    
    return segment_data.get(segmento, {
        "metricas_chave": ["Taxa de ocupação", "Rentabilidade", "Localização"],
        "riscos_principais": ["Mercado específico", "Regulamentação", "Concorrência"],
        "pontos_atencao": ["Análise específica do segmento", "Qualidade dos ativos"],
        "analise_especifica": f"Segmento {segmento} requer análise específica de acordo com suas características particulares."
    })

def enhance_analysis_with_segment(analysis_data: dict) -> dict:
    """Enriquece a análise com informações específicas do segmento"""
    
    segmento = analysis_data.get("fund_info", {}).get("segmento", "Outros")
    segment_info = get_segment_specific_analysis(segmento)
    
    # Adicionar informações do segmento
    analysis_data["segment_analysis"] = {
        "segmento": segmento,
        "metricas_chave": segment_info.get("metricas_chave", []),
        "riscos_principais": segment_info.get("riscos_principais", []),
        "pontos_atencao": segment_info.get("pontos_atencao", []),
        "analise_especifica": segment_info.get("analise_especifica", "")
    }
    
    return analysis_data