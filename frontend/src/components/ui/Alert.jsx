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
  default:     'bg-info/8    border-info/20    text-blue-800',
  destructive: 'bg-danger/8  border-danger/20  text-red-800',
  success:     'bg-success/8 border-success/20 text-emerald-800',
  warning:     'bg-warning/8 border-warning/20 text-amber-800',
  info:        'bg-info/8    border-info/20    text-blue-800',
};

const iconColors = {
  default:     'text-info',
  destructive: 'text-danger',
  success:     'text-success',
  warning:     'text-warning',
  info:        'text-info',
};

const Alert = React.forwardRef(({ className, variant = 'default', children, ...props }, ref) => (
  <div
    ref={ref}
    role="alert"
    className={`flex gap-3 w-full rounded-xl border px-4 py-3 text-sm ${
      variants[variant] || variants.default
    } ${className || ''}`}
    {...props}
  >
    <span className={`mt-0.5 shrink-0 ${iconColors[variant] || iconColors.default}`}>
      {iconMap[variant] || iconMap.default}
    </span>
    <div className="flex-1 min-w-0">{children}</div>
  </div>
))
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
