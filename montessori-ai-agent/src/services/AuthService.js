/**
 * @fileoverview Authentication service for Montessori AI Agent application
 * Handles local user authentication and session management
 */

class AuthService {
  constructor() {
    this.currentProfile = null
    this.isAuthenticated = false
  }

  /**
   * Get current authenticated profile
   */
  getCurrentProfile() {
    if (this.currentProfile) {
      return this.currentProfile
    }

    // Try to load from localStorage
    try {
      const saved = localStorage.getItem('montessori_ai_profile')
      if (saved) {
        this.currentProfile = JSON.parse(saved)
        this.isAuthenticated = true
        return this.currentProfile
      }
    } catch (error) {
      console.error('Error loading profile:', error)
    }

    return null
  }

  /**
   * Login with profile data
   */
  login(profileData) {
    try {
      this.currentProfile = {
        ...profileData,
        id: profileData.id || Date.now().toString(),
        createdAt: profileData.createdAt || new Date().toISOString(),
        lastLogin: new Date().toISOString()
      }

      // Save to localStorage
      localStorage.setItem('montessori_ai_profile', JSON.stringify(this.currentProfile))
      
      this.isAuthenticated = true
      return this.currentProfile
    } catch (error) {
      console.error('Login error:', error)
      throw error
    }
  }

  /**
   * Update current profile
   */
  updateProfile(updates) {
    if (!this.currentProfile) {
      throw new Error('No profile to update')
    }

    try {
      this.currentProfile = {
        ...this.currentProfile,
        ...updates,
        updatedAt: new Date().toISOString()
      }

      // Save to localStorage
      localStorage.setItem('montessori_ai_profile', JSON.stringify(this.currentProfile))
      
      return this.currentProfile
    } catch (error) {
      console.error('Profile update error:', error)
      throw error
    }
  }

  /**
   * Logout current user
   */
  logout() {
    try {
      this.currentProfile = null
      this.isAuthenticated = false
      
      // Clear from localStorage
      localStorage.removeItem('montessori_ai_profile')
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  /**
   * Check if user is authenticated
   */
  isUserAuthenticated() {
    return this.isAuthenticated && this.currentProfile !== null
  }
}

// Export singleton instance
export const authService = new AuthService()
export default AuthService