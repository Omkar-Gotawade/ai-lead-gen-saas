import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Leads from './pages/Leads'
import Campaigns from './pages/Campaigns'
import CampaignEditor from './pages/CampaignEditor'
import MetricsDashboard from './pages/MetricsDashboard'
import WebhooksDebug from './pages/WebhooksDebug'
import Deliverability from './pages/Deliverability'
import DiscoverLeadsPage from './pages/DiscoverLeadsPage'
import DeliverabilityPage from './pages/DeliverabilityPage'
import Layout from './components/Layout'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/leads" replace />} />
            <Route path="leads" element={<Leads />} />
            <Route path="discover-leads" element={<DiscoverLeadsPage />} />
            <Route path="campaigns" element={<Campaigns />} />
            <Route path="campaigns/:campaignId" element={<CampaignEditor />} />
            <Route path="metrics" element={<MetricsDashboard />} />
            <Route path="webhooks" element={<WebhooksDebug />} />
            <Route path="deliverability" element={<Deliverability />} />
            <Route path="deliverability-tools" element={<DeliverabilityPage />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
