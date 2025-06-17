'use client';

import React from 'react';
import { Brain, Building, TrendingUp, DollarSign, Target, AlertTriangle, Eye, CheckCircle } from 'lucide-react';

type DetailedAnalysisProps = {
  analysisData: any;
};

export default function DetailedAnalysis({ analysisData }: DetailedAnalysisProps) {
  if (!analysisData) {
    return (
      <div className="bg-bgTable p-4 rounded-[8px] w-full">
        <div className="text-center py-8">
          <Brain className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-400">Selecione uma análise para visualizar os detalhes completos.</p>
        </div>
      </div>
    );
  }

  const fundInfo = analysisData.fund_info || {};
  const financialMetrics = analysisData.financial_metrics || {};
  const detailedAnalysis = analysisData.detailed_analysis || '';
  const segmentAnalysis = analysisData.segment_analysis || {};

  // Helper para formatar valores
  const formatValue = (value: any, isPercentage = false, isCurrency = false, isLargeCurrency = false) => {
    if (value === null || value === undefined || value === "N/A" || value === "Não informado" || value === 0) {
      return "Não informado";
    }
    
    try {
      const numValue = parseFloat(value);
      
      if (numValue === 0) return "Não informado";
      
      if (isCurrency) {
        if (isLargeCurrency && numValue > 1000000) {
          if (numValue >= 1000000000) {
            return `R$ ${(numValue/1000000000).toFixed(2)} bi`;
          } else {
            return `R$ ${(numValue/1000000).toFixed(2)} mi`;
          }
        } else {
          return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
          }).format(numValue);
        }
      } else if (isPercentage) {
        return `${numValue.toFixed(2)}%`;
      } else {
        return new Intl.NumberFormat('pt-BR').format(numValue);
      }
    } catch (error) {
      return String(value);
    }
  };

  return (
    <div className="bg-bgTable p-4 sm:p-6 rounded-[8px] w-full space-y-6">
      {/* Header */}
      <div className="text-center bg-gradient-to-r from-blue-600 to-purple-600 p-4 sm:p-6 rounded-lg">
        <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-white mb-2 break-words">
          📊 {fundInfo.ticker || 'FII'}
        </h1>
        <h2 className="text-sm sm:text-base lg:text-lg text-gray-200 break-words">
          {fundInfo.nome || 'Análise Detalhada do Fundo'}
        </h2>
      </div>

      {/* Main Content */}
      <div className="space-y-6">
        
        {/* Fund Info */}
        <div className="bg-gray-700 p-4 sm:p-6 rounded-lg space-y-4">
          <h3 className="text-lg sm:text-xl text-blue-400 flex items-center gap-2 mb-4">
            <Building className="w-5 h-5" />
            Informações Básicas
          </h3>
          
          <div className="space-y-3">
            <div className="flex flex-col sm:flex-row sm:justify-between gap-2">
              <span className="text-gray-300 font-medium">Ticker:</span>
              <span className="text-yellow-400 font-bold break-words">{fundInfo.ticker || 'N/A'}</span>
            </div>
            
            <div className="flex flex-col sm:flex-row sm:justify-between gap-2">
              <span className="text-gray-300 font-medium">CNPJ:</span>
              <span className="text-gray-200 text-sm break-all">{fundInfo.cnpj || 'N/A'}</span>
            </div>
            
            <div className="flex flex-col sm:flex-row sm:justify-between gap-2">
              <span className="text-gray-300 font-medium">Administrador:</span>
              <span className="text-gray-200 text-sm break-words sm:text-right">{fundInfo.administrador || 'N/A'}</span>
            </div>
            
            <div className="flex flex-col sm:flex-row sm:justify-between gap-2">
              <span className="text-gray-300 font-medium">Gestor:</span>
              <span className="text-gray-200 text-sm break-words sm:text-right">{fundInfo.gestor || 'N/A'}</span>
            </div>
            
            <div className="flex flex-col sm:flex-row sm:justify-between gap-2">
              <span className="text-gray-300 font-medium">Segmento:</span>
              <span className="bg-green-800 text-green-300 px-3 py-1 rounded-full text-xs font-semibold break-words">
                {fundInfo.segmento || 'N/A'}
              </span>
            </div>
            
            <div className="flex flex-col sm:flex-row sm:justify-between gap-2">
              <span className="text-gray-300 font-medium">Data Relatório:</span>
              <span className="text-gray-200 text-sm">{fundInfo.data_relatorio || 'N/A'}</span>
            </div>
          </div>
        </div>

        {/* Key Indicators */}
        <div className="bg-gray-700 p-4 sm:p-6 rounded-lg space-y-4">
          <h3 className="text-lg sm:text-xl text-green-400 flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5" />
            Indicadores-Chave
          </h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Dividend Yield */}
            <div className="bg-gradient-to-r from-green-700 to-green-600 p-4 rounded-lg text-center">
              <div className="text-green-200 text-sm mb-1">Dividend Yield</div>
              <div className="text-white text-xl sm:text-2xl font-bold break-words">
                {formatValue(financialMetrics.dividend_yield, true)}
              </div>
            </div>
            
            {/* P/VP */}
            <div className="bg-gradient-to-r from-blue-700 to-blue-600 p-4 rounded-lg text-center">
              <div className="text-blue-200 text-sm mb-1">P/VP</div>
              <div className="text-white text-xl sm:text-2xl font-bold break-words">
                {formatValue(financialMetrics.p_vp)}
              </div>
            </div>
            
            {/* Taxa Vacância */}
            <div className="bg-gradient-to-r from-red-700 to-red-600 p-4 rounded-lg text-center">
              <div className="text-red-200 text-sm mb-1">Taxa Vacância</div>
              <div className="text-white text-xl sm:text-2xl font-bold break-words">
                {formatValue(financialMetrics.taxa_vacancia, true)}
              </div>
            </div>
          </div>
        </div>

        {/* Financial Metrics */}
        <div className="bg-gray-700 p-4 sm:p-6 rounded-lg">
          <h3 className="text-lg sm:text-xl text-yellow-400 flex items-center gap-2 mb-6">
            <DollarSign className="w-5 h-5" />
            Métricas Financeiras
          </h3>
          
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:justify-between gap-2 p-3 border-b border-gray-600">
              <span className="text-gray-300">Receitas de Aluguéis</span>
              <span className="text-green-400 font-semibold break-words">
                {formatValue(financialMetrics.receitas_alugueis, false, true)}
              </span>
            </div>
            
            <div className="flex flex-col sm:flex-row sm:justify-between gap-2 p-3 border-b border-gray-600">
              <span className="text-gray-300">Despesas Operacionais</span>
              <span className="text-red-400 font-semibold break-words">
                {formatValue(financialMetrics.despesas_operacionais, false, true)}
              </span>
            </div>
            
            <div className="flex flex-col sm:flex-row sm:justify-between gap-2 p-3 border-b border-gray-600">
              <span className="text-gray-300">Resultado Líquido</span>
              <span className="text-blue-400 font-semibold break-words">
                {formatValue(financialMetrics.resultado_liquido, false, true)}
              </span>
            </div>
            
            <div className="flex flex-col sm:flex-row sm:justify-between gap-2 p-3 border-b border-gray-600">
              <span className="text-gray-300">Patrimônio Líquido</span>
              <span className="text-purple-400 font-semibold break-words">
                {formatValue(financialMetrics.patrimonio_liquido, false, true, true)}
              </span>
            </div>
            
            <div className="flex flex-col sm:flex-row sm:justify-between gap-2 p-3 border-b border-gray-600">
              <span className="text-gray-300">VP por Cota</span>
              <span className="text-yellow-400 font-semibold break-words">
                {formatValue(financialMetrics.vp_por_cota, false, true)}
              </span>
            </div>
            
            <div className="flex flex-col sm:flex-row sm:justify-between gap-2 p-3">
              <span className="text-gray-300">Número de Cotas</span>
              <span className="text-gray-200 font-semibold break-words">
                {formatValue(financialMetrics.numero_cotas)}
              </span>
            </div>
          </div>
        </div>

        {/* Detailed Analysis */}
        <div className="bg-gray-700 p-4 sm:p-6 rounded-lg">
          <h3 className="text-lg sm:text-xl text-purple-400 flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5" />
            Análise Detalhada
          </h3>
          <div className="text-gray-200 text-sm sm:text-base leading-relaxed whitespace-pre-wrap break-words overflow-wrap-anywhere">
            {detailedAnalysis}
          </div>
        </div>

        {/* Segment Analysis */}
        {segmentAnalysis.segmento && (
          <div className="bg-gradient-to-r from-red-800 to-red-700 p-4 sm:p-6 rounded-lg">
            <h3 className="text-lg sm:text-xl text-white flex items-center gap-2 mb-6">
              <Target className="w-5 h-5" />
              Análise do Segmento: {segmentAnalysis.segmento?.toUpperCase()}
            </h3>
            
            <div className="space-y-6">
              {/* Métricas-Chave */}
              <div className="bg-black bg-opacity-20 p-4 rounded-lg">
                <h4 className="text-red-200 font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Métricas-Chave
                </h4>
                <div className="space-y-2">
                  {segmentAnalysis.metricas_chave?.map((metrica: string, index: number) => (
                    <div key={index} className="text-red-100 text-sm break-words">
                      • {metrica}
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Principais Riscos */}
              <div className="bg-black bg-opacity-20 p-4 rounded-lg">
                <h4 className="text-red-200 font-semibold mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4" />
                  Principais Riscos
                </h4>
                <div className="space-y-2">
                  {segmentAnalysis.riscos_principais?.map((risco: string, index: number) => (
                    <div key={index} className="text-red-100 text-sm break-words">
                      • {risco}
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Pontos de Atenção */}
              <div className="bg-black bg-opacity-20 p-4 rounded-lg">
                <h4 className="text-red-200 font-semibold mb-3 flex items-center gap-2">
                  <Eye className="w-4 h-4" />
                  Pontos de Atenção
                </h4>
                <div className="space-y-2">
                  {segmentAnalysis.pontos_atencao?.map((ponto: string, index: number) => (
                    <div key={index} className="text-red-100 text-sm break-words">
                      • {ponto}
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Análise Específica */}
              <div className="bg-black bg-opacity-20 p-4 rounded-lg">
                <h4 className="text-red-200 font-semibold mb-3 flex items-center gap-2">
                  <Brain className="w-4 h-4" />
                  Análise Específica
                </h4>
                <div className="text-red-100 text-sm leading-relaxed whitespace-pre-wrap break-words overflow-wrap-anywhere">
                  {segmentAnalysis.analise_especifica}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center bg-gray-600 p-4 rounded-lg">
          <div className="text-green-400 text-sm font-semibold flex items-center justify-center gap-2">
            <CheckCircle className="w-4 h-4" />
            Análise gerada automaticamente com base no relatório oficial do fundo
          </div>
        </div>
      </div>
    </div>
  );
}