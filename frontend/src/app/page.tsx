import PDFUpload from "@/components/PDFUpload";
import AnalysisTable from "@/components/AnalysisTable";
import HelpSection from "@/components/HelpSection";
import SessionStatus from "@/components/SessionStatus";

export default function Home() {
  return (
    <div className="bg-bgDark min-h-screen">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8">
        <header className="text-center mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-2">
            📊 FII Analyzer
          </h1>
          <p className="text-gray-400 text-base sm:text-lg mb-2">
            Análise inteligente de Fundos de Investimento Imobiliário
          </p>
          <p className="text-gray-500 text-xs sm:text-sm max-w-2xl mx-auto px-4">
            Faça upload de relatórios de FII em PDF e obtenha análises detalhadas com IA, 
            métricas financeiras automáticas e comparações por segmento
          </p>
        </header>

        <HelpSection />
        
        <SessionStatus />

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-8 mb-8">
          <div className="lg:col-span-1">
            <PDFUpload />
          </div>
          <div className="lg:col-span-3">
            <AnalysisTable />
          </div>
        </div>
      </div>
    </div>
  );
}
