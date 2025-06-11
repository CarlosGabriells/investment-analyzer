import { SquareChartGantt } from 'lucide-react';

type ExtraInfoItem = {
  label: string;
  value: string;
};

type MoreInfoReportsProps = {
  extraInfoData?: ExtraInfoItem[]; // Deixa como opcional também
};

const dataPlaceholder: ExtraInfoItem[] = [
  { label: 'Ticket', value: 'Faça uma análise' },
  { label: 'Nome', value: 'Faça uma análise' },
  { label: 'CNPJ', value: 'Faça uma análise' },
  { label: 'Data', value: 'Faça uma análise' },
];

export default function MoreInfoReports({ extraInfoData }: MoreInfoReportsProps) {
  const dataToRender = extraInfoData && extraInfoData.length > 0 ? extraInfoData : dataPlaceholder;

  return (
    <div className="flex flex-col bg-bgTable sm:rounded-[8px] p-4 w-[100%] lg:w-[50%]">
      <p className="flex flex-row gap-2 items-center text-[20px] pb-2 border-b-[1px] w-[100%] border-borderGray font-bold">
        <SquareChartGantt />
        Detalhes
      </p>
      <div className="flex flex-row gap-4 flex-wrap pt-4">
        {dataToRender.map((item, idx) => (
          <div key={idx} className="w-[48%]">
            <p className="pb-2 text-fontGray font-bold">{item.label}</p>
            <div className="text-fontLightGray bg-bgTable">{item.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
