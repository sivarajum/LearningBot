import type { Config } from 'tailwindcss';
import typography from '@tailwindcss/typography';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-geist-sans)', 'Inter', 'system-ui'],
        mono: ['var(--font-geist-mono)', 'SFMono-Regular', 'monospace'],
      },
      colors: {
        'brand-ink': '#020617',
        'brand-emerald': '#34d399',
      },
      boxShadow: {
        glow: '0 0 60px rgba(16, 185, 129, 0.35)',
      },
    },
  },
  plugins: [typography],
};

export default config;

