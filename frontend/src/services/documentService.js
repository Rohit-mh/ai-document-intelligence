import apiClient from './apiClient'

function formatApiError(error, fallback) {
  const detail = error.response?.data?.detail
  if (Array.isArray(detail)) {
    const msg = detail
      .map((d) => (typeof d === 'string' ? d : d.msg || JSON.stringify(d)))
      .join('; ')
    return msg || fallback
  }
  if (typeof detail === 'string') return detail
  if (detail && typeof detail === 'object' && typeof detail.message === 'string') {
    return detail.message
  }
  return error.message || fallback
}

/**
 * Upload a document to the backend
 */
export const uploadDocument = async (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          onProgress(percentCompleted)
        }
      }
    })
    return response.data
  } catch (error) {
    throw new Error(formatApiError(error, 'Failed to upload document'))
  }
}

/**
 * Get concise summary of a document (uses backend doc_id)
 */
export const getConciseSummary = async (docId) => {
  try {
    const response = await apiClient.post('/summary', {
      doc_id: docId,
      summary_type: 'concise'
    })
    return response.data
  } catch (error) {
    throw new Error(formatApiError(error, 'Failed to generate summary'))
  }
}

/**
 * Get detailed summary of a document
 */
export const getDetailedSummary = async (docId) => {
  try {
    const response = await apiClient.post('/summary', {
      doc_id: docId,
      summary_type: 'detailed'
    })
    return response.data
  } catch (error) {
    throw new Error(formatApiError(error, 'Failed to generate detailed summary'))
  }
}

/**
 * Extract insights from a document
 */
export const getInsights = async (docId) => {
  try {
    const response = await apiClient.post('/insights', {
      doc_id: docId
    })
    return response.data
  } catch (error) {
    throw new Error(formatApiError(error, 'Failed to extract insights'))
  }
}

/**
 * Ask a question about a document (RAG)
 */
export const askQuestion = async (docId, question) => {
  try {
    const response = await apiClient.post('/ask', {
      doc_id: docId,
      question
    })
    return response.data
  } catch (error) {
    throw new Error(formatApiError(error, 'Failed to get answer'))
  }
}

/**
 * Get system health and status
 */
export const getHealth = async () => {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error) {
    throw new Error('Failed to fetch health status')
  }
}

/**
 * Get system statistics
 */
export const getStats = async () => {
  try {
    const response = await apiClient.get('/stats')
    return response.data
  } catch (error) {
    throw new Error('Failed to fetch statistics')
  }
}

/**
 * Validate configuration
 */
export const validateConfig = async () => {
  try {
    const response = await apiClient.post('/config/validate')
    return response.data
  } catch (error) {
    throw new Error(formatApiError(error, 'Configuration validation failed'))
  }
}
