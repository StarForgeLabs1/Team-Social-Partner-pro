import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Dashboard from './components/Dashboard/Dashboard';
import ContentScheduler from './components/Dashboard/ContentScheduler';
import Analytics from './components/Dashboard/Analytics';
import SocialAccounts from './components/Dashboard/SocialAccounts';
import ContentLibrary from './components/Dashboard/ContentLibrary';
import { isAuthenticated } from './utils/auth';

function App() {
  const [isAuth, setIsAuth] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setIsAuth(isAuthenticated());
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="relative">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-white"></div>
          <div className="absolute inset-0 rounded-full h-32 w-32 border-r-2 border-purple-400 animate-pulse"></div>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(10px)',
              color: '#fff',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '12px',
            },
          }}
        />
        <Routes>
          <Route 
            path="/login" 
            element={!isAuth ? <Login setIsAuth={setIsAuth} /> : <Navigate to="/dashboard" />} 
          />
          <Route 
            path="/register" 
            element={!isAuth ? <Register setIsAuth={setIsAuth} /> : <Navigate to="/dashboard" />} 
          />
          <Route 
            path="/dashboard" 
            element={isAuth ? <Dashboard setIsAuth={setIsAuth} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/scheduler" 
            element={isAuth ? <ContentScheduler setIsAuth={setIsAuth} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/analytics" 
            element={isAuth ? <Analytics setIsAuth={setIsAuth} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/accounts" 
            element={isAuth ? <SocialAccounts setIsAuth={setIsAuth} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/content" 
            element={isAuth ? <ContentLibrary setIsAuth={setIsAuth} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/" 
            element={<Navigate to={isAuth ? "/dashboard" : "/login"} />} 
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
