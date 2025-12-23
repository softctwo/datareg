import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import DataAssets from './pages/DataAssets'
import Scenarios from './pages/Scenarios'
import RiskAssessments from './pages/RiskAssessments'
import Approvals from './pages/Approvals'
import AuditLogs from './pages/AuditLogs'
import Roles from './pages/Roles'
import UserRoles from './pages/UserRoles'
import Users from './pages/Users'
import Interception from './pages/Interception'
import Notifications from './pages/Notifications'
import SystemConfig from './pages/SystemConfig'

// 路由守卫组件
const PrivateRoute: React.FC<{ children: React.ReactElement }> = ({ children }) => {
  const token = localStorage.getItem('token')
  return token ? children : <Navigate to="/login" replace />
}

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <PrivateRoute>
              <AppLayout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/data-assets" element={<DataAssets />} />
                  <Route path="/scenarios" element={<Scenarios />} />
                  <Route path="/risk-assessments" element={<RiskAssessments />} />
                  <Route path="/approvals" element={<Approvals />} />
                  <Route path="/audit-logs" element={<AuditLogs />} />
                  <Route path="/roles" element={<Roles />} />
                  <Route path="/user-roles" element={<UserRoles />} />
                  <Route path="/users" element={<Users />} />
                  <Route path="/interception" element={<Interception />} />
                  <Route path="/notifications" element={<Notifications />} />
                  <Route path="/system-config" element={<SystemConfig />} />
                </Routes>
              </AppLayout>
            </PrivateRoute>
          }
        />
      </Routes>
    </Router>
  )
}

export default App

