import { useState, useCallback } from 'react'

export const useAsync = (asyncFunction, immediate = true) => {
  const [status, setStatus] = useState('idle')
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  const execute = useCallback(async (...args) => {
    setStatus('pending')
    setData(null)
    setError(null)

    try {
      const response = await asyncFunction(...args)
      setData(response)
      setStatus('success')
      return response
    } catch (error) {
      setError(error.message || 'An error occurred')
      setStatus('error')
      throw error
    }
  }, [asyncFunction])

  if (immediate) {
    execute()
  }

  return { execute, status, data, error }
}

export const useDocumentManager = () => {
  const [documents, setDocuments] = useState([])
  const [selectedDocument, setSelectedDocument] = useState(null)

  const addDocument = useCallback((doc) => {
    setDocuments(prev => [doc, ...prev])
  }, [])

  const removeDocument = useCallback((docId) => {
    setDocuments(prev => prev.filter(doc => doc.id !== docId))
    if (selectedDocument?.id === docId) {
      setSelectedDocument(null)
    }
  }, [selectedDocument])

  const updateDocument = useCallback((docId, updates) => {
    setDocuments(prev =>
      prev.map(doc =>
        doc.id === docId ? { ...doc, ...updates } : doc
      )
    )
    if (selectedDocument?.id === docId) {
      setSelectedDocument(prev => ({ ...prev, ...updates }))
    }
  }, [selectedDocument])

  return {
    documents,
    selectedDocument,
    setSelectedDocument,
    addDocument,
    removeDocument,
    updateDocument
  }
}

export const useNotification = () => {
  const [notification, setNotification] = useState(null)

  const showNotification = useCallback((message, type = 'info', duration = 3000) => {
    setNotification({ message, type, id: Date.now() })
    if (duration) {
      setTimeout(() => setNotification(null), duration)
    }
  }, [])

  return { notification, showNotification }
}
