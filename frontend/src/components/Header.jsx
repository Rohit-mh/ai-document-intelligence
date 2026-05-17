import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Badge } from './Common'

export const Header = ({ systemStatus = null }) => {
  const location = useLocation()
  const isActive = (path) => location.pathname === path

  return (
    <header className="bg-zinc-950 border-b border-zinc-900 sticky top-0 z-50">
      <div className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 bg-zinc-100 rounded-lg flex items-center justify-center text-zinc-950 group-hover:bg-white transition-colors">
              <span className="font-bold text-lg">DI</span>
            </div>
            <div className="hidden sm:block">
              <h1 className="font-bold text-sm text-zinc-100">
                Document Intelligence
              </h1>
              <p className="text-[10px] text-zinc-500 uppercase tracking-widest font-medium">Multi-Agent System</p>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="flex gap-4 sm:gap-8">
            {[
              { path: '/', label: 'Upload' },
              { path: '/chat', label: 'Chat' },
              { path: '/dashboard', label: 'Insights' },
              { path: '/status', label: 'Status' }
            ].map(link => (
              <Link
                key={link.path}
                to={link.path}
                className={`text-xs sm:text-sm font-medium transition-colors ${
                  isActive(link.path) 
                    ? 'text-zinc-100' 
                    : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Status Badge */}
          {systemStatus && (
            <div className="flex items-center gap-2">
              {systemStatus.status === 'healthy' || systemStatus.healthy ? (
                <div className="flex items-center gap-1.5 px-2 py-1 bg-emerald-500/10 rounded-full border border-emerald-500/20">
                   <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                   <span className="text-[10px] font-bold text-emerald-500 uppercase tracking-tighter">Live</span>
                </div>
              ) : (
                <Badge variant="red">Offline</Badge>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export const Footer = () => {
  return (
    <footer className="bg-zinc-950 border-t border-zinc-900 py-4 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <p className="text-center text-[10px] text-zinc-600 uppercase tracking-widest font-medium">
          Intelligence System v1.0 • Built with GitHub Models & ADK
        </p>
      </div>
    </footer>
  )
}
