/**
 * @fileoverview Main App component for Montessori AI Agent application
 * Provides routing, state management, and authentication flow
 */

import React, { useState, useEffect } from 'react'
import styled from 'styled-components'
import { GlobalStyles } from './styles/GlobalStyles.js'
import { authService } from './services/AuthService.js'
import { storageService } from './services/StorageService.js'
import { montessoriAIAgent } from './agents/MontessoriAIAgent.js'
import { llmService } from './services/LLMService.js'
import { recommendationEngine } from './services/RecommendationEngine.js'

// Import components
import LoginPage from './components/LoginPage.jsx'
import HomePage from './components/HomePage.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
`

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  color: white;
`

const LoadingSpinner = styled.div`
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [currentProfile, setCurrentProfile] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    initializeApp()
  }, [])

  const initializeApp = async () => {
    try {
      setIsLoading(true)
      
      // Initialize storage service
      await storageService.initialize()
      
      // Check for existing authentication
      const profile = authService.getCurrentProfile()
      
      if (profile) {
        setCurrentProfile(profile)
        setIsAuthenticated(true)
        
        // Initialize AI agent with profile (this will start autonomous monitoring)
        console.log('🤖 Initializing autonomous agent...')
        await montessoriAIAgent.setProfile(profile)
        
        // Update recommendation engine
        recommendationEngine.updateProfile(profile)
        
        console.log('✅ Montessori AI Agent initialized with autonomous AI agent')
      }
      
    } catch (error) {
      console.error('App initialization error:', error)
      setError('Failed to initialize application')
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogin = async (profile) => {
    try {
      setCurrentProfile(profile)
      setIsAuthenticated(true)
      
      // Initialize AI agent with autonomous monitoring
      await montessoriAIAgent.setProfile(profile)
      recommendationEngine.updateProfile(profile)
    } catch (error) {
      console.error('Login error:', error)
      setError('Failed to complete login')
    }
  }

  const handleLogout = async () => {
    // Stop autonomous monitoring
    await montessoriAIAgent.stopAutonomousMonitoring()
    
    authService.logout()
    setIsAuthenticated(false)
    setCurrentProfile(null)
  }

  const handleProfileUpdate = async (updatedProfile) => {
    try {
      setCurrentProfile(updatedProfile)
      
      // Update AI agent with new profile and start monitoring
      await montessoriAIAgent.setProfile(updatedProfile)
      recommendationEngine.updateProfile(updatedProfile)
    } catch (error) {
      console.error('Profile update error:', error)
      setError('Failed to update profile')
    }
  }

  if (isLoading) {
    return (
      <AppContainer>
        <GlobalStyles />
        <LoadingContainer>
          <LoadingSpinner />
          <p style={{ marginTop: '16px', color: 'rgba(255, 255, 255, 0.8)' }}>
            Loading Montessori AI Agent...
          </p>
        </LoadingContainer>
      </AppContainer>
    )
  }

  if (error) {
    return (
      <AppContainer>
        <GlobalStyles />
        <LoadingContainer>
          <p style={{ color: '#ff6b6b', textAlign: 'center', maxWidth: '400px' }}>
            {error}
          </p>
          <button 
            onClick={() => window.location.reload()} 
            style={{
              marginTop: '16px',
              padding: '8px 16px',
              background: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </LoadingContainer>
      </AppContainer>
    )
  }

  return (
    <ErrorBoundary>
      <AppContainer>
        <GlobalStyles />
        {!isAuthenticated ? (
          <LoginPage onLogin={handleLogin} />
        ) : (
          <HomePage 
            profile={currentProfile}
            onLogout={handleLogout}
            onProfileUpdate={handleProfileUpdate}
          />
        )}
      </AppContainer>
    </ErrorBoundary>
  )
}

export default App