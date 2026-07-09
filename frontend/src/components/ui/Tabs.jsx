import React, { createContext, useContext, useState } from 'react'

/* ─── Context ────────────────────────────────────────────────── */
const TabsCtx = createContext(null)

function useTabsCtx() {
  const ctx = useContext(TabsCtx)
  if (!ctx) throw new Error('Tabs sub-component must be used inside <Tabs>')
  return ctx
}

/* ─── Tabs (root) ────────────────────────────────────────────── */
export function Tabs({ children, defaultTab, onChange, className = '' }) {
  const [active, setActive] = useState(defaultTab)

  const handleChange = (id) => {
    setActive(id)
    onChange?.(id)
  }

  return (
    <TabsCtx.Provider value={{ active, setActive: handleChange }}>
      <div className={className}>{children}</div>
    </TabsCtx.Provider>
  )
}

/* ─── TabList ────────────────────────────────────────────────── */
export function TabList({ children, className = '' }) {
  return (
    <div
      role="tablist"
      className={`flex space-x-0.5 ${className}`}
      style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}
    >
      {children}
    </div>
  )
}

/* ─── Tab ────────────────────────────────────────────────────── */
export function Tab({ id, children, icon: Icon, disabled = false }) {
  const { active, setActive } = useTabsCtx()
  const isActive = active === id

  return (
    <button
      role="tab"
      aria-selected={isActive}
      aria-controls={`tabpanel-${id}`}
      id={`tab-${id}`}
      disabled={disabled}
      onClick={() => setActive(id)}
      className={[
        'flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 transition-all duration-150 -mb-px whitespace-nowrap',
        disabled ? 'opacity-40 cursor-not-allowed' : '',
      ].join(' ')}
      style={isActive
        ? { borderColor: '#f59e0b', color: '#f59e0b' }
        : { borderColor: 'transparent', color: '#343a52' }
      }
      onMouseEnter={e => { if (!isActive && !disabled) { e.currentTarget.style.color = '#8b8fa8'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)'; } }}
      onMouseLeave={e => { if (!isActive) { e.currentTarget.style.color = '#343a52'; e.currentTarget.style.borderColor = 'transparent'; } }}
    >
      {Icon && <Icon className="h-3.5 w-3.5 shrink-0" />}
      {children}
    </button>
  )
}

/* ─── TabPanel ───────────────────────────────────────────────── */
export function TabPanel({ id, children, className = '' }) {
  const { active } = useTabsCtx()
  if (active !== id) return null

  return (
    <div
      role="tabpanel"
      id={`tabpanel-${id}`}
      aria-labelledby={`tab-${id}`}
      className={`tab-panel-enter ${className}`}
    >
      {children}
    </div>
  )
}
