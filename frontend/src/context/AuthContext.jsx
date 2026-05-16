import React, { createContext, useContext, useState, useEffect } from 'react'
import apiClient from '../services/apiClient'

const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      checkUser()
    } else {
      setLoading(false)
    }
  }, [])

  const checkUser = async () => {
    try {
      const res = await apiClient.get('/auth/me')
      setUser(res.data)
    } catch (err) {
      localStorage.removeItem('auth_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      const params = new URLSearchParams()
      params.append('username', email)
      params.append('password', password)
      
      const res = await apiClient.post('/auth/token', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      
      const token = res.data.access_token
      localStorage.setItem('auth_token', token)
      await checkUser()
    } catch (err) {
      console.error("Login service error:", err)
      throw err
    }
  }

  const register = async (email, password) => {
    await apiClient.post('/auth/register', { email, password })
    await login(email, password)
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
