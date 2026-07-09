/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Sidebar & shell
        sidebar: {
          bg:      '#0a0b0f',
          border:  '#1a1c26',
          hover:   '#14151e',
          active:  '#1c1e2c',
          text:    '#8b8fa8',
          muted:   '#3d4160',
        },
        // Surface / canvas — dark by default
        canvas:  '#0d0e18',
        surface: '#111220',
        // Brand accent — Amber / Gold
        brand: {
          50:  '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        // Secondary accent — Electric Cyan (for live/active indicators)
        cyan: {
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4',
          600: '#0891b2',
        },
        // Neutral slate
        ink: {
          50:  '#f8f9fb',
          100: '#f1f2f6',
          200: '#e4e6ef',
          300: '#d1d5e0',
          400: '#9aa0b8',
          500: '#6b7290',
          600: '#4a5168',
          700: '#343a52',
          800: '#1e2130',
          900: '#0f1117',
        },
        // Status colors
        success: { light: '#d1fae5', DEFAULT: '#10b981', dark: '#065f46' },
        warning: { light: '#fef3c7', DEFAULT: '#f59e0b', dark: '#92400e' },
        danger:  { light: '#fee2e2', DEFAULT: '#ef4444', dark: '#991b1b' },
        info:    { light: '#dbeafe', DEFAULT: '#3b82f6', dark: '#1e40af' },
      },
      fontFamily: {
        sans:    ['DM Sans', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Syne', 'system-ui', '-apple-system', 'sans-serif'],
        mono:    ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        'soft':       '0 2px 8px 0 rgba(0,0,0,0.25)',
        'card':       '0 1px 3px 0 rgba(0,0,0,0.3), 0 1px 2px -1px rgba(0,0,0,0.2)',
        'card-md':    '0 4px 12px 0 rgba(0,0,0,0.35), 0 2px 4px -2px rgba(0,0,0,0.2)',
        'card-lg':    '0 8px 24px 0 rgba(0,0,0,0.4), 0 4px 8px -4px rgba(0,0,0,0.2)',
        'glow':       '0 0 0 3px rgba(245,158,11,0.25)',
        'glow-sm':    '0 0 0 2px rgba(245,158,11,0.20)',
        'glow-amber': '0 4px 20px rgba(245,158,11,0.35)',
        'glow-cyan':  '0 0 0 2px rgba(6,182,212,0.25)',
        'inner-sm':   'inset 0 1px 2px 0 rgba(0,0,0,0.3)',
        'sidebar':    '4px 0 24px 0 rgba(0,0,0,0.4)',
      },
      backgroundImage: {
        'gradient-brand':   'linear-gradient(135deg, #d97706 0%, #f59e0b 100%)',
        'gradient-brand-v': 'linear-gradient(180deg, #d97706 0%, #b45309 100%)',
        'gradient-surface': 'linear-gradient(180deg, #111220 0%, #0d0e18 100%)',
        'gradient-dark':    'linear-gradient(135deg, #0a0b0f 0%, #14151e 100%)',
        'gradient-mesh':    'radial-gradient(ellipse at 20% 50%, rgba(245,158,11,0.08) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(6,182,212,0.06) 0%, transparent 60%)',
        'noise':            "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E\")",
      },
      keyframes: {
        'fade-in':      { from: { opacity: '0' }, to: { opacity: '1' } },
        'fade-up':      { from: { opacity: '0', transform: 'translateY(10px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        'fade-down':    { from: { opacity: '0', transform: 'translateY(-10px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        'slide-right':  { from: { opacity: '0', transform: 'translateX(-16px)' }, to: { opacity: '1', transform: 'translateX(0)' } },
        'slide-left':   { from: { opacity: '0', transform: 'translateX(16px)' }, to: { opacity: '1', transform: 'translateX(0)' } },
        'scale-in':     { from: { opacity: '0', transform: 'scale(0.95)' }, to: { opacity: '1', transform: 'scale(1)' } },
        'shimmer':      { from: { backgroundPosition: '-200% 0' }, to: { backgroundPosition: '200% 0' } },
        'spin-slow':    { to: { transform: 'rotate(360deg)' } },
        'pulse-soft':   { '0%, 100%': { opacity: '1' }, '50%': { opacity: '0.5' } },
        'bounce-sm':    { '0%, 100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-4px)' } },
        'sidebar-in':   { from: { transform: 'translateX(-100%)' }, to: { transform: 'translateX(0)' } },
        'glow-pulse':   { '0%, 100%': { boxShadow: '0 4px 20px rgba(245,158,11,0.2)' }, '50%': { boxShadow: '0 4px 30px rgba(245,158,11,0.45)' } },
        'amber-sweep':  { from: { backgroundPosition: '200% center' }, to: { backgroundPosition: '-200% center' } },
      },
      animation: {
        'fade-in':     'fade-in 0.2s ease-out',
        'fade-up':     'fade-up 0.3s ease-out',
        'fade-down':   'fade-down 0.3s ease-out',
        'slide-right': 'slide-right 0.3s ease-out',
        'slide-left':  'slide-left 0.3s ease-out',
        'scale-in':    'scale-in 0.2s ease-out',
        'shimmer':     'shimmer 2s linear infinite',
        'spin-slow':   'spin-slow 3s linear infinite',
        'pulse-soft':  'pulse-soft 2s ease-in-out infinite',
        'bounce-sm':   'bounce-sm 1.5s ease-in-out infinite',
        'sidebar-in':  'sidebar-in 0.25s ease-out',
        'glow-pulse':  'glow-pulse 2s ease-in-out infinite',
        'amber-sweep': 'amber-sweep 3s linear infinite',
      },
      transitionTimingFunction: {
        'spring': 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
}
