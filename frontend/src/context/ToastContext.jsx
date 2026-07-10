import { createContext, useContext, useState, useCallback } from 'react'
import { createPortal } from 'react-dom'
import Toast from '../components/ui/Toast'

const ToastContext = createContext(null)

let _id = 0

/**
 * Provides a global toast notification system.
 * Wrap your app (or Router) with <ToastProvider>.
 */
export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const addToast = useCallback(
    ({ message, title, variant = 'default', duration = 4000 }) => {
      const id = ++_id
      setToasts((prev) => [...prev, { id, message, title, variant }])
      if (duration > 0) {
        setTimeout(() => dismiss(id), duration)
      }
      return id
    },
    [dismiss]
  )

  return (
    <ToastContext.Provider value={{ addToast, dismiss }}>
      {children}
      {createPortal(
        <div
          aria-live="polite"
          aria-atomic="false"
          className="fixed top-4 right-4 flex flex-col gap-2 pointer-events-none"
          style={{ zIndex: 99999 }}
        >
          {toasts.map((t) => (
            <Toast key={t.id} {...t} onClose={() => dismiss(t.id)} />
          ))}
        </div>,
        document.body
      )}
    </ToastContext.Provider>
  )
}

/**
 * Hook to trigger toast notifications from any component.
 *
 * @example
 * const toast = useToast()
 * toast.success('Lead created!', 'Success')
 * toast.error('Something went wrong')
 */
export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')

  const { addToast, dismiss } = ctx

  return {
    toast:   addToast,
    success: (message, title) => addToast({ message, title, variant: 'success' }),
    error:   (message, title) => addToast({ message, title, variant: 'error' }),
    warning: (message, title) => addToast({ message, title, variant: 'warning' }),
    info:    (message, title) => addToast({ message, title, variant: 'info' }),
    dismiss,
  }
}
