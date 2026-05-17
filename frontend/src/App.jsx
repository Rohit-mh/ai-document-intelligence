import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { LandingPage, ChatPage } from './pages'
import { AuthProvider, useAuth } from './context/AuthContext'

function AppContent() {
  const { user, loading } = useAuth()

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
        {/* If user is logged in, "/" renders ChatPage. If not, "/" renders LandingPage */}
        <Route 
          path="/" 
          element={user ? <ChatPage /> : <LandingPage />} 
        />

        {/* Fallback all other routes to "/" */}
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
