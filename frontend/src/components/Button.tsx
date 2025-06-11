export function Button({ className, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button className={`px-4 py-2 rounded hover:bg-fontBlue transition hover:cursor-pointer ${className}`} {...props} />;
}