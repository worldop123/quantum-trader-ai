/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'quantum-dark': '#0a0e17',
        'quantum-darker': '#060912',
        'quantum-card': '#111827',
        'quantum-border': '#1f2937',
        'quantum-cyan': '#00f5ff',
        'quantum-purple': '#a855f7',
        'quantum-green': '#10b981',
        'quantum-red': '#ef4444',
        'quantum-yellow': '#f59e0b',
        'quantum-blue': '#3b82f6',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'neon-cyan': '0 0 20px rgba(0, 245, 255, 0.3)',
        'neon-purple': '0 0 20px rgba(168, 85, 247, 0.3)',
        'neon-green': '0 0 20px rgba(16, 185, 129, 0.3)',
        'neon-red': '0 0 20px rgba(239, 68, 68, 0.3)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(0, 245, 255, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(0, 245, 255, 0.8)' },
        }
      }
    },
  },
  plugins: [],
}
