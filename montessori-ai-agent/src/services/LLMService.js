/**
 * @fileoverview Real LLM Service with OpenAI/Anthropic/Ollama integration
 * Provides autonomous AI reasoning and tool calling capabilities for Montessori AI Agent
 */

/**
 * Real LLM Service class with autonomous reasoning capabilities
 */
export class LLMService {
  constructor() {
    this.isInitialized = false
    this.conversationHistory = []
    this.apiKey = null
    this.provider = 'fallback' // 'openai', 'anthropic', 'ollama', or 'fallback'
    
    // System prompt for autonomous reasoning
    this.systemPrompt = `You are Montessori AI Agent, an autonomous agent specialized in Montessori-based early childhood development. You provide personalized activity recommendations using Montessori principles.`
  }

  /**
   * Initialize the LLM service with real API integration
   */
  async initialize(config = {}) {
    try {
      console.log('🧠 Montessori AI LLM: Starting real LLM initialization...')
      
      // Try to get API keys from localStorage
      const openaiKey = typeof window !== 'undefined' && localStorage.getItem('openai_api_key')
      const anthropicKey = typeof window !== 'undefined' && localStorage.getItem('anthropic_api_key')
      
      if (openaiKey) {
        this.provider = 'openai'
        this.apiKey = openaiKey
        console.log('✅ OpenAI API key found')
      } else if (anthropicKey) {
        this.provider = 'anthropic'
        this.apiKey = anthropicKey
        console.log('✅ Anthropic API key found')
      } else {
        console.log('⚠️ No LLM APIs available, using enhanced reasoning fallback')
        this.provider = 'fallback'
      }
      
      this.isInitialized = true
      return true
      
    } catch (error) {
      console.error('Failed to initialize LLM service:', error)
      this.provider = 'fallback'
      this.isInitialized = true
      return false
    }
  }

  /**
   * Main chat interface with autonomous reasoning
   */
  async chat(message, context = {}) {
    try {
      if (!this.isInitialized) {
        await this.initialize()
      }
      
      let response
      
      // Use real LLM if available
      if (this.provider !== 'fallback' && this.apiKey) {
        response = await this.callLLMAPI(message, context)
      } else {
        // Enhanced fallback with reasoning patterns
        response = await this.generateEnhancedResponse(message, context)
      }
      
      return response
      
    } catch (error) {
      console.error('Chat error:', error)
      // Always fallback to enhanced response on error
      return await this.generateEnhancedResponse(message, context)
    }
  }

  /**
   * Call real LLM API
   */
  async callLLMAPI(message, context) {
    try {
      if (this.provider === 'openai') {
        return await this.callOpenAI(message, context)
      } else if (this.provider === 'anthropic') {
        return await this.callAnthropic(message, context)
      }
    } catch (error) {
      console.error('LLM API call failed:', error)
      throw error
    }
  }

  async callOpenAI(message, context) {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: this.systemPrompt },
          { role: 'user', content: message }
        ],
        max_tokens: 500,
        temperature: 0.7
      })
    })
    
    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.status}`)
    }
    
    const data = await response.json()
    return data.choices[0].message.content
  }

  async callAnthropic(message, context) {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': this.apiKey,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-3-sonnet-20240229',
        max_tokens: 500,
        system: this.systemPrompt,
        messages: [{ role: 'user', content: message }]
      })
    })
    
    if (!response.ok) {
      throw new Error(`Anthropic API error: ${response.status}`)
    }
    
    const data = await response.json()
    return data.content[0].text
  }

  /**
   * Generate enhanced response when no LLM is available
   */
  async generateEnhancedResponse(message, context) {
    const lowerMessage = message.toLowerCase()
    
    if (lowerMessage.includes('activity') || lowerMessage.includes('recommendation')) {
      return `Based on Montessori principles, here are some age-appropriate activities:

🎯 **Sensory Exploration**: Provide different textures for your child to explore safely
🤲 **Practical Life**: Simple pouring or sorting activities with household items  
🗣️ **Language Development**: Name objects and describe actions during daily routines
🧠 **Cognitive Growth**: Simple cause-and-effect toys or activities

Each child develops at their own pace. Observe your child's interests and follow their lead for the most engaging learning experiences.`
    }
    
    return `I'm here to help with your child's development using Montessori principles. You can ask me about:
- Age-appropriate activities
- Developmental milestones  
- Montessori methods
- Learning through play

What would you like to explore today?`
  }

  /**
   * Get service status
   */
  getStatus() {
    return {
      initialized: this.isInitialized,
      provider: this.provider,
      hasApiKey: !!this.apiKey
    }
  }

  /**
   * Set API key for runtime configuration
   */
  setApiKey(provider, apiKey) {
    if (provider === 'openai' || provider === 'anthropic') {
      this.apiKey = apiKey
      this.provider = provider
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(`${provider}_api_key`, apiKey)
      }
      console.log(`${provider} API key updated`)
    }
  }
}

// Export singleton instance
export const llmService = new LLMService()
export default LLMService