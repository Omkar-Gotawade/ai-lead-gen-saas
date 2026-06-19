import React, { createContext, useContext, useState, useId } from 'react'

/* ─── Context ────────────────────────────────────────────────── */
const TabsCtx = createContext(null)

function useTabsCtx() {
  const ctx = useContext(TabsCtx)
  if (!ctx) throw new Error('Tabs sub-component must be used inside <Tabs>')
  return ctx
}

/* ─── Tabs (root) ────────────────────────────────────────────── */
/**
 * Compound Tabs component following the Context + compound-component pattern.
 *
 * @example
 * <Tabs defaultTab="profile">
 *   <TabList>
 *     <Tab id="profile" icon={User}>Profile</Tab>
 *     <Tab id="security" icon={Shield}>Security</Tab>
 *   </TabList>
 *   <TabPanel id="profile">…content…</TabPanel>
 *   <TabPanel id="security">…content…</TabPanel>
 * </Tabs>
 */
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
      className={`flex space-x-1 border-b border-ink-100 ${className}`}
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
        'flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px whitespace-nowrap',
        isActive
          ? 'border-brand-600 text-brand-700'
          : 'border-transparent text-ink-500 hover:text-ink-800 hover:border-ink-200',
        disabled ? 'opacity-40 cursor-not-allowed' : '',
      ].join(' ')}
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
