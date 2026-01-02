/**
 * @fileoverview Home page component for Montessori AI Agent application
 * Displays personalized greetings, recommendations, and activity discovery
 */

import React, { useState, useEffect } from 'react'
import styled from 'styled-components'
import { recommendationEngine } from '../services/RecommendationEngine.js'
import { montessoriAIAgent } from '../agents/MontessoriAIAgent.js'

const HomeContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
`

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  color: white;
`

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
`

const LogoutButton = styled.button`
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: rgba(255, 255, 255, 0.3);
  }
`

const WelcomeCard = styled.div`
  background: white;
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
`

const WelcomeTitle = styled.h2`
  color: #667eea;
  margin-bottom: 1rem;
`

const RecommendationsSection = styled.div`
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
`

const SectionTitle = styled.h3`
  color: #333;
  margin-bottom: 1.5rem;
`

const ActivityGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
`

const ActivityCard = styled.div`
  background: #f8f9fa;
  border-radius: 12px;
  padding: 1.5rem;
  border: 2px solid transparent;
  transition: all 0.2s;
  cursor: pointer;

  &:hover {
    border-color: #667eea;
    transform: translateY(-2px);
  }
`

const ActivityTitle = styled.h4`
  color: #333;
  margin-bottom: 0.5rem;
`

const ActivityDescription = styled.p`
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1rem;
`

const ActivityMeta = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: #888;
`

const LoadingMessage = styled.p`
  text-align: center;
  color: #666;
  font-style: italic;
`

function HomePage({ profile, onLogout }) {
  const [recommendations, setRecommendations] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [agentStatus, setAgentStatus] = useState(null)

  useEffect(() => {
    loadRecommendations()
    loadAgentStatus()
  }, [])

  const loadRecommendations = async () => {
    try {
      setIsLoading(true)
      const recs = await recommendationEngine.generateRecommendations(6)
      setRecommendations(recs)
    } catch (error) {
      console.error('Error loading recommendations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadAgentStatus = () => {
    try {
      const status = montessoriAIAgent.getAgentStatus()
      setAgentStatus(status)
    } catch (error) {
      console.error('Error loading agent status:', error)
    }
  }

  const calculateAge = (birthDate) => {
    const birth = new Date(birthDate)
    const now = new Date()
    const ageInMonths = (now.getFullYear() - birth.getFullYear()) * 12 + (now.getMonth() - birth.getMonth())
    
    if (ageInMonths < 12) {
      return `${ageInMonths} months`
    } else {
      const years = Math.floor(ageInMonths / 12)
      const months = ageInMonths % 12
      return months > 0 ? `${years} years ${months} months` : `${years} years`
    }
  }

  const handleActivityClick = (activity) => {
    // Record interaction with AI agent for learning
    if (montessoriAIAgent && montessoriAIAgent.recordInteraction) {
      montessoriAIAgent.recordInteraction(activity.id, 'started', {
        category: activity.category,
        difficulty: activity.difficulty || 'medium',
        timestamp: new Date().toISOString()
      })
    }
    
    // In a full implementation, this would open an activity detail view
    console.log('Activity clicked:', activity)
  }

  return (
    <HomeContainer>
      <Header>
        <Title>Welcome back!</Title>
        <LogoutButton onClick={onLogout}>
          Logout
        </LogoutButton>
      </Header>

      <WelcomeCard>
        <WelcomeTitle>Hello, {profile.name}! 👋</WelcomeTitle>
        <p>
          Age: {calculateAge(profile.birthDate)} • 
          AI Status: {agentStatus?.isActive ? '🤖 Active' : '😴 Inactive'} •
          Provider: {agentStatus?.provider || 'fallback'}
        </p>
        <p>
          Your AI agent is continuously learning about {profile.name}'s preferences 
          to provide personalized Montessori activities.
        </p>
      </WelcomeCard>

      <RecommendationsSection>
        <SectionTitle>🎯 Personalized Recommendations</SectionTitle>
        
        {isLoading ? (
          <LoadingMessage>Generating personalized activities...</LoadingMessage>
        ) : (
          <ActivityGrid>
            {recommendations.map((activity) => (
              <ActivityCard 
                key={activity.id} 
                onClick={() => handleActivityClick(activity)}
              >
                <ActivityTitle>{activity.title}</ActivityTitle>
                <ActivityDescription>{activity.description}</ActivityDescription>
                <ActivityMeta>
                  <span>📂 {activity.category}</span>
                  <span>⏱️ {activity.duration}</span>
                </ActivityMeta>
              </ActivityCard>
            ))}
          </ActivityGrid>
        )}
      </RecommendationsSection>
    </HomeContainer>
  )
}

export default HomePage