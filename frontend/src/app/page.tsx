import { getFundData } from "@/utils/useDataJson";
import TableRanking from "@/components/TableDinamic";
import { Button } from "@/components/Button";

export default function Home() {
  const data = getFundData();

  return (
    <div className="bg-bgDark h-[100%] min-h-[100vh] overflow-hidden">
      <TableRanking data={data}/>
    </div>
  );
}
