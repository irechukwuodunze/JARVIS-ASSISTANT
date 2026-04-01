import React from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export function Input({ label, error, className = '', ...props }: InputProps) {
  return (
    <div className="mb-4">
      {label && (
        <label className="block text-sm font-bold mb-2 font-[Archivo]">
          {label}
        </label>
      )}
      <input
        className={`w-full border-2 border-black p-3 font-[Inter] focus:outline-none focus:shadow-[2px_2px_0px_rgba(0,0,0,1)] focus:bg-[#F4F4F0] ${error ? 'border-[#FF6B6B]' : ''} ${className}`}
        {...props}
      />
      {error && (
        <p className="text-[#FF6B6B] text-sm mt-1 font-[Inter]">{error}</p>
      )}
    </div>
  )
}
