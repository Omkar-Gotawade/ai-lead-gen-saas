import React from 'react';

const Input = ({
  label,
  error,
  helperText,
  icon,
  suffix,
  className = '',
  fullWidth = true,
  ...props
}) => {
  const base = [
    'block border rounded-lg text-sm transition-colors duration-150',
    'focus:outline-none focus:ring-2',
    'placeholder:text-[#252840]',
    error
      ? 'border-danger focus:border-danger focus:ring-danger/20'
      : 'focus:border-brand-500 focus:ring-brand-500/15',
    icon ? 'pl-9' : 'pl-3',
    suffix ? 'pr-9' : 'pr-3',
    'py-2',
    fullWidth ? 'w-full' : '',
    className,
  ].join(' ');

  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label className="block text-xs font-medium mb-1.5" style={{ color: '#4a5168' }}>
          {label}
          {props.required && <span className="text-danger ml-0.5">*</span>}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-2.5 flex items-center pointer-events-none" style={{ color: '#343a52' }}>
            {icon}
          </div>
        )}
        <input
          className={base}
          style={{
            background: '#111220',
            border: error ? '' : '1px solid rgba(255,255,255,0.08)',
            color: '#c8cce0',
            ...(props.disabled ? { opacity: 0.5, cursor: 'not-allowed', background: '#0d0e18' } : {}),
          }}
          {...props}
        />
        {suffix && (
          <div className="absolute inset-y-0 right-0 pr-2.5 flex items-center pointer-events-none" style={{ color: '#343a52' }}>
            {suffix}
          </div>
        )}
      </div>
      {error && <p className="mt-1 text-xs text-danger">{error}</p>}
      {helperText && !error && <p className="mt-1 text-xs" style={{ color: '#343a52' }}>{helperText}</p>}
    </div>
  );
};

export default Input;
