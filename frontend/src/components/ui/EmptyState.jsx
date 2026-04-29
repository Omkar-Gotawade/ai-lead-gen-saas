import React from 'react'
import Button from './Button'
import { Card, CardContent } from './Card'
import { Alert, AlertDescription } from './Alert'
import { AlertTriangle } from 'lucide-react'

/**
 * EmptyState — consistent with the design system ink/brand token palette.
 * Supports legacy single-action props for backward compatibility.
 */
const EmptyState = ({
  icon,
  title,
  description,
  actions = [],
  helpText,
  warning,
  className = '',
  /* Legacy props */
  actionLabel,
  onAction,
  actionIcon,
}) => {
  const buttons =
    actions.length > 0
      ? actions
      : actionLabel && onAction
      ? [{ label: actionLabel, onClick: onAction, icon: actionIcon, variant: 'primary' }]
      : []

  return (
    <Card className={`border-2 border-dashed border-ink-200 ${className}`}>
      <CardContent className="flex flex-col items-center justify-center py-16 px-6 text-center">

        {/* Icon */}
        <div className="flex justify-center mb-6">
          {icon ? (
            <div className="p-4 rounded-2xl bg-ink-100">
              {React.cloneElement(icon, { className: 'w-10 h-10 text-ink-400' })}
            </div>
          ) : (
            <div className="p-4 rounded-2xl bg-ink-100">
              <svg
                className="w-10 h-10 text-ink-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="1.5"
                  d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                />
              </svg>
            </div>
          )}
        </div>

        {/* Text */}
        <h3 className="text-xl font-semibold text-ink-900 mb-2">{title}</h3>
        <p className="text-sm text-ink-500 mb-6 max-w-md leading-relaxed">{description}</p>

        {/* Warning */}
        {warning && (
          <Alert variant="warning" className="mb-6 max-w-md">
            <AlertDescription>{warning}</AlertDescription>
          </Alert>
        )}

        {/* Action buttons */}
        {buttons.length > 0 && (
          <div className="flex flex-wrap gap-3 justify-center mb-4">
            {buttons.map((action, idx) => (
              <Button
                key={idx}
                variant={action.variant || 'primary'}
                onClick={action.onClick}
                icon={action.icon}
                disabled={action.disabled}
              >
                {action.label}
              </Button>
            ))}
          </div>
        )}

        {/* Help text */}
        {helpText && (
          <p className="text-xs text-ink-400 mt-4 max-w-lg leading-relaxed">{helpText}</p>
        )}
      </CardContent>
    </Card>
  )
}

export default EmptyState
