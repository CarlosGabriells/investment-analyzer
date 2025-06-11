'use client';

import React, { useState, useMemo } from 'react';
import { Star, Brain, Tag, User, FilePlus2 } from 'lucide-react';
import { Button } from './Button';
import { FundData } from '@/utils/types';
import AiReport from './AiReport';
import MoreInfoReports from './MoreInfoReports';
import { Input } from './Input';
import './styles.css';
import { UploadButton } from './ButtonFile';

type Props = {
  data: FundData;
};

type ExtraInfoItem = {
  label: string;
  value: string;
};

export default function TableRanking({ data }: Props) {
  const [search, setSearch] = useState('');
  const [rankingFilter, setRankingFilter] = useState('');
  const [analysis, setAnalysis] = useState('');
  const [extraInfo, setExtraInfoData] = useState<ExtraInfoItem[]>([]);

  const jsonTableData = [
    {
      ranking: 1,
      nome: data.fund_info.nome,
      ticker: data.fund_info.ticker,
      relatorio: data.fund_info.data_relatorio,
      func: () => {
        setAnalysis(data.investment_analysis);
        setExtraInfoData([
          {
            label: 'Ticket',
            value: data.fund_info.ticker
          },
          {
            label: 'Nome',
            value: data.fund_info.nome
          },
          {
            label: 'CNPJ',
            value: data.fund_info.cnpj
          },
          {
            label: 'Data',
            value: data.fund_info.data_relatorio
          }
        ]);
      }
    },
  ];

  const filteredData = useMemo(() => {
    return jsonTableData.filter((item) => {
      const matchesName = item.nome.toLowerCase().includes(search.toLowerCase());
      const matchesRanking = rankingFilter ? item.ranking === Number(rankingFilter) : true;
      return matchesName && matchesRanking;
    });
  }, [search, rankingFilter, data]);

  return (
    <div>
      <div className='flex flex-col lg:flex-col items-start justify-center max-w-[1440px] m-auto gap-4 p-0 sm:p-8 overflow-hidden'>
        <h2 className='text-[32px] m-0 p-4 sm:p-0'>Titulo</h2>
        <p className='text-fontGray pb-8 p-4 sm:p-0'>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Ab soluta blanditiis, voluptas dignissimos adipisci aliquam qui, autem est dicta omnis perferendis fugit impedit possimus nam animi laboriosam tenetur expedita hic! Lorem ipsum dolor sit amet consectetur, adipisicing elit. Veniam, aperiam recusandae! Quo sed cupiditate dolorem. Itaque iste porro quisquam necessitatibus fugit est cum ab a? Quis temporibus pariatur dolor hic!</p>

        {/* SEARCH */}
        <div className="flex items-start gap-4 flex-col md:flex-row md:items-center px-4 sm:px-0">
          <Input
            placeholder="Buscar pelo nome do ativo"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-borderGray min-w-[260px] md:min-w-[350px]"
          />
          <UploadButton />
        </div>

        <div className='w-[100%] flex flex-col gap-4 justify-center items-start lg:flex-row'>
          <table className="bg-bgTable flex flex-col items-start justify-start sm:rounded-[8px] p-4 w-[100%] lg:w-[50%]">
            <thead className="pb-2 border-b-[1px] w-[100%] border-borderGray">
              <tr className='flex justify-between gap-2 md:gap-16 sm:px-2'>
                <th className="flex flex-row md:gap-2 items-center text-fontWhite font-roboto font-bold text-[14px] md:text-[20px] w-[150px] sm:w-[180px] md:w-[230px] lg:w-[270px]"><User className='w-[18px]' />Nome</th>
                <th className="flex flex-row md:gap-2 items-center text-fontWhite font-roboto font-bold text-[14px] md:text-[20px] w-[60px] sm:w-[100px]"><Tag className='w-[18px]' />Ticker</th>
                <th className="flex flex-row md:gap-2 items-center justify-center text-fontWhite font-roboto font-bold text-[14px] md:text-[20px] w-[56px] sm:w-[140px]"><Brain /><span className='hidden sm:block'>Relatório IA</span></th>
              </tr>
            </thead>
            <tbody className="flex flex-col w-full gap-4 pt-4">
              {filteredData.map((item) => (
                <tr key={item.ranking} className="tr-custom border-b-[1px] w-[100%] border-borderGray sm:p-2 flex justify-between items-center hover:bg-borderGray transition-colors duration-300 ease-in-out rounded-[8px] gap-1">
                  <td className="text-start text-fontGray w-[150px] sm:w-[180px] md:w-[230px] lg:w-[270px]">{item.nome}</td>
                  <td className="sm:w-[100px] text-center text-fontGray">{item.ticker}</td>
                  <td className='sm:w-[140px] text-center'>
                    <Button onClick={item.func} className='buttom-custom flex flex-row items-center text-fontGray gap-2'>
                      <Brain className="text-fontGray transition sm:hidden" />
                      <span className='hidden sm:block'>Análise IA</span>
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <MoreInfoReports extraInfoData={extraInfo} />
        </div>

        <AiReport text={analysis} />
      </div>
    </div>
  );
}
