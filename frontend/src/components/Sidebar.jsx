import React, { useState, useEffect } from 'react'
import { Plus, MessageSquare, Search, Settings, HelpCircle, LogOut, User } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import apiClient from '../services/apiClient'

export const Sidebar = ({ onSelectSession, currentSessionId, onNewChat }) => {
  const { user, logout } = useAuth()
  const [sessions, setSessions] = useState([])

  useEffect(() => {
    if (user) {
      fetchSessions()
    }
  }, [user])

  const fetchSessions = async () => {
    try {
      const res = await apiClient.get('/sessions')
      setSessions(res.data)
    } catch (err) {
      console.error("Failed to fetch sessions", err)
    }
  }

  return (
    <div className="w-64 bg-zinc-950 h-screen flex flex-col border-r border-zinc-800 text-zinc-300">
      {/* New Chat Button */}
      <div className="p-3">
        <button 
          onClick={onNewChat}
          className="w-full flex items-center gap-3 px-3 py-3 rounded-lg border border-zinc-800 hover:bg-zinc-900 transition-colors text-sm font-medium text-zinc-100"
        >
          <Plus className="w-4 h-4" />
          New chat
        </button>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto px-2 space-y-1 scrollbar-hide">
        <div className="px-3 py-2 text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Recent</div>
        {sessions.map(session => (
          <button
            key={session.id}
            onClick={() => onSelectSession(session.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm truncate transition-colors ${
              currentSessionId === session.id ? 'bg-zinc-900 text-zinc-100' : 'hover:bg-zinc-900/50'
            }`}
          >
            <MessageSquare className="w-4 h-4 flex-shrink-0 text-zinc-500" />
            <span className="truncate">{session.title}</span>
          </button>
        ))}
      </div>

      {/* Bottom Actions */}
      <div className="p-2 border-t border-zinc-900 space-y-1">
        <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm hover:bg-zinc-900 transition-colors">
          <User className="w-4 h-4" />
          Upgrade Plan
        </button>
        <button className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm hover:bg-zinc-900 transition-colors">
          <Settings className="w-4 h-4" />
          Settings
        </button>
        <button 
          onClick={logout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-rose-400 hover:bg-rose-500/10 transition-colors mt-2"
        >
          <LogOut className="w-4 h-4" />
          Log out
        </button>
      </div>
    </div>
  )
}
