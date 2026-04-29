import React, { useState } from 'react'
import { Eye, EyeOff, Lock } from 'lucide-react'

/**
 * Password input with show/hide toggle.
 *
 * @example
 * <PasswordInput
 *   value={password}
 *   onChange={(e) => setPassword(e.target.value)}
 *   placeholder="••••••••"
 *   label="Password"
 * />
 */
const PasswordInput = React.forwardRef(({
  value,
  onChange,
  placeholder = '••••••••',
  label,
  id,
  required,
  autoComplete = 'current-password',
  className = '',
  inputClassName = '',
  /* dark mode (login page) vs light mode */
  dark = false,
}, ref) => {
  const [visible, setVisible] = useState(false)

  const baseInput = dark
    ? 'w-full bg-white/5 border border-white/10 rounded-lg pl-9 pr-10 py-2.5 text-sm text-white placeholder-ink-600 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors'
    : 'w-full bg-surface border border-ink-200 rounded-lg pl-9 pr-10 py-2.5 text-sm text-ink-900 placeholder-ink-400 focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors'

  const labelClass = dark
    ? 'text-xs font-medium text-ink-300 mb-1.5 block'
    : 'text-xs font-medium text-ink-600 mb-1.5 block'

  const iconColor = dark ? 'text-ink-500' : 'text-ink-400'
  const toggleColor = dark
    ? 'text-ink-500 hover:text-ink-300'
    : 'text-ink-400 hover:text-ink-600'

  return (
    <div className={className}>
      {label && (
        <label htmlFor={id} className={labelClass}>
          {label}
        </label>
      )}
      <div className="relative">
        <Lock
          className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none ${iconColor}`}
        />
        <input
          ref={ref}
          id={id}
          type={visible ? 'text' : 'password'}
          value={value}
          onChange={onChange}
          required={required}
          autoComplete={autoComplete}
          placeholder={placeholder}
          className={[baseInput, inputClassName].join(' ')}
        />
        <button
          type="button"
          onClick={() => setVisible((v) => !v)}
          aria-label={visible ? 'Hide password' : 'Show password'}
          className={`absolute right-3 top-1/2 -translate-y-1/2 transition-colors focus:outline-none focus-visible:ring-1 focus-visible:ring-brand-500 rounded ${toggleColor}`}
        >
          {visible
            ? <EyeOff className="w-4 h-4" />
            : <Eye className="w-4 h-4" />
          }
        </button>
      </div>
    </div>
  )
})

PasswordInput.displayName = 'PasswordInput'
export default PasswordInput
