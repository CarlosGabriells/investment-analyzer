const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface AnalysisResult {
  session_id: string;
  fund_info: {
    ticker: string;
    nome: string;
    cnpj: string;
    administrador: string;
    gestor: string;
    tipo: string;
    segmento: string;
    data_relatorio: string;
  };
  financial_metrics: {
    receitas_alugueis: number | string;
    despesas_operacionais: number | string | null;
    resultado_liquido: number | string;
    patrimonio_liquido: number | string;
    vp_por_cota: number | string;
    dividend_yield: number | string;
    p_vp: number | string;
    taxa_vacancia: number | string;
    numero_cotas: number | string;
    valor_cota: number | string;
  };
  detailed_analysis: any;
  human_readable_analysis?: string;
  summary?: string;
  cached?: boolean;
  status?: string;
  error?: string;
  suggestion?: string;
  debug_info?: any;
}

export interface RankingResult {
  ranking: Array<{
    ticker: string;
    nome: string;
    valor: number;
    posicao: number;
  }>;
  cached?: boolean;
}

export interface SessionAnalyses {
  session_id: string;
  analyses: Array<{
    id: number;
    fii_code: string;
    fii_name: string;
    fund_info: any;
    financial_metrics: any;
    detailed_analysis: any;
    pdf_filename: string;
    created_at: string;
  }>;
}

class ApiService {
  async uploadPDF(file: File, sessionId?: string): Promise<AnalysisResult> {
    const formData = new FormData();
    formData.append('pdf_file', file);
    if (sessionId) {
      formData.append('session_id', sessionId);
    }

    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async getRanking(criteria: 'dividend_yield' | 'pvp', sessionId: string): Promise<RankingResult> {
    const response = await fetch(`${API_BASE_URL}/ranking/${criteria}?session_id=${sessionId}`);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async getSessionAnalyses(sessionId: string): Promise<SessionAnalyses> {
    const response = await fetch(`${API_BASE_URL}/analysis/${sessionId}`);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async getSpecificAnalysis(sessionId: string, fiiCode: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/analysis/${sessionId}/${fiiCode}`);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${API_BASE_URL}/health`);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }
}

export const apiService = new ApiService();