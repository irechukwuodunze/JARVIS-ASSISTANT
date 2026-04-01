import React from 'react'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'accent' | 'success' | 'warning' | 'error'
  className?: string
}

export function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  const variantClasses = {
    default: 'bg-black text-white',
    accent: 'bg-[#FF6B6B] text-white',
    success: 'bg-[#51CF66] text-white',
    warning: 'bg-[#FFD93D] text-black',
    error: 'bg-[#FF6B6B] text-white',
  }

  return (
    <span className={`inline-block px-3 py-1 border-2 border-black text-xs font-bold font-[Archivo] ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  )
}
