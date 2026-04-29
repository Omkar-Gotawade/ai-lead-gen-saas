import React, { useEffect, useRef } from 'react'
import { AlertTriangle, X } from 'lucide-react'
import Button from './Button'

/**
 * Inline confirmation dialog — replaces browser window.confirm().
 *
 * @example
 * <ConfirmDialog
 *   isOpen={showConfirm}
 *   onConfirm={handleDelete}
 *   onCancel={() => setShowConfirm(false)}
 *   title="Delete Campaign"
 *   message={`Are you sure you want to delete "${name}"? This cannot be undone.`}
 *   confirmLabel="Delete"
 *   variant="danger"
 * />
 */
export default function ConfirmDialog({
  isOpen,
  onConfirm,
  onCancel,
  title = 'Are you sure?',
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'danger',   // 'danger' | 'primary'
  loading = false,
}) {
  const cancelRef = useRef(null)

  /* Focus the cancel button when dialog opens (safer default) */
  useEffect(() => {
    if (isOpen) {
      requestAnimationFrame(() => cancelRef.current?.focus())
    }
  }, [isOpen])

  /* Close on Escape */
  useEffect(() => {
    if (!isOpen) return
    const handler = (e) => { if (e.key === 'Escape') onCancel() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [isOpen, onCancel])

  if (!isOpen) return null

  return (
    /* Backdrop */
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center p-4"
      role="presentation"
    >
      <div
        className="absolute inset-0 bg-ink-900/50 backdrop-blur-sm modal-backdrop"
        onClick={onCancel}
      />

      {/* Dialog panel */}
      <div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        aria-describedby={message ? 'confirm-message' : undefined}
        className="relative z-10 w-full max-w-sm bg-surface rounded-2xl shadow-card-lg border border-ink-100 animate-scale-in p-6"
      >
        {/* Icon + close */}
        <div className="flex items-start justify-between mb-4">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${
            variant === 'danger' ? 'bg-danger/10' : 'bg-brand-50'
          }`}>
            <AlertTriangle className={`w-5 h-5 ${variant === 'danger' ? 'text-danger' : 'text-brand-600'}`} />
          </div>
          <button
            onClick={onCancel}
            className="text-ink-400 hover:text-ink-700 transition-colors rounded-md p-1 -mr-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
            aria-label="Cancel"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <h2 id="confirm-title" className="text-base font-semibold text-ink-900 mb-1.5">
          {title}
        </h2>
        {message && (
          <p id="confirm-message" className="text-sm text-ink-500 leading-relaxed mb-6">
            {message}
          </p>
        )}

        {/* Actions */}
        <div className="flex gap-2 justify-end">
          <Button
            ref={cancelRef}
            variant="outline"
            size="sm"
            onClick={onCancel}
            disabled={loading}
          >
            {cancelLabel}
          </Button>
          <Button
            variant={variant === 'danger' ? 'danger' : 'primary'}
            size="sm"
            onClick={onConfirm}
            loading={loading}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  )
}
