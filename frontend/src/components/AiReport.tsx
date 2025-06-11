import { useEffect, useState } from 'react';
import { Brain, Hourglass } from 'lucide-react';

type AiReportProps = {
  text: string;
};

function capitalizeFirstLetter(text: string) {
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

export default function AiReport({ text }: AiReportProps) {
  const [animatedText, setAnimatedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (!text) {
      setAnimatedText('');
      return;
    }

    setAnimatedText('');
    setIsTyping(true);

    const delayTimer = setTimeout(() => {
      let index = 1;
      const typingInterval = setInterval(() => {
        const current = text.substring(0, index);
        setAnimatedText(current);
        index++;

        if (index > text.length) {
          clearInterval(typingInterval);
          setIsTyping(false);
        }
      }, 5);
    }, 1000);

    return () => clearTimeout(delayTimer);
  }, [text]);

  const renderFormattedText = (rawText: string) => {
    const normalizedText = rawText.replace(/\n{2,}/g, '');
    const parts = normalizedText.split(/(\*\*[^*]+\*\*)/g);

    return parts.map((part, index) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        const content = part.slice(2, -2);
        return (
          <strong key={index} className="text-fontBlue font-normal text-[20px] pb-2">
            {capitalizeFirstLetter(content)}
          </strong>
        );
      }

      return (
        <p
          className="flex h-[100%] leading-[1.6] font-normal text-[16px] text-fontLightGray whitespace-pre-wrap pb-6"
          key={index}
        >
          {part}
        </p>
      );
    });
  };

  return (
    <div className="flex flex-col bg-bgTable p-4 sm:rounded-[8px] w-[100%] max-w-[100%]">
      <div>
        <p className="flex flex-row gap-2 items-center text-[20px] pb-2 border-b-[1px] w-[100%] border-borderGray font-bold">
          <Brain />
          Relatório AI
        </p>
      </div>

      <div className="text-delete flex flex-col pt-4 sm:p-4 whitespace-pre-line min-h-[120px]">
        {isTyping && <span className="flex flex-row gap-2 items-center text-sm text-fontLightGray animate-pulse pb-2"><Hourglass className='w-[18px]'/> Gerando relatório...</span>}
        {animatedText ? renderFormattedText(animatedText) : 'Gere um relatório para visualizar aqui.'}
      </div>
    </div>
  );
}
