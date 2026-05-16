import React, { useState, useRef, useEffect } from 'react'
import { LoadingSpinner, Alert } from '../components'
import { askQuestion, getConciseSummary, getInsights, uploadDocument } from '../services'
import apiClient from '../services/apiClient'
import { 
  Plus, 
  ArrowUp, 
  FileText, 
  Lightbulb, 
  Paperclip,
  CheckCircle2,
  XCircle,
  Info,
  X,
  History
} from 'lucide-react'
import { useNotification } from '../hooks'
import ReactMarkdown from 'react-markdown'
import { Sidebar } from '../components/Sidebar'
import { useAuth } from '../context/AuthContext'
import { motion, AnimatePresence } from 'framer-motion'

export const ChatPage = () => {
  const { user } = useAuth()
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [userInput, setUserInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedDocumentId, setSelectedDocumentId] = useState(null)
  const [documents, setDocuments] = useState([])
  
  const messagesEndRef = useRef(null)
  const fileInputRef = useRef(null)
  const { notification, showNotification } = useNotification()

  // Load documents on mount
  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const res = await apiClient.get('/stats')
      if (res.data && res.data.documents) {
        setDocuments(res.data.documents)
      }
    } catch (err) {
      console.error("Failed to fetch documents", err)
    }
  }

  const loadSession = async (id) => {
    setIsLoading(true)
    setSessionId(id)
    try {
      const res = await apiClient.get(`/sessions/${id}/messages`)
      setMessages(res.data.map(m => ({
        text: m.content,
        isUser: m.role === 'user',
        timestamp: new Date(m.timestamp),
        attachedDoc: m.attached_doc_id ? { id: m.attached_doc_id, name: 'Attached Document' } : null
      })))
    } catch (err) {
      setError("Failed to load conversation")
    } finally {
      setIsLoading(false)
    }
  }

  const handleNewChat = () => {
    setSessionId(null)
    setMessages([])
    setSelectedDocumentId(null)
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (customInput = null) => {
    const input = customInput || userInput
    if (!input.trim() || isLoading) return

    let currentSessionId = sessionId
    
    // Create new session if needed
    if (!currentSessionId) {
      try {
        const sessionRes = await apiClient.post('/sessions', { title: input.trim().substring(0, 30) })
        currentSessionId = sessionRes.data.id
        setSessionId(currentSessionId)
      } catch (err) {
        setError("Failed to create session")
        return
      }
    }

    // Add user message to UI
    const userMsg = {
      text: input.trim(),
      isUser: true,
      timestamp: new Date(),
      attachedDoc: selectedDocumentId ? documents.find(d => d.id === selectedDocumentId) : null
    }
    setMessages(prev => [...prev, userMsg])
    if (!customInput) setUserInput('')
    
    const docIdForRequest = selectedDocumentId
    setSelectedDocumentId(null)
    setIsLoading(true)
    setError(null)

    try {
      const result = await apiClient.post('/ask', {
        question: input.trim(),
        doc_id: docIdForRequest,
        session_id: currentSessionId
      })
      
      setMessages(prev => [...prev, {
        text: result.data.answer || result.data.response,
        isUser: false,
        timestamp: new Date(),
        sources: result.data.sources || []
      }])
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickAction = async (action) => {
    if (!selectedDocumentId || isLoading) return
    
    let currentSessionId = sessionId
    if (!currentSessionId) {
      const sessionRes = await apiClient.post('/sessions', { title: action === 'summary' ? "Summary" : "Insights" })
      currentSessionId = sessionRes.data.id
      setSessionId(currentSessionId)
    }

    setIsLoading(true)
    setError(null)

    const intentText = action === 'summary' ? 'Generate a summary for this document' : 'Extract key insights from this document'
    const userMsg = {
      text: intentText,
      isUser: true,
      timestamp: new Date(),
      attachedDoc: documents.find(d => d.id === selectedDocumentId)
    }
    setMessages(prev => [...prev, userMsg])

    const docIdForRequest = selectedDocumentId
    setSelectedDocumentId(null)

    try {
      let result
      if (action === 'summary') {
        result = await apiClient.post('/summary', {
          doc_id: docIdForRequest,
          summary_type: 'concise',
          session_id: currentSessionId
        })
        setMessages(prev => [...prev, {
          text: result.data.summary,
          isUser: false,
          timestamp: new Date()
        }])
      } else {
        result = await apiClient.post('/insights', {
          doc_id: docIdForRequest,
          session_id: currentSessionId
        })
        const textResult = result.data.raw_insights || JSON.stringify(result.data, null, 2)
        setMessages(prev => [...prev, {
          text: textResult,
          isUser: false,
          timestamp: new Date()
        }])
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await apiClient.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      const newDoc = { id: res.data.doc_id, name: res.data.file_name || file.name }
      setDocuments(prev => [newDoc, ...prev])
      setSelectedDocumentId(newDoc.id)
      showNotification('Document uploaded successfully!', 'success')
    } catch (err) {
      setError(`Upload failed: ${err.message}`)
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const selectedDoc = documents.find(d => d.id === selectedDocumentId)

  return (
    <div className="flex h-screen bg-zinc-950 overflow-hidden text-zinc-100 font-sans">
      {/* Hidden File Input for uploads */}
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileUpload} 
        className="hidden" 
        accept=".pdf,.docx,.txt" 
      />
      
      <Sidebar 
        onSelectSession={loadSession} 
        currentSessionId={sessionId} 
        onNewChat={handleNewChat} 
      />
      
      <div className="flex-1 flex flex-col relative overflow-hidden">
        {/* Top Header info */}
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 flex justify-between items-center bg-zinc-950/40 backdrop-blur-xl z-20 border-b border-zinc-900/50"
        >
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-zinc-500">Document Intelligence</span>
            <span className="text-zinc-700">/</span>
            <span className="text-sm font-semibold text-zinc-200 truncate max-w-[200px]">
              {sessionId ? messages.find(m => m.isUser)?.text?.substring(0, 30) || "Conversation" : "New Chat"}
            </span>
          </div>
          <div className="flex items-center gap-2">
             <button className="p-2 text-zinc-500 hover:text-zinc-100 hover:bg-zinc-900 rounded-lg transition-all"><History className="w-4 h-4" /></button>
          </div>
        </motion.div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col items-center w-full max-w-4xl mx-auto px-4 overflow-hidden relative">
          
          <AnimatePresence mode="wait">
            {messages.length === 0 ? (
              <motion.div 
                key="welcome"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="flex-1 flex flex-col items-center justify-center w-full pb-12"
              >
                <motion.h1 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="text-5xl font-bold text-zinc-100 mb-12 text-center tracking-tight"
                >
                  What are you <span className="text-zinc-500">working on?</span>
                </motion.h1>
                
                <div className="w-full relative mb-8 flex flex-col items-center max-w-2xl">
                  <motion.div 
                    layoutId="input-bar"
                    className="w-full bg-zinc-900/50 backdrop-blur-md rounded-[2.5rem] p-3.5 flex flex-col gap-3 border border-zinc-800 focus-within:border-zinc-700 transition-all shadow-2xl"
                  >
                    <AnimatePresence>
                      {selectedDoc && (
                        <motion.div 
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: -10 }}
                          className="flex items-center gap-3 bg-zinc-800 border border-zinc-700/50 rounded-2xl pl-2 pr-4 py-2.5 max-w-xs relative group w-fit ml-2 mt-1 shadow-lg"
                        >
                          <div className="w-10 h-10 rounded-xl bg-rose-500 flex items-center justify-center flex-shrink-0">
                            <FileText className="w-5 h-5 text-white" />
                          </div>
                          <div className="flex flex-col flex-1 overflow-hidden min-w-0">
                            <span className="text-xs font-bold text-zinc-100 truncate w-full block">{selectedDoc.name}</span>
                            <span className="text-[10px] text-rose-300 font-bold uppercase tracking-wider mt-0.5">PDF DOCUMENT</span>
                          </div>
                          <button 
                            onClick={() => setSelectedDocumentId(null)} 
                            className="absolute -top-2 -right-2 bg-zinc-700 text-zinc-300 rounded-full p-1 border border-zinc-600 hover:bg-zinc-600 transition-colors shadow-sm"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </motion.div>
                      )}
                    </AnimatePresence>
                    <div className="flex items-center gap-3 w-full px-2">
                      <motion.button 
                        whileHover={{ scale: 1.1, backgroundColor: '#27272a' }}
                        whileTap={{ scale: 0.9 }}
                        onClick={() => fileInputRef.current?.click()} 
                        className="p-1.5 text-zinc-400 hover:text-zinc-200 transition-colors"
                      >
                        <Plus className="w-7 h-7" />
                      </motion.button>
                      <input 
                        type="text" 
                        value={userInput} 
                        onChange={(e) => setUserInput(e.target.value)} 
                        onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()} 
                        placeholder="Ask anything..." 
                        className="flex-1 bg-transparent border-none text-zinc-100 placeholder-zinc-500 text-xl py-1.5 px-1 focus:ring-0" 
                      />
                      <motion.button 
                        whileHover={userInput.trim() ? { scale: 1.1 } : {}}
                        whileTap={userInput.trim() ? { scale: 0.9 } : {}}
                        onClick={() => handleSendMessage()} 
                        disabled={!userInput.trim() || isLoading} 
                        className={`p-2 rounded-full flex items-center justify-center transition-all ${userInput.trim() ? 'bg-white text-zinc-950 shadow-lg' : 'bg-zinc-800 text-zinc-600'}`}
                      >
                        <ArrowUp className="w-6 h-6 stroke-[3px]" />
                      </motion.button>
                    </div>
                  </motion.div>
                </div>

                <AnimatePresence>
                  {selectedDocumentId && (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      className="flex flex-wrap justify-center gap-4"
                    >
                      <motion.button 
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleQuickAction('summary')} 
                        className="flex items-center gap-2.5 px-6 py-3 bg-zinc-900 border border-zinc-800 rounded-full text-zinc-300 text-sm font-bold hover:bg-zinc-800 hover:border-zinc-700 transition-all shadow-xl"
                      >
                        <FileText className="w-4.5 h-4.5 text-rose-500" />
                        Generate Summary
                      </motion.button>
                      <motion.button 
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleQuickAction('insights')} 
                        className="flex items-center gap-2.5 px-6 py-3 bg-zinc-900 border border-zinc-800 rounded-full text-zinc-300 text-sm font-bold hover:bg-zinc-800 hover:border-zinc-700 transition-all shadow-xl"
                      >
                        <Lightbulb className="w-4.5 h-4.5 text-amber-500" />
                        Insights Generator
                      </motion.button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ) : (
              <motion.div 
                key="chat"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="w-full flex-1 overflow-y-auto px-2 space-y-12 pt-8 scroll-smooth scrollbar-thin scrollbar-thumb-zinc-800"
              >
                {messages.map((msg, idx) => (
                  <motion.div 
                    key={idx} 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4 }}
                    className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[85%] ${msg.isUser ? 'bg-zinc-900 px-6 py-4 rounded-[2rem] text-zinc-100 shadow-lg border border-zinc-800' : 'text-zinc-200'}`}>
                      {!msg.isUser && (
                        <div className="flex items-center gap-3 mb-4">
                          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-xs font-black text-white shadow-lg">DI</div>
                          <span className="text-[10px] font-black text-zinc-500 uppercase tracking-widest">AI ASSISTANT</span>
                        </div>
                      )}
                      <div className="prose prose-invert max-w-none text-zinc-200 leading-relaxed break-words">
                        {msg.isUser && msg.attachedDoc && (
                          <div className="flex items-center gap-3 bg-zinc-800 border border-zinc-700/50 rounded-2xl pl-2 pr-4 py-2.5 max-w-xs shadow-md mb-4 w-fit">
                            <div className="w-10 h-10 rounded-xl bg-rose-500 flex items-center justify-center flex-shrink-0">
                              <FileText className="w-5 h-5 text-white" />
                            </div>
                            <div className="flex flex-col flex-1 overflow-hidden min-w-0 pr-2">
                              <span className="text-xs font-bold text-zinc-100 truncate w-full block">{msg.attachedDoc.name}</span>
                              <span className="text-[10px] text-zinc-400 font-bold mt-0.5 uppercase">PDF</span>
                            </div>
                          </div>
                        )}
                        <ReactMarkdown>{msg.text}</ReactMarkdown>
                      </div>
                      
                      {!msg.isUser && msg.sources && msg.sources.length > 0 && (
                        <div className="mt-6 flex flex-wrap gap-2 pt-4 border-t border-zinc-900/50">
                          {msg.sources.map((s, i) => (
                            <button key={i} className="px-3 py-1 bg-zinc-900/50 border border-zinc-800 rounded-lg text-[10px] font-bold text-zinc-500 hover:text-zinc-300 transition-colors">
                              SOURCE {s.chunk_index}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
                {isLoading && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex justify-start items-center gap-4 text-zinc-500 px-6"
                  >
                    <div className="w-5 h-5 border-2 border-zinc-700 border-t-zinc-400 rounded-full animate-spin" />
                    <span className="text-xs font-bold tracking-tight italic opacity-70">Document Intelligence is thinking...</span>
                  </motion.div>
                )}
                <div ref={messagesEndRef} className="h-32" />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Floating Input (Chat mode) */}
          <AnimatePresence>
            {messages.length > 0 && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                className="w-full pt-4 mt-auto pb-6 px-4 bg-gradient-to-t from-zinc-950 via-zinc-950 to-transparent"
              >
                <div className="w-full max-w-3xl mx-auto bg-zinc-900/80 backdrop-blur-2xl rounded-[2.5rem] p-3.5 flex flex-col gap-3 border border-zinc-800 focus-within:border-zinc-700 transition-all shadow-2xl">
                  <AnimatePresence>
                    {selectedDoc && (
                      <motion.div 
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -10 }}
                        className="flex items-center gap-3 bg-zinc-800 border border-zinc-700/50 rounded-2xl pl-2 pr-4 py-2.5 max-w-xs relative group w-fit ml-2 mt-1 shadow-lg"
                      >
                        <div className="w-10 h-10 rounded-xl bg-rose-500 flex items-center justify-center flex-shrink-0"><FileText className="w-5 h-5 text-white" /></div>
                        <div className="flex flex-col flex-1 overflow-hidden min-w-0 pr-2">
                          <span className="text-xs font-bold text-zinc-100 truncate w-full block">{selectedDoc.name}</span>
                          <span className="text-[10px] text-rose-300 font-bold uppercase mt-0.5 tracking-wider">ATTACHED PDF</span>
                        </div>
                        <button 
                          onClick={() => setSelectedDocumentId(null)} 
                          className="absolute -top-2 -right-2 bg-zinc-700 text-zinc-300 rounded-full p-1 border border-zinc-600 hover:bg-zinc-600 transition-colors shadow-sm z-10"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
                  <div className="flex items-center gap-3 w-full px-2">
                    <motion.button 
                      whileHover={{ scale: 1.1, backgroundColor: '#27272a' }}
                      whileTap={{ scale: 0.9 }}
                      onClick={() => fileInputRef.current?.click()} 
                      className="p-1.5 text-zinc-400 hover:text-zinc-200 transition-colors"
                    >
                      <Plus className="w-7 h-7" />
                    </motion.button>
                    <input 
                      type="text" 
                      value={userInput} 
                      onChange={(e) => setUserInput(e.target.value)} 
                      onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()} 
                      placeholder="Ask anything..." 
                      className="flex-1 bg-transparent border-none text-zinc-100 placeholder-zinc-500 text-lg py-1.5 px-1 focus:ring-0" 
                    />
                    <motion.button 
                      whileHover={userInput.trim() ? { scale: 1.1 } : {}}
                      whileTap={userInput.trim() ? { scale: 0.9 } : {}}
                      onClick={() => handleSendMessage()} 
                      disabled={!userInput.trim() || isLoading} 
                      className={`p-2 rounded-full flex items-center justify-center transition-all ${userInput.trim() ? 'bg-white text-zinc-950 shadow-lg' : 'bg-zinc-800 text-zinc-600'}`}
                    >
                      <ArrowUp className="w-6 h-6 stroke-[3px]" />
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Notifications/Alerts */}
      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            className="fixed bottom-24 right-8 z-50 shadow-2xl"
          >
            <Alert variant="error" onClose={() => setError(null)}>{error}</Alert>
          </motion.div>
        )}
        {notification && (
          <motion.div 
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-6 right-6 z-50"
          >
            <div className={`px-5 py-3.5 rounded-2xl border flex items-center gap-3 backdrop-blur-2xl shadow-2xl ${notification.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-blue-500/10 text-blue-400 border-blue-500/20'}`}>
              {notification.type === 'success' ? <CheckCircle2 className="w-5 h-5" /> : <Info className="w-5 h-5" />}
              <span className="text-sm font-bold tracking-tight">{notification.message}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
