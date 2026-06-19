import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import { AuthProvider } from './context/AuthContext'
import { ToastProvider } from './context/ToastContext'
import ProtectedRoute from './components/ProtectedRoute'
import ErrorBoundary from './components/ErrorBoundary'
import LoadingSpinner from './components/ui/LoadingSpinner'
import Layout from './components/Layout'

/* ─── Lazy-loaded pages for code splitting ──────────────────── */
const Login            = lazy(() => import('./pages/Login'))
const Signup           = lazy(() => import('./pages/Signup'))
const LandingPage      = lazy(() => import('./pages/LandingPage'))
const Leads            = lazy(() => import('./pages/Leads'))
const Campaigns        = lazy(() => import('./pages/Campaigns'))
const CampaignEditor   = lazy(() => import('./pages/CampaignEditor'))
const MetricsDashboard = lazy(() => import('./pages/MetricsDashboard'))
const WebhooksDebug    = lazy(() => import('./pages/WebhooksDebug'))
const Deliverability   = lazy(() => import('./pages/Deliverability'))
const DiscoverLeadsPage = lazy(() => import('./pages/DiscoverLeadsPage'))
const Settings         = lazy(() => import('./pages/Settings'))
const Pricing          = lazy(() => import('./pages/Pricing'))

/* ─── Inline page-load fallback ────────────────────────────── */
const PageFallback = () => (
  <div className="flex items-center justify-center h-full min-h-[400px]">
    <LoadingSpinner size="md" text="Loading…" />
  </div>
)

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <ToastProvider>
          <Router>
            <Suspense fallback={<PageFallback />}>
              <Routes>
                <Route path="/"       element={<LandingPage />} />
                <Route path="/login"  element={<Login />} />
                <Route path="/signup" element={<Signup />} />

                {/* Internal App */}
                <Route
                  path="/*"
                  element={
                    <ProtectedRoute>
                      <Layout />
                    </ProtectedRoute>
                  }
                >
                  <Route path="leads"              element={<Leads />} />
                  <Route path="discover-leads"     element={<DiscoverLeadsPage />} />
                  <Route path="campaigns"          element={<Campaigns />} />
                  <Route path="campaigns/:campaignId" element={<CampaignEditor />} />
                  <Route path="metrics"            element={<MetricsDashboard />} />
                  <Route path="webhooks"           element={<WebhooksDebug />} />
                  <Route path="deliverability"     element={<Deliverability />} />
                  <Route path="pricing"            element={<Pricing />} />
                  <Route path="settings"           element={<Settings />} />
                  
                  {/* Catch-all for unknown protected routes */}
                  <Route path="*" element={<Navigate to="/leads" replace />} />
                </Route>
              </Routes>
            </Suspense>
          </Router>
        </ToastProvider>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
