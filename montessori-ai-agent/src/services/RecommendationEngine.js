/**
 * @fileoverview Recommendation Engine for Montessori AI Agent application
 * Provides intelligent activity recommendations based on AI agent learning and user preferences
 */

import { montessoriAIAgent } from '../agents/MontessoriAIAgent.js'

class RecommendationEngine {
  constructor() {
    this.currentProfile = null
  }

  /**
   * Update current profile
   */
  updateProfile(profile) {
    this.currentProfile = profile
  }

  /**
   * Generate recommendations using AI agent
   */
  async generateRecommendations(count = 5) {
    try {
      // Use the autonomous agent's LLM-powered recommendation system
      if (montessoriAIAgent && montessoriAIAgent.generateRecommendations) {
        const llmRecommendations = await montessoriAIAgent.generateRecommendations(count)
        
        if (llmRecommendations && llmRecommendations.length > 0) {
          return llmRecommendations
        }
      }
      
      // Fallback recommendations
      return this.getFallbackRecommendations(count)
      
    } catch (error) {
      console.error('Error generating recommendations:', error)
      return this.getFallbackRecommendations(count)
    }
  }

  /**
   * Get fallback recommendations
   */
  getFallbackRecommendations(count) {
    const fallbackActivities = [
      {
        id: 'fallback_1',
        title: 'Sensory Exploration',
        description: 'Explore different textures with safe household items',
        category: 'sensory',
        duration: '10-15 minutes'
      },
      {
        id: 'fallback_2', 
        title: 'Simple Sorting',
        description: 'Sort objects by color, size, or shape',
        category: 'cognitive',
        duration: '15-20 minutes'
      },
      {
        id: 'fallback_3',
        title: 'Water Play',
        description: 'Supervised water pouring and exploration',
        category: 'practical',
        duration: '20-25 minutes'
      }
    ]

    return fallbackActivities.slice(0, count)
  }
}

// Export singleton instance
export const recommendationEngine = new RecommendationEngine()
export default RecommendationEngine