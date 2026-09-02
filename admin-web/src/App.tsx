import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, Ticket, LogOut, Users as UsersIcon } from 'lucide-react';
import { authStorage } from './lib/authStorage';
import './App.css';

import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Vouchers from './pages/Vouchers';
import Users from './pages/Users';

// Protected Route Wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = authStorage.getItem('token');
  const role = authStorage.getItem('role');
  
  if (!token || role !== 'admin') {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// Sidebar Layout
const AdminLayout = ({ children }: { children: React.ReactNode }) => {
  const location = useLocation();
  
  const handleLogout = () => {
    authStorage.removeItem('token');
    authStorage.removeItem('role');
    window.location.href = '/login';
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="sidebar-header">
          <h2>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: 16 }}>
              PP
            </div>
            PricePilot
          </h2>
        </div>
        
        <div className="nav-links">
          <a href="/dashboard" className={`nav-item ${location.pathname === '/dashboard' ? 'active' : ''}`}>
            <LayoutDashboard size={20} />
            Dashboard
          </a>
          <a href="/users" className={`nav-item ${location.pathname === '/users' ? 'active' : ''}`}>
            <UsersIcon size={20} />
            Users
          </a>
          <a href="/vouchers" className={`nav-item ${location.pathname === '/vouchers' ? 'active' : ''}`}>
            <Ticket size={20} />
            Vouchers
          </a>
        </div>

        <button className="logout-btn" onClick={handleLogout}>
          <LogOut size={20} />
          Sign Out
        </button>
      </div>

      <div className="main-content">
        <div className="topbar">
          <div style={{ fontWeight: 500 }}>Admin Portal</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 36, height: 36, borderRadius: 18, background: '#E5E7EB', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600 }}>
              A
            </div>
            <span>Administrator</span>
          </div>
        </div>
        {children}
      </div>
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <AdminLayout>
              <Dashboard />
            </AdminLayout>
          </ProtectedRoute>
        } />
        
        <Route path="/vouchers" element={
          <ProtectedRoute>
            <AdminLayout>
              <Vouchers />
            </AdminLayout>
          </ProtectedRoute>
        } />
        
        <Route path="/users" element={
          <ProtectedRoute>
            <AdminLayout>
              <Users />
            </AdminLayout>
          </ProtectedRoute>
        } />

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
