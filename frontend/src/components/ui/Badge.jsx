import React from 'react';

const Badge = ({ children, variant = 'default', size = 'sm', dot = false, className = '' }) => {
  const base = 'inline-flex items-center gap-1.5 font-medium rounded-full leading-none';

  const variants = {
    default: 'bg-ink-100 text-ink-700',
    success: 'bg-success/10 text-emerald-700',
    warning: 'bg-warning/10 text-amber-700',
    danger:  'bg-danger/10  text-red-700',
    info:    'bg-info/10    text-blue-700',
    brand:   'bg-brand-100  text-brand-700',
    indigo:  'bg-brand-100  text-brand-700',
    purple:  'bg-purple-100 text-purple-700',
    // filled dark variants
    'success-solid': 'bg-success text-white',
    'danger-solid':  'bg-danger  text-white',
    'brand-solid':   'bg-brand-600 text-white',
  };

  const sizes = {
    xs: 'px-1.5 py-0.5 text-[10px]',
    sm: 'px-2   py-0.5 text-xs',
    md: 'px-2.5 py-1   text-xs',
    lg: 'px-3   py-1   text-sm',
  };

  const dotColors = {
    default: 'bg-ink-400',
    success: 'bg-success',
    warning: 'bg-warning',
    danger:  'bg-danger',
    info:    'bg-info',
    brand:   'bg-brand-500',
    indigo:  'bg-brand-500',
  };

  return (
    <span className={[base, variants[variant] ?? variants.default, sizes[size] ?? sizes.sm, className].join(' ')}>
      {dot && <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${dotColors[variant] || 'bg-ink-400'}`} />}
      {children}
    </span>
  );
};

export default Badge;
