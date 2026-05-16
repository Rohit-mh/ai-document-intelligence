import React from 'react'
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
      {user ? <ChatPage /> : <LandingPage />}
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
