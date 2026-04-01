import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'accent' | 'error'
  size?: 'sm' | 'md' | 'lg'
}

export function Button({
  variant = 'secondary',
  size = 'md',
  className = '',
  children,
  ...props
}: ButtonProps) {
  const baseClasses = 'font-[Archivo] font-bold border-2 border-black transition-all'
  
  const variantClasses = {
    primary: 'bg-black text-white hover:shadow-[4px_4px_0px_rgba(0,0,0,1)]',
    secondary: 'bg-white text-black hover:shadow-[4px_4px_0px_rgba(0,0,0,1)]',
    accent: 'bg-[#FF6B6B] text-white hover:shadow-[4px_4px_0px_rgba(0,0,0,1)]',
    error: 'bg-[#FF6B6B] text-white hover:shadow-[4px_4px_0px_rgba(0,0,0,1)]',
  }

  const sizeClasses = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  }

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} shadow-[2px_2px_0px_rgba(0,0,0,1)] hover:-translate-x-0.5 hover:-translate-y-0.5 active:shadow-none active:translate-x-0 active:translate-y-0 ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
