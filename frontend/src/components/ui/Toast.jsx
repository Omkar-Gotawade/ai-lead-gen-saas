import React, { useEffect, useState } from 'react'
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-react'

const config = {
  default: { Icon: Info,          iconCls: 'text-info',    border: 'border-info/20'    },
  success: { Icon: CheckCircle,   iconCls: 'text-success', border: 'border-success/30' },
  error:   { Icon: XCircle,       iconCls: 'text-danger',  border: 'border-danger/30'  },
  warning: { Icon: AlertTriangle, iconCls: 'text-warning', border: 'border-warning/30' },
  info:    { Icon: Info,          iconCls: 'text-info',    border: 'border-info/20'    },
}

/**
 * Single toast notification.
 * Rendered by ToastContext — do not use directly.
 */
export default function Toast({ message, title, variant = 'default', onClose }) {
  const [visible, setVisible] = useState(false)
  const { Icon, iconCls, border } = config[variant] || config.default

  /* Trigger enter animation on next frame */
  useEffect(() => {
    const raf = requestAnimationFrame(() => setVisible(true))
    return () => cancelAnimationFrame(raf)
  }, [])

  const handleClose = () => {
    setVisible(false)
    setTimeout(onClose, 280) // wait for exit animation
  }

  return (
    <div
      role="alert"
      className={[
        'pointer-events-auto flex items-start gap-3',
        'min-w-[280px] max-w-sm w-full rounded-xl border shadow-card-lg',
        'bg-ink-900/95 backdrop-blur-md text-white px-4 py-3',
        border,
        'transition-all duration-280 ease-out',
        visible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-6',
      ].join(' ')}
    >
      <Icon className={`w-4 h-4 shrink-0 mt-0.5 ${iconCls}`} />

      <div className="flex-1 min-w-0">
        {title && (
          <p className="text-sm font-semibold text-white mb-0.5 leading-snug">{title}</p>
        )}
        <p className="text-sm text-white/75 leading-relaxed">{message}</p>
      </div>

      <button
        onClick={handleClose}
        aria-label="Dismiss notification"
        className="shrink-0 mt-0.5 rounded text-white/30 hover:text-white/80 transition-colors focus:outline-none focus-visible:ring-1 focus-visible:ring-white/40"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  )
}
