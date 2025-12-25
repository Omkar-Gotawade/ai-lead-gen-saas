import { createContext, useState, useContext, useEffect } from 'react'
import { authAPI } from '../api'
import api from '../api/axios'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchUserInfo = async () => {
    try {
      const response = await api.get('/auth/me')
      console.log('✓ User info fetched:', response.data)
      return response.data
    } catch (error) {
      console.error('✗ Failed to fetch user info:', error)
      return null
    }
  }

  useEffect(() => {
    console.log('🔄 AuthContext: Initializing...')
    // Check if user is logged in on mount
    const token = localStorage.getItem('token')
    console.log('🔑 Token exists:', !!token)
    
    if (token) {
      // Try to load from localStorage first for faster initial load
      const cachedUser = localStorage.getItem('user')
      console.log('💾 Cached user exists:', !!cachedUser)
      
      if (cachedUser) {
        try {
          const parsedUser = JSON.parse(cachedUser)
          if (parsedUser.id) {
            console.log('✓ Using cached user:', parsedUser.email)
            setUser(parsedUser)
            setLoading(false)
            return
          }
        } catch (e) {
          console.error('Failed to parse cached user:', e)
        }
      }
      
      // If no cached user or invalid, fetch from server
      console.log('📡 Fetching user info from server...')
      fetchUserInfo().then(userInfo => {
        if (userInfo) {
          console.log('✓ User fetched successfully:', userInfo.email)
          setUser(userInfo)
          localStorage.setItem('user', JSON.stringify(userInfo))
        } else {
          // If fetch fails, user needs to login again
          console.log('✗ Failed to fetch user, clearing session')
          localStorage.removeItem('token')
          localStorage.removeItem('user')
        }
        setLoading(false)
      })
    } else {
      console.log('❌ No token found')
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    const response = await authAPI.login(email, password)
    const { access_token } = response.data
    localStorage.setItem('token', access_token)
    
    // Fetch user info after login
    const userInfo = await fetchUserInfo()
    if (userInfo) {
      setUser(userInfo)
      localStorage.setItem('user', JSON.stringify(userInfo))
    }
    
    return response
  }

  const signup = async (email, password) => {
    const response = await authAPI.register(email, password)
    return response
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }

  const value = {
    user,
    login,
    signup,
    logout,
    loading,
    fetchUserInfo,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
