/**
 * @fileoverview Local storage service for Montessori AI Agent application
 * Handles all localStorage operations with validation and error handling
 */

class StorageService {
  constructor() {
    this.isInitialized = false
  }

  /**
   * Initialize storage service
   */
  async initialize() {
    try {
      // Test localStorage availability
      if (typeof Storage === 'undefined') {
        throw new Error('localStorage not available')
      }

      // Test write/read
      const testKey = 'montessori_ai_test'
      localStorage.setItem(testKey, 'test')
      localStorage.removeItem(testKey)

      this.isInitialized = true
      console.log('✅ Storage service initialized')
      return true
    } catch (error) {
      console.error('Storage initialization failed:', error)
      this.isInitialized = false
      return false
    }
  }

  /**
   * Save profile data
   */
  saveProfile(profile) {
    try {
      localStorage.setItem('montessori_ai_profile', JSON.stringify(profile))
      return true
    } catch (error) {
      console.error('Error saving profile:', error)
      return false
    }
  }

  /**
   * Load profile data
   */
  loadProfile() {
    try {
      const saved = localStorage.getItem('montessori_ai_profile')
      return saved ? JSON.parse(saved) : null
    } catch (error) {
      console.error('Error loading profile:', error)
      return null
    }
  }

  /**
   * Save agent state
   */
  saveAgentState(state) {
    try {
      localStorage.setItem('montessori_ai_agent_state', JSON.stringify(state))
      return true
    } catch (error) {
      console.error('Error saving agent state:', error)
      return false
    }
  }

  /**
   * Load agent state
   */
  loadAgentState() {
    try {
      const saved = localStorage.getItem('montessori_ai_agent_state')
      return saved ? JSON.parse(saved) : null
    } catch (error) {
      console.error('Error loading agent state:', error)
      return null
    }
  }

  /**
   * Clear all data
   */
  clearAll() {
    try {
      const keys = [
        'montessori_ai_profile',
        'montessori_ai_agent_state',
        'montessori_ai_favorites'
      ]
      
      keys.forEach(key => localStorage.removeItem(key))
      return true
    } catch (error) {
      console.error('Error clearing data:', error)
      return false
    }
  }
}

// Export singleton instance
export const storageService = new StorageService()
export default StorageService