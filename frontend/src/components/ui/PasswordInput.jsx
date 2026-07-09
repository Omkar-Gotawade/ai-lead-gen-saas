import React, { useState } from 'react'
import { Eye, EyeOff, Lock } from 'lucide-react'

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
  helperText,
  dark = false, // kept for API compatibility — all variants now use dark
}, ref) => {
  const [visible, setVisible] = useState(false)

  return (
    <div className={className}>
      {label && (
        <label htmlFor={id} className="text-xs font-medium mb-1.5 block" style={{ color: '#4a5168' }}>
          {label}
        </label>
      )}
      <div className="relative">
        <Lock
          className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 pointer-events-none"
          style={{ color: '#343a52' }}
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
          className={['w-full rounded-lg pl-9 pr-10 py-2 text-sm focus:outline-none focus:ring-2 transition-colors', inputClassName].join(' ')}
          style={{
            background: '#111220',
            border: '1px solid rgba(255,255,255,0.08)',
            color: '#c8cce0',
          }}
          onFocus={e => { e.target.style.borderColor = '#d97706'; e.target.style.boxShadow = '0 0 0 3px rgba(245,158,11,0.12)'; }}
          onBlur={e => { e.target.style.borderColor = 'rgba(255,255,255,0.08)'; e.target.style.boxShadow = 'none'; }}
        />
        <button
          type="button"
          onClick={() => setVisible((v) => !v)}
          aria-label={visible ? 'Hide password' : 'Show password'}
          className="absolute right-3 top-1/2 -translate-y-1/2 transition-colors focus:outline-none rounded"
          style={{ color: '#343a52' }}
          onMouseEnter={e => e.currentTarget.style.color = '#8b8fa8'}
          onMouseLeave={e => e.currentTarget.style.color = '#343a52'}
        >
          {visible ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
        </button>
      </div>
      {helperText && (
        <p className="mt-1 text-xs" style={{ color: '#343a52' }}>
          {helperText}
        </p>
      )}
    </div>
  )
})

PasswordInput.displayName = 'PasswordInput'
export default PasswordInput
