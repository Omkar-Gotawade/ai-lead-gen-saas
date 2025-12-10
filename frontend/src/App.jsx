import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Leads from './pages/Leads'
import Campaigns from './pages/Campaigns'
import CampaignEditor from './pages/CampaignEditor'
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
            <Route path="campaigns" element={<Campaigns />} />
            <Route path="campaigns/:campaignId" element={<CampaignEditor />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
