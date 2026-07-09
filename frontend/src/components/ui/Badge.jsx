import React from 'react';

const Badge = ({ children, variant = 'default', size = 'sm', dot = false, className = '' }) => {
  const base = 'inline-flex items-center gap-1.5 font-medium rounded-full leading-none';

  const variants = {
    default:       'bg-white/[0.05] text-[#6b7290] border border-white/[0.06]',
    secondary:     'bg-white/[0.04] text-[#4a5168] border border-white/[0.04]',
    success:       'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
    warning:       'bg-amber-500/10 text-amber-400 border border-amber-500/20',
    danger:        'bg-red-500/10 text-red-400 border border-red-500/20',
    destructive:   'bg-red-500/10 text-red-400 border border-red-500/20',
    info:          'bg-blue-500/10 text-blue-400 border border-blue-500/20',
    brand:         'bg-amber-500/12 text-amber-400 border border-amber-500/25',
    indigo:        'bg-amber-500/12 text-amber-400 border border-amber-500/25',
    purple:        'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20',
    // filled solid variants
    'success-solid': 'bg-emerald-500 text-white',
    'danger-solid':  'bg-red-500 text-white',
    'brand-solid':   'bg-amber-500 text-[#07080f] font-semibold',
  };

  const sizes = {
    xs: 'px-1.5 py-0.5 text-[10px]',
    sm: 'px-2   py-0.5 text-xs',
    md: 'px-2.5 py-1   text-xs',
    lg: 'px-3   py-1   text-sm',
  };

  const dotColors = {
    default:     'bg-[#4a5168]',
    secondary:   'bg-[#343a52]',
    success:     'bg-emerald-400',
    warning:     'bg-amber-400',
    danger:      'bg-red-400',
    destructive: 'bg-red-400',
    info:        'bg-blue-400',
    brand:       'bg-amber-400',
    indigo:      'bg-amber-400',
    purple:      'bg-cyan-400',
  };

  return (
    <span className={[base, variants[variant] ?? variants.default, sizes[size] ?? sizes.sm, className].join(' ')}>
      {dot && <span className={`w-1.5 h-1.5 rounded-full shrink-0 animate-pulse-soft ${dotColors[variant] || 'bg-[#4a5168]'}`} />}
      {children}
    </span>
  );
};

export default Badge;
