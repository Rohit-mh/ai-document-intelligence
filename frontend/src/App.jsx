import React from 'react'
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { LandingPage, ChatPage, DashboardPage, StatusPage, UploadPage } from './pages'
import { MainLayout } from './layouts/MainLayout'
import { AuthProvider, useAuth } from './context/AuthContext'

function AppContent() {
  const { user, loading } = useAuth()
  const navigate = useNavigate()

  if (loading) {
    return (
      <div className="bg-zinc-950 min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-zinc-700 border-t-zinc-100 rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="bg-zinc-950 min-h-screen text-zinc-100 font-sans selection:bg-purple-500/30">
      <Routes>
        {/* If user is logged in, "/" renders UploadPage inside MainLayout.
            If not, "/" renders LandingPage */}
        <Route 
          path="/" 
          element={
            user ? (
              <MainLayout>
                <UploadPage onDocumentUploaded={() => navigate('/dashboard')} />
              </MainLayout>
            ) : (
              <LandingPage />
            )
          } 
        />

        {/* /chat is the ChatPage (full-screen, no MainLayout wrapper needed) */}
        <Route 
          path="/chat" 
          element={user ? <ChatPage /> : <Navigate to="/" replace />} 
        />

        {/* /dashboard is the DashboardPage inside MainLayout */}
        <Route 
          path="/dashboard" 
          element={
            user ? (
              <MainLayout>
                <DashboardPage />
              </MainLayout>
            ) : (
              <Navigate to="/" replace />
            )
          } 
        />

        {/* /status is the StatusPage inside MainLayout */}
        <Route 
          path="/status" 
          element={
            user ? (
              <MainLayout>
                <StatusPage />
              </MainLayout>
            ) : (
              <Navigate to="/" replace />
            )
          } 
        />

        {/* Fallback to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
