import { Navigate, Route, Routes } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Problems from './pages/Problems'
import Register from './pages/Register'
import Roadmap from './pages/Roadmap'
import Solve from './pages/Solve'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      {/* The roadmap is the default landing page after login. */}
      <Route path="/" element={<Navigate to="/roadmap" replace />} />
      <Route
        path="/campaign"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/roadmap"
        element={
          <ProtectedRoute>
            <Roadmap />
          </ProtectedRoute>
        }
      />
      <Route
        path="/problems"
        element={
          <ProtectedRoute>
            <Problems />
          </ProtectedRoute>
        }
      />
      <Route
        path="/problems/:slug"
        element={
          <ProtectedRoute>
            <Solve />
          </ProtectedRoute>
        }
      />
      <Route
        path="/problems/:slug/solve"
        element={
          <ProtectedRoute>
            <Solve />
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}
