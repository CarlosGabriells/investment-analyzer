'use client';

import React, { useState, useMemo } from 'react';
import { Star, Brain, Tag, User, TrendingUp, DollarSign } from 'lucide-react';
import { Button } from './Button';
import { useApp } from '@/contexts/AppContext';
import AiReport from './AiReport';
import { Input } from './Input';
import './styles.css';


export default function AnalysisTable() {
  const { analyses } = useApp();
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<'dividend_yield' | 'p_vp' | 'nome'>('dividend_yield');
  const [analysis, setAnalysis] = useState('');

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
          // Usar análise formatada para humanos se disponível
          let analysisText = '';
          
          if (analysis.human_readable_analysis) {
            analysisText = analysis.human_readable_analysis;
          } else if (typeof analysis.detailed_analysis === 'string') {
            analysisText = analysis.detailed_analysis;
          } else {
            analysisText = JSON.stringify(analysis.detailed_analysis, null, 2);
          }
          
          setAnalysis(analysisText);
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
      <div className='flex flex-col lg:flex-col items-start justify-center max-w-[1440px] m-auto gap-4 p-0 sm:p-8 overflow-hidden'>
        <h2 className='text-[32px] m-0 p-4 sm:p-0 text-white'>Análises de FIIs</h2>
        <p className='text-fontGray pb-8 p-4 sm:p-0'>
          Visualize e compare as análises dos Fundos de Investimento Imobiliário. 
          Use os filtros para encontrar e ordenar os FIIs conforme seus critérios de investimento.
        </p>

        {/* SEARCH AND SORT */}
        <div className="flex items-start gap-4 flex-col md:flex-row md:items-center px-4 sm:px-0">
          <Input
            placeholder="Buscar por nome ou ticker"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-borderGray min-w-[260px] md:min-w-[350px]"
          />
          
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="bg-borderGray text-white px-3 py-2 rounded-md border border-gray-600 focus:border-blue-500"
          >
            <option value="dividend_yield">Dividend Yield (maior)</option>
            <option value="p_vp">P/VP (menor)</option>
            <option value="nome">Nome (A-Z)</option>
          </select>
        </div>

        <div className="bg-bgTable flex flex-col items-start justify-start sm:rounded-[8px] p-4 w-[100%] overflow-x-auto mb-4">
          <table className="w-full">
            <thead className="pb-2 border-b-[1px] w-[100%] border-borderGray">
              <tr className='flex justify-between gap-2 md:gap-4 sm:px-2 min-w-[600px]'>
                <th className="flex flex-row md:gap-2 items-center text-fontWhite font-roboto font-bold text-[12px] md:text-[16px] w-[40px]">
                  <Star className='w-[14px]' />Rank
                </th>
                <th className="flex flex-row md:gap-2 items-center text-fontWhite font-roboto font-bold text-[12px] md:text-[16px] w-[120px] md:w-[180px]">
                  <User className='w-[14px]' />Nome
                </th>
                <th className="flex flex-row md:gap-2 items-center text-fontWhite font-roboto font-bold text-[12px] md:text-[16px] w-[60px]">
                  <Tag className='w-[14px]' />Ticker
                </th>
                <th className="flex flex-row md:gap-2 items-center text-fontWhite font-roboto font-bold text-[12px] md:text-[16px] w-[80px]">
                  <TrendingUp className='w-[14px]' />DY%
                </th>
                <th className="flex flex-row md:gap-2 items-center text-fontWhite font-roboto font-bold text-[12px] md:text-[16px] w-[60px]">
                  <DollarSign className='w-[14px]' />P/VP
                </th>
                <th className="flex flex-row md:gap-2 items-center justify-center text-fontWhite font-roboto font-bold text-[12px] md:text-[16px] w-[80px]">
                  <Brain className='w-[14px]' />Análise
                </th>
              </tr>
            </thead>
            <tbody className="flex flex-col w-full gap-2 pt-4">
              {sortedAndFilteredData.map((item) => (
                <tr key={`${item.ticker}-${item.ranking}`} className="tr-custom border-b-[1px] w-[100%] border-borderGray p-2 flex justify-between items-center hover:bg-borderGray transition-colors duration-300 ease-in-out rounded-[8px] min-w-[600px]">
                  <td className="text-center text-fontWhite font-bold w-[40px]">#{item.ranking}</td>
                  <td className="text-start text-fontGray w-[120px] md:w-[180px] truncate" title={item.nome}>
                    {item.nome}
                  </td>
                  <td className="w-[60px] text-center text-fontWhite font-semibold">{item.ticker}</td>
                  <td className="w-[80px] text-center text-green-400 font-semibold">
                    {formatDisplayValue(item.analysis.financial_metrics.dividend_yield, true)}
                  </td>
                  <td className="w-[60px] text-center text-blue-400 font-semibold">
                    {formatDisplayValue(item.analysis.financial_metrics.p_vp)}
                  </td>
                  <td className='w-[80px] text-center'>
                    <Button 
                      onClick={item.func} 
                      className='buttom-custom flex flex-row items-center text-fontGray gap-1 px-2 py-1 text-sm'
                    >
                      <Brain className="text-fontGray transition w-4 h-4" />
                      <span className='hidden sm:block'>Ver</span>
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <AiReport text={analysis} />
      </div>
    </div>
  );
}