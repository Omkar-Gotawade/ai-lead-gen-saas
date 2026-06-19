import React from 'react'
import { ChevronDown } from 'lucide-react'

/**
 * Styled select wrapper that matches the Input component visual language.
 *
 * @example
 * <Select
 *   label="Email Tone"
 *   value={tone}
 *   onChange={(e) => setTone(e.target.value)}
 *   options={[
 *     { value: 'professional', label: 'Professional' },
 *     { value: 'friendly', label: 'Friendly' },
 *   ]}
 * />
 */
const Select = React.forwardRef(function Select(
  {
    label,
    id,
    value,
    onChange,
    options = [],
    placeholder,
    required,
    disabled,
    helperText,
    error,
    className = '',
  },
  ref
) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')

  const baseSelect = [
    'w-full appearance-none bg-surface border rounded-lg pl-3 pr-9 py-2.5 text-sm text-ink-900',
    'focus:outline-none focus:ring-1 focus:ring-brand-500 focus:border-brand-500 transition-colors',
    'disabled:opacity-60 disabled:cursor-not-allowed',
    error ? 'border-danger' : 'border-ink-200',
  ].join(' ')

  return (
    <div className={className}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-xs font-medium text-ink-600 mb-1.5"
        >
          {label}
          {required && <span className="text-danger ml-0.5">*</span>}
        </label>
      )}
      <div className="relative">
        <select
          ref={ref}
          id={inputId}
          value={value}
          onChange={onChange}
          required={required}
          disabled={disabled}
          className={baseSelect}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((opt) =>
            typeof opt === 'string' ? (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ) : (
              <option key={opt.value} value={opt.value} disabled={opt.disabled}>
                {opt.label}
              </option>
            )
          )}
        </select>
        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-400 pointer-events-none" />
      </div>
      {helperText && !error && (
        <p className="mt-1 text-xs text-ink-400">{helperText}</p>
      )}
      {error && <p className="mt-1 text-xs text-danger">{error}</p>}
    </div>
  )
})

Select.displayName = 'Select'
export default Select
