import React from 'react';
import { AlertTriangle, CheckCircle, Info, XCircle } from 'lucide-react';

const iconMap = {
  default:     <Info className="w-4 h-4" />,
  destructive: <XCircle className="w-4 h-4" />,
  success:     <CheckCircle className="w-4 h-4" />,
  warning:     <AlertTriangle className="w-4 h-4" />,
  info:        <Info className="w-4 h-4" />,
};

const variants = {
  default:     { bg: 'rgba(59,130,246,0.08)',  border: 'rgba(59,130,246,0.2)',   text: '#93c5fd', iconColor: '#3b82f6'  },
  destructive: { bg: 'rgba(239,68,68,0.08)',   border: 'rgba(239,68,68,0.2)',    text: '#fca5a5', iconColor: '#ef4444'  },
  success:     { bg: 'rgba(16,185,129,0.08)',  border: 'rgba(16,185,129,0.2)',   text: '#6ee7b7', iconColor: '#10b981'  },
  warning:     { bg: 'rgba(245,158,11,0.08)',  border: 'rgba(245,158,11,0.2)',   text: '#fcd34d', iconColor: '#f59e0b'  },
  info:        { bg: 'rgba(59,130,246,0.08)',  border: 'rgba(59,130,246,0.2)',   text: '#93c5fd', iconColor: '#3b82f6'  },
};

const Alert = React.forwardRef(({ className, variant = 'default', children, ...props }, ref) => {
  const v = variants[variant] || variants.default;
  return (
    <div
      ref={ref}
      role="alert"
      className={`flex gap-3 w-full rounded-xl border px-4 py-3 text-sm ${className || ''}`}
      style={{ background: v.bg, borderColor: v.border, color: v.text }}
      {...props}
    >
      <span className="mt-0.5 shrink-0" style={{ color: v.iconColor }}>
        {iconMap[variant] || iconMap.default}
      </span>
      <div className="flex-1 min-w-0">{children}</div>
    </div>
  );
})
Alert.displayName = 'Alert'

const AlertTitle = React.forwardRef(({ className, children, ...props }, ref) => (
  <h5
    ref={ref}
    className={`font-semibold leading-snug mb-0.5 ${className || ''}`}
    {...props}
  >
    {children}
  </h5>
))
AlertTitle.displayName = 'AlertTitle'

const AlertDescription = React.forwardRef(({ className, children, ...props }, ref) => (
  <div
    ref={ref}
    className={`text-sm opacity-90 leading-relaxed ${className || ''}`}
    {...props}
  >
    {children}
  </div>
))
AlertDescription.displayName = 'AlertDescription'

export { Alert, AlertTitle, AlertDescription }
