'use client';

import React, { useState, useMemo } from 'react';
import { Star, Brain, Tag, User, TrendingUp, DollarSign } from 'lucide-react';
import { Button } from './Button';
import { useApp } from '@/contexts/AppContext';
import DetailedAnalysis from './DetailedAnalysis';
import { Input } from './Input';
import './styles.css';


export default function AnalysisTable() {
  const { analyses } = useApp();
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<'dividend_yield' | 'p_vp' | 'nome'>('dividend_yield');
  const [selectedAnalysis, setSelectedAnalysis] = useState<any>(null);

  // Helper function to safely convert to number
  const toNumber = (value: any): number => {
    if (value === null || value === undefined || value === "N/A" || value === "Não informado") {
      return 0;
    }
    const num = typeof value === 'string' ? parseFloat(value) : Number(value);
    return isNaN(num) ? 0 : num;
  };

  // Helper to format display values
  const formatDisplayValue = (value: any, isPercentage = false): string => {
    if (value === null || value === undefined || value === "N/A" || value === "Não informado") {
      return "N/A";
    }
    const num = toNumber(value);
    if (num === 0) return "N/A";
    
    if (isPercentage) return `${num.toFixed(2)}%`;
    return num.toFixed(2);
  };

  const tableData = useMemo(() => {
    return analyses.map((analysis, index) => {
      return {
        ranking: index + 1,
        nome: analysis.fund_info.nome || 'N/A',
        ticker: analysis.fund_info.ticker || 'N/A',
        dividend_yield: toNumber(analysis.financial_metrics.dividend_yield),
        p_vp: toNumber(analysis.financial_metrics.p_vp),
        valor_cota: toNumber(analysis.financial_metrics.valor_cota),
        relatorio: analysis.fund_info.data_relatorio || 'N/A',
        analysis: analysis,
        func: () => {
          setSelectedAnalysis(analysis);
        }
      };
    });
  }, [analyses]);

  const sortedAndFilteredData = useMemo(() => {
    let filtered = tableData.filter((item) => {
      const matchesName = item.nome.toLowerCase().includes(search.toLowerCase()) ||
                         item.ticker.toLowerCase().includes(search.toLowerCase());
      return matchesName;
    });

    // Sort data
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'dividend_yield':
          return Number(b.dividend_yield) - Number(a.dividend_yield); // Descending
        case 'p_vp':
          return Number(a.p_vp) - Number(b.p_vp); // Ascending (lower P/VP is better)
        case 'nome':
          return String(a.nome).localeCompare(String(b.nome));
        default:
          return 0;
      }
    });

    // Update rankings after sorting
    return filtered.map((item, index) => ({
      ...item,
      ranking: index + 1
    }));
  }, [tableData, search, sortBy]);

  if (analyses.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-400">Nenhuma análise disponível. Faça upload de um PDF para começar.</p>
      </div>
    );
  }

  return (
    <div>
      <div className='flex flex-col items-start justify-center max-w-[1440px] m-auto gap-4 px-4 sm:px-8 overflow-hidden'>
        <h2 className='text-2xl sm:text-[32px] m-0 text-white'>Análises de FIIs</h2>
        <p className='text-fontGray pb-4 sm:pb-8 text-sm sm:text-base'>
          Visualize e compare as análises dos Fundos de Investimento Imobiliário. 
          Use os filtros para encontrar e ordenar os FIIs conforme seus critérios de investimento.
        </p>

        {/* SEARCH AND SORT */}
        <div className="flex items-start gap-4 flex-col md:flex-row md:items-center w-full">
          <Input
            placeholder="Buscar por nome ou ticker"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-borderGray w-full md:min-w-[350px] md:w-auto"
          />
          
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="bg-borderGray text-white px-3 py-2 rounded-md border border-gray-600 focus:border-blue-500 w-full md:w-auto"
          >
            <option value="dividend_yield">Dividend Yield (maior)</option>
            <option value="p_vp">P/VP (menor)</option>
            <option value="nome">Nome (A-Z)</option>
          </select>
        </div>

        <div className="bg-bgTable flex flex-col items-start justify-start rounded-[8px] p-2 sm:p-4 w-full overflow-x-auto mb-4">
          <table className="w-full">
            <thead className="pb-2 border-b-[1px] w-full border-borderGray">
              <tr className='flex justify-between gap-1 sm:gap-2 md:gap-4 px-1 sm:px-2 min-w-[600px]'>
                <th className="flex flex-row gap-1 md:gap-2 items-center text-fontWhite font-roboto font-bold text-[10px] sm:text-[12px] md:text-[16px] w-[35px] sm:w-[40px]">
                  <Star className='w-[12px] sm:w-[14px]' /><span className="hidden sm:inline">Rank</span>
                </th>
                <th className="flex flex-row gap-1 md:gap-2 items-center text-fontWhite font-roboto font-bold text-[10px] sm:text-[12px] md:text-[16px] w-[100px] sm:w-[120px] md:w-[180px]">
                  <User className='w-[12px] sm:w-[14px]' /><span className="hidden sm:inline">Nome</span>
                </th>
                <th className="flex flex-row gap-1 md:gap-2 items-center text-fontWhite font-roboto font-bold text-[10px] sm:text-[12px] md:text-[16px] w-[50px] sm:w-[60px]">
                  <Tag className='w-[12px] sm:w-[14px]' /><span className="hidden sm:inline">Ticker</span>
                </th>
                <th className="flex flex-row gap-1 md:gap-2 items-center text-fontWhite font-roboto font-bold text-[10px] sm:text-[12px] md:text-[16px] w-[60px] sm:w-[80px]">
                  <TrendingUp className='w-[12px] sm:w-[14px]' />DY%
                </th>
                <th className="flex flex-row gap-1 md:gap-2 items-center text-fontWhite font-roboto font-bold text-[10px] sm:text-[12px] md:text-[16px] w-[50px] sm:w-[60px]">
                  <DollarSign className='w-[12px] sm:w-[14px]' />P/VP
                </th>
                <th className="flex flex-row gap-1 md:gap-2 items-center justify-center text-fontWhite font-roboto font-bold text-[10px] sm:text-[12px] md:text-[16px] w-[60px] sm:w-[80px]">
                  <Brain className='w-[12px] sm:w-[14px]' /><span className="hidden sm:inline">Análise</span>
                </th>
              </tr>
            </thead>
            <tbody className="flex flex-col w-full gap-2 pt-4">
              {sortedAndFilteredData.map((item) => (
                <tr key={`${item.ticker}-${item.ranking}`} className="tr-custom border-b-[1px] w-full border-borderGray p-1 sm:p-2 flex justify-between items-center hover:bg-borderGray transition-colors duration-300 ease-in-out rounded-[8px] min-w-[600px]">
                  <td className="text-center text-fontWhite font-bold w-[35px] sm:w-[40px] text-[10px] sm:text-sm">#{item.ranking}</td>
                  <td className="text-start text-fontGray w-[100px] sm:w-[120px] md:w-[180px] truncate text-[10px] sm:text-sm" title={item.nome}>
                    {item.nome}
                  </td>
                  <td className="w-[50px] sm:w-[60px] text-center text-fontWhite font-semibold text-[10px] sm:text-sm">{item.ticker}</td>
                  <td className="w-[60px] sm:w-[80px] text-center text-green-400 font-semibold text-[10px] sm:text-sm">
                    {formatDisplayValue(item.analysis.financial_metrics.dividend_yield, true)}
                  </td>
                  <td className="w-[50px] sm:w-[60px] text-center text-blue-400 font-semibold text-[10px] sm:text-sm">
                    {formatDisplayValue(item.analysis.financial_metrics.p_vp)}
                  </td>
                  <td className='w-[60px] sm:w-[80px] text-center'>
                    <Button 
                      onClick={item.func} 
                      className='buttom-custom flex flex-row items-center text-fontGray gap-1 px-1 sm:px-2 py-1 text-xs sm:text-sm'
                    >
                      <Brain className="text-fontGray transition w-3 h-3 sm:w-4 sm:h-4" />
                      <span className='hidden sm:block'>Ver</span>
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <DetailedAnalysis analysisData={selectedAnalysis} />
      </div>
    </div>
  );
}