import { createContext, useState, useContext, useEffect } from 'react'
import { authAPI } from '../api'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is logged in on mount
    const token = localStorage.getItem('token')
    if (token) {
      // In a real app, you might want to validate the token here
      setUser({ token })
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const response = await authAPI.login(email, password)
    const { access_token } = response.data
    localStorage.setItem('token', access_token)
    setUser({ token: access_token })
    return response
  }

  const signup = async (email, password) => {
    const response = await authAPI.register(email, password)
    return response
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
  }

  const value = {
    user,
    login,
    signup,
    logout,
    loading,
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
