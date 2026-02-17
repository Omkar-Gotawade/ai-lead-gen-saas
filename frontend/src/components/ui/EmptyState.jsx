import React from 'react';
import Button from './Button';
import { Card, CardContent } from './Card';
import { Alert, AlertDescription } from './Alert';
import { AlertTriangle } from 'lucide-react';

const EmptyState = ({ 
  icon, 
  title, 
  description,
  // New props for enhanced functionality
  actions = [],         // Array of action buttons: [{ label, onClick, variant, icon, disabled }]
  helpText,            // Additional help text below buttons
  warning,             // Warning message to display
  className = '',
  // Legacy props for backward compatibility
  actionLabel, 
  onAction,
  actionIcon 
}) => {
  // Convert legacy props to new format for backward compatibility
  const actionButtons = actions.length > 0 
    ? actions 
    : actionLabel && onAction 
    ? [{ label: actionLabel, onClick: onAction, icon: actionIcon, variant: 'primary' }]
    : [];

  return (
    <Card className={`border-2 border-dashed ${className}`}>
      <CardContent className="flex flex-col items-center justify-center py-16 px-6 text-center">
        <div className="flex justify-center mb-6">
          {icon ? (
            <div className="p-4 rounded-full bg-slate-100">
              {React.cloneElement(icon, { className: 'w-12 h-12 text-slate-400' })}
            </div>
          ) : (
            <div className="p-4 rounded-full bg-slate-100">
              <svg
                className="h-12 w-12 text-slate-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="1"
                  d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                />
              </svg>
            </div>
          )}
        </div>
        
        <h3 className="text-2xl font-semibold text-slate-900 mb-2">
          {title}
        </h3>
        
        <p className="text-slate-600 mb-6 max-w-md">
          {description}
        </p>
        
        {warning && (
          <Alert variant="destructive" className="mb-6 max-w-md">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{warning}</AlertDescription>
          </Alert>
        )}
        
        {actionButtons.length > 0 && (
          <div className="flex flex-wrap gap-3 justify-center mb-4">
            {actionButtons.map((action, idx) => (
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
        
        {helpText && (
          <p className="text-sm text-slate-500 mt-4 max-w-lg">
            {helpText}
          </p>
        )}
      </CardContent>
    </Card>
  );
};

export default EmptyState;
