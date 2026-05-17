import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000 // 30 second timeout
})

// Request interceptor (optional auth token if you add auth later)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor — avoid redirecting to /login (no auth routes in this app)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
    }
    
    // Enhance error messages for connection diagnostics
    if (error.code === 'ECONNABORTED') {
      error.message = `Request timeout (30s). Backend at ${API_BASE_URL} may be slow or unreachable.`
    } else if (error.message === 'Network Error' || !error.response) {
      error.message = `Cannot connect to backend at ${API_BASE_URL}. Make sure the backend server is running.`
    }
    
    return Promise.reject(error)
  }
)

// Export the API URL for diagnostics
export { API_BASE_URL }
export default apiClient
