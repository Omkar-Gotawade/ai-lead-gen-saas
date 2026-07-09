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
  { name: 'Campaigns',      to: '/campaigns',      icon: Mail },
  { name: 'Analytics',      to: '/metrics',        icon: BarChart2 },
  { name: 'Deliverability', to: '/deliverability', icon: ShieldCheck },
  { name: 'Webhooks',       to: '/webhooks',       icon: Webhook },
]

const bottomNav = [
  { name: 'Settings', to: '/settings', icon: Settings },
  { name: 'Pricing',  to: '/pricing',  icon: CreditCard },
]

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
      className={`group relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] font-medium transition-all duration-200 select-none ${
        isActive
          ? 'bg-white/[0.07] text-white'
          : 'text-sidebar-text hover:bg-white/[0.04] hover:text-white/80'
      }`}
    >
      {/* Active left-rail glow */}
      {isActive && (
        <span
          className="absolute left-0 top-[18%] bottom-[18%] w-[2.5px] rounded-r-full"
          style={{
            background: 'linear-gradient(180deg, #fbbf24, #d97706)',
            boxShadow: '0 0 10px rgba(245,158,11,0.7)',
          }}
        />
      )}

      {/* Icon */}
      <span
        className={`w-6 h-6 shrink-0 flex items-center justify-center rounded-md transition-all duration-200 ${
          isActive
            ? 'text-amber-400'
            : 'text-sidebar-muted group-hover:text-white/60'
        }`}
        style={isActive ? {
          background: 'rgba(245,158,11,0.12)',
          boxShadow: '0 0 8px rgba(245,158,11,0.15)',
        } : {}}
      >
        <Icon className="w-[15px] h-[15px]" />
      </span>

      <span className="truncate flex-1">{item.name}</span>

      {/* Active amber dot */}
      {isActive && (
        <span
          className="w-1.5 h-1.5 rounded-full shrink-0"
          style={{ background: '#f59e0b', boxShadow: '0 0 6px rgba(245,158,11,0.8)' }}
        />
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
    <aside
      className="flex flex-col w-60 h-full sidebar-scroll overflow-y-auto"
      style={{
        background: '#0a0b0f',
        borderRight: '1px solid rgba(255,255,255,0.05)',
        boxShadow: '4px 0 24px rgba(0,0,0,0.4)',
      }}
    >
      {/* Logo */}
      <div
        className="flex items-center gap-2.5 px-4 h-[60px] shrink-0 group cursor-default"
        style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}
      >
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 transition-transform duration-200 group-hover:scale-105"
          style={{
            background: 'linear-gradient(135deg, #d97706, #f59e0b)',
            boxShadow: '0 0 0 1px rgba(245,158,11,0.3), 0 4px 12px rgba(217,119,6,0.4)',
          }}
        >
          <Zap className="w-4 h-4 text-white" />
        </div>
        <span
          className="font-bold text-[15px] tracking-tight text-white"
          style={{ fontFamily: 'Syne, system-ui, sans-serif' }}
        >
          Lead Gen AI
        </span>
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
      <div
        className="px-2 pb-3 shrink-0 pt-2"
        style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}
      >
        <div className="relative">
          <button
            onClick={() => setUserMenuOpen((v) => !v)}
            className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg transition-colors duration-150"
            style={{ ':hover': { background: 'rgba(255,255,255,0.04)' } }}
            onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.04)'}
            onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
          >
            {/* Avatar with amber ring */}
            <div
              className="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0"
              style={{
                background: 'linear-gradient(135deg, #d97706, #f59e0b)',
                boxShadow: '0 0 0 2px rgba(245,158,11,0.2)',
              }}
            >
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
              <div
                className="absolute bottom-full left-0 right-0 mb-1 rounded-lg py-1 z-20 animate-fade-up"
                style={{
                  background: '#111220',
                  border: '1px solid rgba(255,255,255,0.08)',
                  boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
                }}
              >
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-2.5 px-3 py-2 text-[13px] text-red-400 hover:bg-white/[0.04] transition-colors"
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
    <div className="flex h-screen overflow-hidden" style={{ background: '#0d0e18' }}>
      {/* Accessibility: skip to main content */}
      <a href="#main-content" className="skip-link">
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
          <div className="absolute inset-0 bg-black/70 backdrop-blur-sm modal-backdrop" />
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
        <header
          className="md:hidden flex items-center gap-3 h-14 px-4 shrink-0"
          style={{
            background: '#0a0b0f',
            borderBottom: '1px solid rgba(255,255,255,0.05)',
          }}
        >
          <button
            onClick={() => setSidebarOpen(true)}
            className="text-sidebar-text hover:text-white transition-colors"
            aria-label="Open navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-2">
            <div
              className="w-6 h-6 rounded-md flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #d97706, #f59e0b)' }}
            >
              <Zap className="w-3.5 h-3.5 text-white" />
            </div>
            <span
              className="text-white font-semibold text-sm"
              style={{ fontFamily: 'Syne, system-ui, sans-serif' }}
            >
              {pageTitle || 'Lead Gen AI'}
            </span>
          </div>
        </header>

        {/* Page content */}
        <main
          id="main-content"
          className="flex-1 overflow-y-auto"
          style={{ background: '#0d0e18' }}
          tabIndex={-1}
        >
          <div className="page-enter">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

export default Layout
