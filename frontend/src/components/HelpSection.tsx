'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, HelpCircle, FileText, TrendingUp, BarChart3 } from 'lucide-react';

export default function HelpSection() {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-600 mb-8">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-4 flex items-center justify-between text-white hover:bg-gray-700 transition-colors rounded-t-lg"
      >
        <div className="flex items-center gap-2">
          <HelpCircle className="w-5 h-5" />
          <span className="font-medium">Como usar o FII Analyzer</span>
        </div>
        {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
      </button>
      
      {isExpanded && (
        <div className="px-4 pb-4 text-gray-300">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div className="flex flex-col items-center text-center p-4 bg-gray-700/50 rounded-lg">
              <FileText className="w-8 h-8 text-blue-400 mb-2" />
              <h3 className="font-semibold text-white mb-2">1. Upload do PDF</h3>
              <p className="text-sm">
                Faça upload do relatório mensal ou trimestral do FII em formato PDF. 
                Aceita relatórios de todos os tipos de FII.
              </p>
            </div>
            
            <div className="flex flex-col items-center text-center p-4 bg-gray-700/50 rounded-lg">
              <TrendingUp className="w-8 h-8 text-green-400 mb-2" />
              <h3 className="font-semibold text-white mb-2">2. Análise Automática</h3>
              <p className="text-sm">
                A IA extrai automaticamente métricas financeiras, identifica o segmento 
                e calcula indicadores como P/VP e Dividend Yield.
              </p>
            </div>
            
            <div className="flex flex-col items-center text-center p-4 bg-gray-700/50 rounded-lg">
              <BarChart3 className="w-8 h-8 text-purple-400 mb-2" />
              <h3 className="font-semibold text-white mb-2">3. Compare e Analise</h3>
              <p className="text-sm">
                Compare múltiplos FIIs, veja rankings dinâmicos e obtenha 
                análises específicas por segmento (Shopping, Logística, etc.).
              </p>
            </div>
          </div>
          
          <div className="mt-4 p-3 bg-blue-900/20 border border-blue-600/30 rounded-lg">
            <h4 className="font-semibold text-blue-300 mb-2">💡 Dicas de Uso:</h4>
            <ul className="text-sm space-y-1">
              <li>• Use relatórios oficiais dos FIIs para melhores resultados</li>
              <li>• Faça upload de vários FIIs para comparar performance</li>
              <li>• A análise considera o segmento específico de cada FII</li>
              <li>• Rankings são atualizados automaticamente a cada nova análise</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}