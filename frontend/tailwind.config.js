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
          bg:      '#0f1117',
          border:  '#1e2130',
          hover:   '#1a1d2e',
          active:  '#22263a',
          text:    '#8b8fa8',
          muted:   '#4a4f6a',
        },
        // Surface / canvas
        canvas:  '#f6f7fb',
        surface: '#ffffff',
        // Brand accent — violet
        brand: {
          50:  '#f3f0ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
        },
        // Neutral slate (replaces default gray in components)
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
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        'soft':    '0 2px 8px 0 rgba(15,17,23,0.06)',
        'card':    '0 1px 3px 0 rgba(15,17,23,0.08), 0 1px 2px -1px rgba(15,17,23,0.06)',
        'card-md': '0 4px 12px 0 rgba(15,17,23,0.10), 0 2px 4px -2px rgba(15,17,23,0.06)',
        'card-lg': '0 8px 24px 0 rgba(15,17,23,0.12), 0 4px 8px -4px rgba(15,17,23,0.06)',
        'glow':    '0 0 0 3px rgba(139,92,246,0.25)',
        'glow-sm': '0 0 0 2px rgba(139,92,246,0.20)',
        'inner-sm':'inset 0 1px 2px 0 rgba(15,17,23,0.06)',
        'sidebar':  '4px 0 24px 0 rgba(0,0,0,0.18)',
      },
      backgroundImage: {
        'gradient-brand':   'linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)',
        'gradient-surface': 'linear-gradient(180deg, #ffffff 0%, #f6f7fb 100%)',
        'gradient-dark':    'linear-gradient(135deg, #0f1117 0%, #1a1d2e 100%)',
        'gradient-mesh':    'radial-gradient(ellipse at 20% 50%, rgba(139,92,246,0.15) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(168,85,247,0.10) 0%, transparent 60%)',
        'noise':            "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E\")",
      },
      keyframes: {
        'fade-in':     { from: { opacity: '0' }, to: { opacity: '1' } },
        'fade-up':     { from: { opacity: '0', transform: 'translateY(10px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        'fade-down':   { from: { opacity: '0', transform: 'translateY(-10px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        'slide-right': { from: { opacity: '0', transform: 'translateX(-16px)' }, to: { opacity: '1', transform: 'translateX(0)' } },
        'slide-left':  { from: { opacity: '0', transform: 'translateX(16px)' }, to: { opacity: '1', transform: 'translateX(0)' } },
        'scale-in':    { from: { opacity: '0', transform: 'scale(0.95)' }, to: { opacity: '1', transform: 'scale(1)' } },
        'shimmer':     { from: { backgroundPosition: '-200% 0' }, to: { backgroundPosition: '200% 0' } },
        'spin-slow':   { to: { transform: 'rotate(360deg)' } },
        'pulse-soft':  { '0%, 100%': { opacity: '1' }, '50%': { opacity: '0.6' } },
        'bounce-sm':   { '0%, 100%': { transform: 'translateY(0)' }, '50%': { transform: 'translateY(-4px)' } },
        'sidebar-in':  { from: { transform: 'translateX(-100%)' }, to: { transform: 'translateX(0)' } },
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
      },
      transitionTimingFunction: {
        'spring': 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
}
