import { useRef } from 'react';
import { FilePlus2 } from 'lucide-react';

export function UploadButton() {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      console.log("Arquivo selecionado:", file);
    }
  };

  return (
    <>
      <button
        onClick={handleClick}
        className="px-4 py-2 bg-fontBlue rounded-[8px] flex flex-row items-center gap-2 transition-all hover:bg-frontBlueHover duration-300 ease-in-out hover:cursor-pointer"
      >
        <FilePlus2 className="w-[18px]" />
        Add File
      </button>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        className="hidden"
      />
    </>
  );
}
