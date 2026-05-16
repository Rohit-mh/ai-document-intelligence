import React from 'react'
import { LoadingSpinner } from './Common'

export const ChatMessage = ({ 
  message, 
  isUser = false, 
  isLoading = false,
  sources = []
}) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-slide-up`}>
      <div
        className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
          isUser
            ? 'bg-primary-600 text-white rounded-br-none'
            : 'bg-gray-100 text-gray-900 rounded-bl-none'
        }`}
      >
        {isLoading ? (
          <div className="flex items-center gap-2">
            <LoadingSpinner size="sm" />
            <span className="text-sm">Thinking...</span>
          </div>
        ) : (
          <>
            <p className="text-sm leading-relaxed">{message}</p>
            {sources && sources.length > 0 && (
              <div className="mt-2 pt-2 border-t border-opacity-30" style={{borderColor: 'currentColor'}}>
                <p className="text-xs font-semibold mb-1">Sources:</p>
                <div className="space-y-1">
                  {sources.map((source, idx) => (
                    <p key={idx} className="text-xs opacity-75">
                      • {source}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export const ChatInput = ({ 
  value, 
  onChange, 
  onSubmit, 
  disabled = false,
  placeholder = "Ask a question..."
}) => {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !disabled) {
      e.preventDefault()
      onSubmit()
    }
  }

  return (
    <div className="flex gap-2">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={placeholder}
        disabled={disabled}
        className="flex-1 px-4 py-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-600 disabled:bg-gray-50"
        rows="3"
      />
      <button
        onClick={onSubmit}
        disabled={disabled || !value.trim()}
        className="px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        Send
      </button>
    </div>
  )
}
