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
    'bg-surface text-ink-900 placeholder:text-ink-400',
    'focus:outline-none focus:ring-2',
    error
      ? 'border-danger focus:border-danger focus:ring-danger/20'
      : 'border-ink-200 focus:border-brand-500 focus:ring-brand-500/15',
    'disabled:opacity-60 disabled:cursor-not-allowed',
    icon ? 'pl-9' : 'pl-3',
    suffix ? 'pr-9' : 'pr-3',
    'py-2.5',
    fullWidth ? 'w-full' : '',
    className,
  ].join(' ');

  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label className="block text-xs font-medium text-ink-600 mb-1.5">
          {label}
          {props.required && <span className="text-danger ml-0.5">*</span>}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-ink-400">
            {icon}
          </div>
        )}
        <input
          className={base}
          {...props}
        />
        {suffix && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-ink-400">
            {suffix}
          </div>
        )}
      </div>
      {error && <p className="mt-1 text-xs text-danger">{error}</p>}
      {helperText && !error && <p className="mt-1 text-xs text-ink-400">{helperText}</p>}
    </div>
  );
};

export default Input;
