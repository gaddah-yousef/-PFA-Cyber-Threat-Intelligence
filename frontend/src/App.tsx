import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { AdminRoute } from './components/AdminRoute'
import { ProtectedRoute } from './components/ProtectedRoute'
import { About } from './pages/About'
import { Alerts } from './pages/Alerts'
import { AssetDetails } from './pages/AssetDetails'
import { Assets } from './pages/Assets'
import { Login } from './pages/Login'
import { Overview } from './pages/Overview'
import { ReflexSheets } from './pages/ReflexSheets'
import { Sources } from './pages/Sources'
import { ThreatDetails } from './pages/ThreatDetails'
import { Threats } from './pages/Threats'
import { Users } from './pages/Users'

export default function App() {
  return (
    <Routes>
      <Route path="login" element={<Login />} />
      <Route
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Overview />} />
        <Route path="threats" element={<Threats />} />
        <Route path="threats/:id" element={<ThreatDetails />} />
        <Route path="alerts" element={<Alerts />} />
        <Route path="assets" element={<Assets />} />
        <Route path="assets/:id" element={<AssetDetails />} />
        <Route path="reflex-sheets" element={<ReflexSheets />} />
        <Route path="sources" element={<Sources />} />
        <Route path="users" element={<AdminRoute><Users /></AdminRoute>} />
        <Route path="about" element={<About />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
