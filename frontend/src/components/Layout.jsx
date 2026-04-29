import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useState } from 'react'
import {
  Users,
  Search,
  Mail,
  BarChart2,
  Webhook,
  ShieldCheck,
  Settings,
  LogOut,
  Menu,
  X,
  Zap,
  CreditCard,
  ChevronDown,
} from 'lucide-react'

/* ─── Navigation items ─────────────────────────────────────── */
const mainNav = [
  { name: 'Leads',          to: '/leads',          icon: Users },
  { name: 'Discover',       to: '/discover-leads', icon: Search },
  { name: 'Campaigns',      to: '/campaigns',       icon: Mail },
  { name: 'Analytics',      to: '/metrics',         icon: BarChart2 },
  { name: 'Deliverability', to: '/deliverability',  icon: ShieldCheck },
  { name: 'Webhooks',       to: '/webhooks',        icon: Webhook },
]

const bottomNav = [
  { name: 'Settings', to: '/settings', icon: Settings },
  { name: 'Pricing',  to: '/pricing',  icon: CreditCard },
]

/* Helper: find the display name for the current path */
const allNav = [...mainNav, ...bottomNav]
function getPageTitle(pathname) {
  const match = allNav.find(
    (item) => pathname === item.to || pathname.startsWith(item.to + '/')
  )
  return match?.name ?? ''
}

/* ─── Sub-components ────────────────────────────────────────── */
function NavItem({ item, isActive, onClick }) {
  const Icon = item.icon
  return (
    <Link
      to={item.to}
      onClick={onClick}
      className={`group flex items-center gap-3 px-3 py-2 rounded-lg text-[13px] font-medium transition-all duration-200 select-none ${
        isActive
          ? 'bg-white/10 text-white'
          : 'text-sidebar-text hover:bg-white/5 hover:text-white'
      }`}
    >
      {/* Icon with active-state pill */}
      <span
        className={`w-6 h-6 shrink-0 flex items-center justify-center rounded-md transition-all duration-200 ${
          isActive
            ? 'bg-brand-500/25 text-brand-300 scale-105'
            : 'text-sidebar-muted group-hover:text-white/70'
        }`}
      >
        <Icon className="w-[15px] h-[15px]" />
      </span>

      <span className="truncate flex-1">{item.name}</span>

      {/* Active dot */}
      {isActive && (
        <span className="w-1.5 h-1.5 rounded-full bg-brand-400 shrink-0 opacity-80" />
      )}
    </Link>
  )
}

/* ─── Sidebar ───────────────────────────────────────────────── */
function Sidebar({ onClose }) {
  const { logout, user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  const isActive = (path) =>
    location.pathname === path || location.pathname.startsWith(path + '/')

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const initials = user?.email?.[0]?.toUpperCase() || 'U'
  const email = user?.email || ''

  return (
    <aside className="flex flex-col w-60 h-full bg-sidebar-bg border-r border-sidebar-border shadow-sidebar sidebar-scroll overflow-y-auto">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-4 h-[60px] shrink-0 border-b border-sidebar-border group cursor-default">
        <div className="w-8 h-8 rounded-lg bg-gradient-brand flex items-center justify-center shadow-md shrink-0 transition-transform duration-200 group-hover:scale-105">
          <Zap className="w-4 h-4 text-white" />
        </div>
        <span className="text-white font-bold text-[15px] tracking-tight">Lead Gen AI</span>
        {/* Mobile close */}
        {onClose && (
          <button
            onClick={onClose}
            className="ml-auto text-sidebar-muted hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Main nav */}
      <nav className="flex-1 px-2 pt-4 pb-2 space-y-0.5">
        <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest text-sidebar-muted">
          Main
        </p>
        {mainNav.map((item) => (
          <NavItem key={item.to} item={item} isActive={isActive(item.to)} onClick={onClose} />
        ))}

        <div className="divider-dark" />

        <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest text-sidebar-muted">
          Account
        </p>
        {bottomNav.map((item) => (
          <NavItem key={item.to} item={item} isActive={isActive(item.to)} onClick={onClose} />
        ))}
      </nav>

      {/* User footer */}
      <div className="px-2 pb-3 shrink-0 border-t border-sidebar-border pt-2">
        <div className="relative">
          <button
            onClick={() => setUserMenuOpen((v) => !v)}
            className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg hover:bg-sidebar-hover transition-colors duration-150"
          >
            <div className="w-7 h-7 rounded-full bg-gradient-brand flex items-center justify-center text-white text-xs font-bold shrink-0 shadow-sm">
              {initials}
            </div>
            <div className="flex-1 text-left min-w-0">
              <p className="text-[12px] font-medium text-sidebar-text truncate">{email}</p>
            </div>
            <ChevronDown className={`w-3.5 h-3.5 text-sidebar-muted shrink-0 transition-transform duration-150 ${userMenuOpen ? 'rotate-180' : ''}`} />
          </button>

          {userMenuOpen && (
            <>
              <div className="fixed inset-0 z-10" onClick={() => setUserMenuOpen(false)} />
              <div className="absolute bottom-full left-0 right-0 mb-1 bg-[#181b2b] border border-sidebar-border rounded-lg shadow-card-lg py-1 z-20 animate-fade-up">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2.5 px-3 py-2 text-[13px] text-red-400 hover:bg-white/5 transition-colors"
                >
                  <LogOut className="w-4 h-4 shrink-0" />
                  Sign out
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </aside>
  )
}

/* ─── Layout ────────────────────────────────────────────────── */
const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const pageTitle = getPageTitle(location.pathname)

  return (
    <div className="flex h-screen bg-canvas overflow-hidden">
      {/* Accessibility: skip to main content */}
      <a
        href="#main-content"
        className="skip-link"
      >
        Skip to content
      </a>

      {/* Desktop sidebar — always visible */}
      <div className="hidden md:flex shrink-0">
        <Sidebar />
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        >
          <div className="absolute inset-0 bg-ink-900/60 backdrop-blur-sm modal-backdrop" />
        </div>
      )}
      <div
        className={`fixed inset-y-0 left-0 z-50 md:hidden w-60 transition-transform duration-250 ease-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <Sidebar onClose={() => setSidebarOpen(false)} />
      </div>

      {/* Main area */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Mobile topbar */}
        <header className="md:hidden flex items-center gap-3 h-14 px-4 bg-sidebar-bg border-b border-sidebar-border shrink-0">
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-sidebar-text hover:text-white transition-colors"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md bg-gradient-brand flex items-center justify-center">
              <Zap className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="text-white font-semibold text-sm">
              {pageTitle || 'Lead Gen AI'}
            </span>
          </div>
        </header>

        {/* Page content */}
        <main id="main-content" className="flex-1 overflow-y-auto" tabIndex={-1}>
          <div className="page-enter">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout

