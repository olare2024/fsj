import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('accessToken'))
  const refreshToken = ref(localStorage.getItem('refreshToken'))
  const sessionToken = ref(null)
  const requiresVerification = ref(false)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const userRole = computed(() => user.value?.role)
  const isVerified = computed(() => user.value?.is_verified)

  // Set tokens in localStorage and store
  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('accessToken', access)
    localStorage.setItem('refreshToken', refresh)
  }

  // Clear tokens from localStorage and store
  function clearTokens() {
    accessToken.value = null
    refreshToken.value = null
    sessionToken.value = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  }

  // Set user data
  function setUser(userData) {
    user.value = userData
  }

  // Login function
  async function login(credentials) {
    try {
      isLoading.value = true
      const response = await api.post('/auth/login/', credentials)
      
      if (response.data.requires_verification) {
        requiresVerification.value = true
        sessionToken.value = response.data.session_token
        return { requiresVerification: true }
      } else {
        setTokens(response.data.access, response.data.refresh)
        setUser(response.data.user)
        requiresVerification.value = false
        return { success: true }
      }
    } catch (error) {
      throw error.response?.data || { error: 'Login failed' }
    } finally {
      isLoading.value = false
    }
  }

  // Verify login with OTP
  async function verifyLogin(verificationData) {
    try {
      isLoading.value = true
      const response = await api.post('/auth/verify-login/', {
        ...verificationData,
        session_token: sessionToken.value
      })
      
      setTokens(response.data.access, response.data.refresh)
      setUser(response.data.user)
      requiresVerification.value = false
      sessionToken.value = null
      
      return { success: true }
    } catch (error) {
      throw error.response?.data || { error: 'Verification failed' }
    } finally {
      isLoading.value = false
    }
  }

  // Register function
  async function register(userData) {
    try {
      isLoading.value = true
      const response = await api.post('/auth/register/', userData)
      return response.data
    } catch (error) {
      throw error.response?.data || { error: 'Registration failed' }
    } finally {
      isLoading.value = false
    }
  }

  // Verify registration
  async function verifyRegistration(verificationData) {
    try {
      const response = await api.post('/auth/verify-registration/', verificationData)
      return response.data
    } catch (error) {
      throw error.response?.data || { error: 'Verification failed' }
    }
  }

  // Forgot password
  async function forgotPassword(email) {
    try {
      const response = await api.post('/auth/forgot-password/', { email })
      return response.data
    } catch (error) {
      throw error.response?.data || { error: 'Password reset failed' }
    }
  }

  // Reset password
  async function resetPassword(resetData) {
    try {
      const response = await api.post('/auth/reset-password/', resetData)
      return response.data
    } catch (error) {
      throw error.response?.data || { error: 'Password reset failed' }
    }
  }

  // Logout function
  async function logout() {
    try {
      await api.post('/auth/logout/')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      clearTokens()
      user.value = null
      requiresVerification.value = false
      sessionToken.value = null
    }
  }

  // Refresh token
  async function refreshTokens() {
    try {
      const response = await api.post('/auth/token/refresh/', {
        refresh: refreshToken.value
      })
      
      setTokens(response.data.access, refreshToken.value)
      return true
    } catch (error) {
      clearTokens()
      user.value = null
      return false
    }
  }

  // Get user profile
  async function getProfile() {
    try {
      const response = await api.get('/auth/profile/')
      setUser(response.data.user)
      return response.data
    } catch (error) {
      throw error
    }
  }

  // Update profile
  async function updateProfile(profileData) {
    try {
      const response = await api.put('/auth/profile/update/', profileData)
      setUser(response.data)
      return response.data
    } catch (error) {
      throw error.response?.data || { error: 'Profile update failed' }
    }
  }

  // Change password
  async function changePassword(passwordData) {
    try {
      const response = await api.post('/auth/change-password/', passwordData)
      return response.data
    } catch (error) {
      throw error.response?.data || { error: 'Password change failed' }
    }
  }

  // Toggle 2FA
  async function toggle2FA() {
    try {
      const response = await api.post('/auth/toggle-2fa/')
      if (user.value) {
        user.value.is_2fa_enabled = response.data.is_2fa_enabled
      }
      return response.data
    } catch (error) {
      throw error.response?.data || { error: '2FA toggle failed' }
    }
  }

  return {
    user,
    accessToken,
    isAuthenticated,
    userRole,
    isVerified,
    requiresVerification,
    isLoading,
    login,
    verifyLogin,
    register,
    verifyRegistration,
    forgotPassword,
    resetPassword,
    logout,
    refreshTokens,
    getProfile,
    updateProfile,
    changePassword,
    toggle2FA,
    clearTokens
  }
})