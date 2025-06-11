import { Search } from 'lucide-react';

export function Input({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) {
  return <div className='relative'><input className={`rounded-[8px] px-4 py-2 ${className}`} {...props} /><Search className='absolute top-[8px] right-[10px] w-[18px]'/></div>;
}