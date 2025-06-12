'use client';

import React from 'react';
import { BarChart3, FileText, Clock } from 'lucide-react';
import { useApp } from '@/contexts/AppContext';

export default function SessionStatus() {
  const { sessionId, analyses, isLoading } = useApp();

  if (!sessionId) return null;

  const totalAnalyses = analyses.length;
  const avgDividendYield = totalAnalyses > 0 
    ? analyses.reduce((sum, a) => sum + (Number(a.financial_metrics.dividend_yield) || 0), 0) / totalAnalyses
    : 0;

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-600 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-400" />
            <span className="text-white font-medium">{totalAnalyses}</span>
            <span className="text-gray-400 text-sm">FII{totalAnalyses !== 1 ? 's' : ''} analisado{totalAnalyses !== 1 ? 's' : ''}</span>
          </div>
          
          {totalAnalyses > 0 && (
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-green-400" />
              <span className="text-white font-medium">{avgDividendYield.toFixed(2)}%</span>
              <span className="text-gray-400 text-sm">DY médio</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {isLoading && (
            <div className="flex items-center gap-2 text-blue-400">
              <Clock className="w-4 h-4 animate-pulse" />
              <span className="text-sm">Analisando...</span>
            </div>
          )}
          <div className="text-xs text-gray-500">
            Sessão: {sessionId.slice(-8)}
          </div>
        </div>
      </div>

      {totalAnalyses > 1 && (
        <div className="mt-3 pt-3 border-t border-gray-700">
          <div className="flex flex-wrap gap-2">
            {analyses.slice(0, 5).map((analysis, index) => (
              <div
                key={index}
                className="flex items-center gap-1 bg-gray-700 px-2 py-1 rounded text-xs"
              >
                <span className="text-white font-medium">{analysis.fund_info.ticker}</span>
                <span className="text-gray-400">
                  {analysis.fund_info.segmento !== 'Não informado' ? analysis.fund_info.segmento : 'FII'}
                </span>
              </div>
            ))}
            {totalAnalyses > 5 && (
              <div className="flex items-center bg-gray-700 px-2 py-1 rounded text-xs text-gray-400">
                +{totalAnalyses - 5} mais
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}