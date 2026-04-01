import type { Config } from 'tailwindcss'

export default {
  content: ['./client/src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Neubrutalist palette
        'neu-bg': '#F4F4F0',
        'neu-card': '#FFFFFF',
        'neu-border': '#000000',
        'neu-text': '#000000',
        'neu-text-light': '#666666',
        'neu-accent': '#FF6B6B',
        'neu-success': '#51CF66',
        'neu-warning': '#FFD93D',
        'neu-error': '#FF6B6B',
      },
      fontFamily: {
        'archivo': ['Archivo', 'sans-serif'],
        'inter': ['Inter', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        'neu': '4px 4px 0px rgba(0, 0, 0, 1)',
        'neu-lg': '8px 8px 0px rgba(0, 0, 0, 1)',
        'neu-sm': '2px 2px 0px rgba(0, 0, 0, 1)',
      },
      borderWidth: {
        'neu': '2px',
      },
      spacing: {
        'neu-xs': '4px',
        'neu-sm': '8px',
        'neu-md': '16px',
        'neu-lg': '24px',
        'neu-xl': '32px',
      },
    },
  },
  plugins: [],
} satisfies Config
