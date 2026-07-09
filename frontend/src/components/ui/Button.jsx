import React from 'react';

const Button = React.forwardRef(function Button({
  children,
  variant = 'primary',
  size = 'md',
  onClick,
  type = 'button',
  disabled = false,
  loading = false,
  isLoading = false,
  fullWidth = false,
  icon = null,
  iconEnd = null,
  className = '',
  ...props
}, ref) {
  const isLoadingState = loading || isLoading;

  const base = [
    'inline-flex items-center justify-center gap-2 font-semibold rounded-lg',
    'transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-offset-canvas',
    'disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.98] select-none',
  ].join(' ');

  const variants = {
    primary:     'bg-gradient-brand text-[#07080f] hover:opacity-90 shadow-glow-amber focus:ring-brand-400',
    secondary:   'bg-white/[0.06] text-white/70 hover:bg-white/[0.1] hover:text-white border border-white/[0.08] focus:ring-brand-500',
    success:     'bg-success text-white hover:bg-emerald-600 shadow-soft focus:ring-success',
    danger:      'bg-danger text-white hover:bg-red-600 shadow-soft focus:ring-danger',
    destructive: 'bg-danger text-white hover:bg-red-600 shadow-soft focus:ring-danger',
    ghost:       'text-white/50 hover:bg-white/[0.05] hover:text-white/80 focus:ring-brand-400',
    outline:     'bg-transparent text-white/60 border border-white/[0.1] hover:bg-white/[0.05] hover:text-white hover:border-white/[0.15] focus:ring-brand-400',
    link:        'text-brand-400 hover:text-brand-300 hover:underline focus:ring-brand-400 px-0 py-0',
  };

  const sizes = {
    xs: 'px-2.5 py-1 text-xs',
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-2.5 text-sm',
    xl: 'px-6 py-3 text-base',
  };

  return (
    <button
      ref={ref}
      type={type}
      onClick={onClick}
      disabled={disabled || isLoadingState}
      className={[
        base,
        variants[variant] ?? variants.primary,
        sizes[size] ?? sizes.md,
        fullWidth ? 'w-full' : '',
        className,
      ].join(' ')}
      {...props}
    >
      {isLoadingState ? (
        <>
          <svg className="animate-spin h-3.5 w-3.5" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          Loading…
        </>
      ) : (
        <>
          {icon && <span className="shrink-0">{icon}</span>}
          {children}
          {iconEnd && <span className="shrink-0">{iconEnd}</span>}
        </>
      )}
    </button>
  );
});

export default Button;
