'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Award, Loader2, RefreshCw } from 'lucide-react';
import { Button } from './Button';
import { useApp } from '@/contexts/AppContext';
import { apiService, RankingResult } from '@/services/api';

export default function DynamicRanking() {
  const { sessionId, analyses } = useApp();
  const [activeTab, setActiveTab] = useState<'dividend_yield' | 'pvp'>('dividend_yield');
  const [rankingData, setRankingData] = useState<RankingResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadRanking = async (criteria: 'dividend_yield' | 'pvp') => {
    if (!sessionId || analyses.length === 0) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await apiService.getRanking(criteria, sessionId);
      setRankingData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar ranking');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (sessionId && analyses.length > 0) {
      loadRanking(activeTab);
    }
  }, [activeTab, sessionId, analyses.length]);

  const handleTabChange = (tab: 'dividend_yield' | 'pvp') => {
    setActiveTab(tab);
    setRankingData(null);
  };

  const handleRefresh = () => {
    loadRanking(activeTab);
  };

  if (analyses.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-600">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Award className="w-5 h-5" />
          Rankings Dinâmicos
        </h3>
        <div className="text-center py-4">
          <Award className="w-12 h-12 text-gray-500 mx-auto mb-3" />
          <p className="text-gray-400 mb-2">
            Adicione FIIs para ver rankings
          </p>
          <p className="text-gray-500 text-sm">
            Com 2+ FIIs você poderá comparar por Dividend Yield e P/VP
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-600">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Award className="w-5 h-5" />
          Rankings Dinâmicos
        </h3>
        <Button
          onClick={handleRefresh}
          variant="outline"
          size="sm"
          disabled={isLoading}
          className="flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          Atualizar
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => handleTabChange('dividend_yield')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2
            ${activeTab === 'dividend_yield'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
        >
          <TrendingUp className="w-4 h-4" />
          Dividend Yield
        </button>
        <button
          onClick={() => handleTabChange('pvp')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2
            ${activeTab === 'pvp'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
        >
          <TrendingDown className="w-4 h-4" />
          P/VP (Menor é Melhor)
        </button>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
          <span className="ml-2 text-gray-400">Carregando ranking...</span>
        </div>
      ) : error ? (
        <div className="text-center py-4">
          <p className="text-red-400 mb-2">{error}</p>
          <Button onClick={handleRefresh} variant="outline" size="sm">
            Tentar novamente
          </Button>
        </div>
      ) : rankingData ? (
        <div className="space-y-2">
          {rankingData.cached && (
            <p className="text-xs text-yellow-400 mb-2">📁 Dados do cache</p>
          )}
          
          {rankingData.ranking.map((item, index) => (
            <div
              key={item.ticker}
              className={`flex items-center justify-between p-3 rounded-lg border
                ${index === 0
                  ? 'bg-yellow-900/20 border-yellow-600/30'
                  : index === 1
                  ? 'bg-gray-600/20 border-gray-500/30'
                  : index === 2
                  ? 'bg-orange-900/20 border-orange-600/30'
                  : 'bg-gray-700/20 border-gray-600/30'
                }`}
            >
              <div className="flex items-center gap-3">
                <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold
                  ${index === 0
                    ? 'bg-yellow-600 text-yellow-100'
                    : index === 1
                    ? 'bg-gray-500 text-gray-100'
                    : index === 2
                    ? 'bg-orange-600 text-orange-100'
                    : 'bg-gray-600 text-gray-100'
                  }`}
                >
                  {index + 1}
                </div>
                <div>
                  <p className="text-white font-medium">{item.ticker}</p>
                  <p className="text-gray-400 text-sm truncate max-w-[200px]">
                    {item.nome}
                  </p>
                </div>
              </div>
              
              <div className="text-right">
                <p className={`font-semibold
                  ${activeTab === 'dividend_yield'
                    ? 'text-green-400'
                    : 'text-blue-400'
                  }`}
                >
                  {activeTab === 'dividend_yield'
                    ? `${Number(item.valor || 0).toFixed(2)}%`
                    : Number(item.valor || 0).toFixed(2)
                  }
                </p>
                <p className="text-gray-500 text-xs">
                  #{item.posicao}
                </p>
              </div>
            </div>
          ))}
          
          {rankingData.ranking.length === 0 && (
            <p className="text-gray-400 text-center py-4">
              Nenhum FII encontrado para este critério
            </p>
          )}
        </div>
      ) : (
        <p className="text-gray-400 text-center py-4">
          Selecione um critério para ver o ranking
        </p>
      )}
    </div>
  );
}