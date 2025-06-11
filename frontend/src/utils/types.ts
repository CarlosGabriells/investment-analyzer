export type FundInfo = {
  ticker: string;
  nome: string;
  cnpj: string;
  administrador: string;
  gestor: string;
  tipo: string;
  data_relatorio: string;
};

export type FinancialMetrics = {
  receitas_alugueis: number;
  despesas_operacionais: number | null;
  resultado_liquido: number;
  patrimonio_liquido: number;
  vp_por_cota: number;
  dividend_yield: number;
  p_vp: number;
  taxa_vacancia: number;
  numero_cotas: number;
  valor_cota: number;
};

export type FundData = {
  portfolio_composition: any;
  timestamp: string;
  fund_info: FundInfo;
  financial_metrics: FinancialMetrics;
  investment_analysis: string;
};
