'use client'

import React, { useState, useMemo } from 'react';
import { Star, Brain } from 'lucide-react';
import { Input } from './Input';
import { Button } from './Button';

const sampleData = [
  { ranking: 1, nome: 'Ações XPTO', func: () => alert('Executando função para Ações XPTO') },
  { ranking: 2, nome: 'ETF ABC', func: () => alert('Executando função para ETF ABC') },
  { ranking: 3, nome: 'Cripto XYZ', func: () => alert('Executando função para Cripto XYZ') },
];

export default function TableRanking() {
  const [favorites, setFavorites] = useState<number[]>([]);
  const [search, setSearch] = useState('');
  const [rankingFilter, setRankingFilter] = useState('');

  const filteredData = useMemo(() => {
    return sampleData.filter((item) => {
      const matchesName = item.nome.toLowerCase().includes(search.toLowerCase());
      const matchesRanking = rankingFilter ? item.ranking === Number(rankingFilter) : true;
      return matchesName && matchesRanking;
    });
  }, [search, rankingFilter]);

  const toggleFavorite = (ranking: number) => {
    setFavorites((prev) =>
      prev.includes(ranking) ? prev.filter((r) => r !== ranking) : [...prev, ranking]
    );
  };

  return (
    <div className="">
      <div className="flex items-center gap-4">
        <Input
          placeholder="Buscar por nome..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-sm"
        />
      </div>

      <table className="bg-bgTable border-borderGray border-[1px] border-solid flex flex-col items-start justify-start rounded-[8px] p-4">
        <thead className="py-4 px-8 mb-4 bg-tableHead w-[100%] rounded-[8px]">
          <tr className='flex gap-16'>
            <th className="text-fontWhite font-roboto tracking-[1px] font-normal">Fav</th>
            <th className="text-fontWhite font-roboto tracking-[1px] font-normal">Ranking</th>
            <th className="text-fontWhite font-roboto tracking-[1px] font-normal">Nome</th>
            <th className="text-fontWhite font-roboto tracking-[1px] font-normal">Relatorio</th>
          </tr>
        </thead>
        <tbody className='flex flex-col p-4 w-[100%] gap-8'>
          {filteredData.map((item) => (
            <tr key={item.ranking} className="border-b-[1px] w-[100%] border-borderGray pb-2 flex justify-between">
              <td className="">
                <button onClick={() => toggleFavorite(item.ranking)}>
                  {favorites.includes(item.ranking) ? (
                    <Star className="text-yellow-500" />
                  ) : (
                    <Star className="text-gray-400" />
                  )}
                </button>
              </td>
              <td className="">{item.ranking}</td>
              <td className="">{item.nome}</td>
              <td className="">
                <Button onClick={item.func}><Brain className="text-gray-400" /></Button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
