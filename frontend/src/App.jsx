import { Route, Routes } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import ProblemDetail from './pages/ProblemDetail'
import Problems from './pages/Problems'
import Register from './pages/Register'
import Solve from './pages/Solve'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
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
            <ProblemDetail />
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
