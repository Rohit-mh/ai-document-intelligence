import React, { useState } from 'react'
import { Plus, Mic, ArrowUp, Zap, FileText, Layout, MessageSquare, Shield, Globe, Sparkles } from 'lucide-react'
import { AuthModal } from '../components/AuthModal'
import { motion } from 'framer-motion'

export const LandingPage = () => {
  const [isAuthOpen, setIsAuthOpen] = useState(false)
  const [authMode, setAuthMode] = useState('login')

  const openAuth = (mode) => {
    setAuthMode(mode)
    setIsAuthOpen(true)
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col relative overflow-hidden">
      {/* Dynamic Background */}
      <div className="absolute inset-0 pointer-events-none">
        <motion.div 
          animate={{ 
            scale: [1, 1.2, 1],
            opacity: [0.1, 0.15, 0.1]
          }}
          transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
          className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] bg-purple-600/10 blur-[120px] rounded-full" 
        />
        <motion.div 
          animate={{ 
            x: [-100, 100, -100],
            y: [-50, 50, -50]
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
          className="absolute bottom-0 right-0 w-[600px] h-[600px] bg-blue-600/5 blur-[100px] rounded-full" 
        />
      </div>
      
      {/* Header */}
      <motion.header 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="p-6 flex items-center justify-between relative z-50 max-w-7xl mx-auto w-full"
      >
        <div className="flex items-center gap-2.5 group cursor-pointer">
          <motion.div 
            whileHover={{ scale: 1.1, rotate: 5 }}
            className="w-9 h-9 bg-zinc-100 rounded-xl flex items-center justify-center text-zinc-950 font-black shadow-[0_0_20px_rgba(255,255,255,0.1)]"
          >
            DI
          </motion.div>
          <span className="font-bold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-zinc-400">
            Document Intelligence
          </span>
        </div>
        <div className="flex items-center gap-4">
          <button 
            id="login-button-top"
            onClick={() => openAuth('login')}
            className="px-5 py-2.5 text-sm font-bold text-zinc-400 hover:text-white transition-all cursor-pointer active:scale-95"
          >
            Log in
          </button>
          <button 
            id="signup-button-top"
            onClick={() => openAuth('signup')}
            className="px-6 py-2.5 bg-zinc-100 text-zinc-950 rounded-full text-sm font-black shadow-xl shadow-white/10 hover:bg-white hover:scale-105 transition-all cursor-pointer active:scale-95"
          >
            Sign up
          </button>
        </div>
      </motion.header>

      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 relative z-10 -mt-16 max-w-5xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center mb-16"
        >
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-xs font-bold text-zinc-400 mb-6"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            <span>AI-POWERED ANALYSIS</span>
          </motion.div>
          <h1 className="text-6xl md:text-7xl font-bold tracking-tight leading-[1.1] mb-6">
            What are you <br />
            <span className="text-zinc-500">working on?</span>
          </h1>
        </motion.div>

        {/* Search Bar Area */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="w-full max-w-2xl group"
        >
          <div className="bg-zinc-900/40 backdrop-blur-2xl border border-zinc-800/50 rounded-[2rem] p-4 shadow-[0_32px_64px_-16px_rgba(0,0,0,0.5)] focus-within:border-zinc-700/50 transition-all focus-within:shadow-[0_32px_64px_-16px_rgba(0,0,0,0.6)]">
            <div className="flex items-center gap-3 mb-5 px-2">
              <motion.button 
                whileHover={{ scale: 1.1, backgroundColor: 'rgba(39, 39, 42, 0.8)' }}
                whileTap={{ scale: 0.9 }}
                onClick={() => openAuth('login')}
                className="p-2.5 bg-zinc-800/50 rounded-full text-zinc-400 transition-colors"
              >
                <Plus className="w-6 h-6" />
              </motion.button>
              <input 
                type="text"
                readOnly
                onClick={() => openAuth('login')}
                placeholder="Ask anything about your documents..."
                className="flex-1 bg-transparent border-none text-zinc-100 placeholder-zinc-500 text-xl py-2 focus:ring-0 cursor-pointer"
              />
              <div className="flex items-center gap-2">
                <Mic className="w-5 h-5 text-zinc-500 hover:text-zinc-300 cursor-pointer transition-colors" />
                <motion.button 
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => openAuth('login')}
                  className="p-2.5 bg-zinc-800 text-zinc-600 rounded-full cursor-not-allowed"
                >
                  <ArrowUp className="w-5 h-5 stroke-[3px]" />
                </motion.button>
              </div>
            </div>

            {/* Feature Pills */}
            <motion.div 
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              className="flex flex-wrap gap-2.5 pt-1 px-1"
            >
              {[
                { icon: Zap, label: 'Analyze PDF', color: 'text-amber-400' },
                { icon: MessageSquare, label: 'Deep Research', color: 'text-blue-400' },
                { icon: FileText, label: 'Summary', color: 'text-rose-400' },
                { icon: Layout, label: 'Visual Insights', color: 'text-emerald-400' }
              ].map((f, i) => (
                <motion.button 
                  key={i}
                  variants={itemVariants}
                  whileHover={{ scale: 1.05, y: -2, backgroundColor: 'rgba(24, 24, 27, 0.8)' }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => openAuth('login')}
                  className="flex items-center gap-2.5 px-4 py-2 bg-zinc-900/80 border border-zinc-800/50 rounded-2xl text-xs font-bold text-zinc-400 hover:border-zinc-700 transition-all shadow-lg"
                >
                  <f.icon className={`w-3.5 h-3.5 ${f.color}`} />
                  {f.label}
                </motion.button>
              ))}
            </motion.div>
          </div>
        </motion.div>

        {/* Feature Highlights */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-12 w-full max-w-4xl"
        >
          <div className="flex flex-col items-center text-center group">
            <div className="w-12 h-12 bg-zinc-900 border border-zinc-800 rounded-2xl flex items-center justify-center mb-4 group-hover:border-zinc-700 transition-colors shadow-xl">
              <Shield className="w-6 h-6 text-zinc-400" />
            </div>
            <h3 className="font-bold text-sm mb-2 text-zinc-200">Secure & Private</h3>
            <p className="text-xs text-zinc-500 leading-relaxed">Your data is encrypted and never used for training models.</p>
          </div>
          <div className="flex flex-col items-center text-center group">
            <div className="w-12 h-12 bg-zinc-900 border border-zinc-800 rounded-2xl flex items-center justify-center mb-4 group-hover:border-zinc-700 transition-colors shadow-xl">
              <Globe className="w-6 h-6 text-zinc-400" />
            </div>
            <h3 className="font-bold text-sm mb-2 text-zinc-200">Multi-Modal</h3>
            <p className="text-xs text-zinc-500 leading-relaxed">Extract text, charts, and tables from any document type.</p>
          </div>
          <div className="flex flex-col items-center text-center group">
            <div className="w-12 h-12 bg-zinc-900 border border-zinc-800 rounded-2xl flex items-center justify-center mb-4 group-hover:border-zinc-700 transition-colors shadow-xl">
              <Sparkles className="w-6 h-6 text-zinc-400" />
            </div>
            <h3 className="font-bold text-sm mb-2 text-zinc-200">AI Reasoning</h3>
            <p className="text-xs text-zinc-500 leading-relaxed">Advanced RAG ensures answers are grounded in your data.</p>
          </div>
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="p-8 text-center relative z-10">
        <p className="text-zinc-600 text-[10px] uppercase tracking-widest font-bold mb-4">
          By messaging Document Intelligence, you agree to our Terms and Privacy Policy.
        </p>
        <div className="flex justify-center gap-8 text-[10px] text-zinc-700 font-bold uppercase tracking-[0.2em]">
          <a href="#" className="hover:text-zinc-500 transition-colors">Twitter</a>
          <a href="#" className="hover:text-zinc-500 transition-colors">GitHub</a>
          <a href="#" className="hover:text-zinc-500 transition-colors">Discord</a>
        </div>
      </footer>

      <AuthModal 
        isOpen={isAuthOpen} 
        onClose={() => setIsAuthOpen(false)} 
        initialMode={authMode} 
      />
    </div>
  )
}
