import type { Config } from 'tailwindcss'

export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // AI Writer 创作主题色
        writing: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
        // 创作进度色
        progress: {
          draft: '#94a3b8',
          writing: '#3b82f6',
          completed: '#22c55e',
          reviewed: '#8b5cf6',
        },
        // 关系类型色（用于关系图谱）
        relation: {
          family: '#ef4444',
          love: '#ec4899',
          friend: '#22c55e',
          enemy: '#f97316',
          master: '#8b5cf6',
          rival: '#f59e0b',
        },
      },
    },
  },
  plugins: [],
} satisfies Config
