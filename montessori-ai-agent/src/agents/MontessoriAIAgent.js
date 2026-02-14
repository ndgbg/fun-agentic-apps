/**
 * @fileoverview Autonomous Montessori AI Agent with real LLM-powered reasoning
 * Implements continuous observe→reason→act loop with adaptive learning
 */

import { llmService } from '../services/LLMService.js'

/**
 * Autonomous Montessori AI Agent with LLM-powered reasoning loop
 */
export class MontessoriAIAgent {
  constructor() {
    this.llmService = llmService
    this.profile = null
    this.isActive = false
    this.isInitialized = false
    this.monitoringInterval = null
    this.learningModel = this._loadLearningModel()
    this.activityHistory = []
    this.pendingActions = []
    this.listeners = []
  }

  /**
   * Initialize the autonomous AI agent
   */
  async initialize() {
    try {
      console.log('🤖 Montessori AI Agent: Initializing autonomous agent...')

      if (this.llmService && this.llmService.initialize) {
        await this.llmService.initialize()
      }

      this.isInitialized = true
      console.log('🤖 Montessori AI Agent: Initialization complete')
    } catch (error) {
      console.error('Error initializing Montessori AI Agent:', error)
      this.isInitialized = true
    }
  }

  /**
   * Register a listener for agent events (recommendations, alerts, etc.)
   */
  onEvent(callback) {
    this.listeners.push(callback)
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback)
    }
  }

  _emit(event) {
    this.listeners.forEach(cb => cb(event))
  }

  /**
   * Set profile and start autonomous monitoring
   */
  async setProfile(profile) {
    try {
      this.profile = profile
      if (profile) {
        await this.startAutonomousMonitoring()
      }
    } catch (error) {
      console.error('Error setting profile:', error)
    }
  }

  /**
   * Start the autonomous observe→reason→act monitoring loop
   */
  async startAutonomousMonitoring() {
    if (this.isActive) return

    this.isActive = true
    console.log('🤖 Montessori AI Agent: Starting autonomous monitoring loop...')

    // Run the first cycle immediately
    await this._runAgentCycle()

    // Then run every 15 minutes
    this.monitoringInterval = setInterval(async () => {
      if (this.isActive) {
        await this._runAgentCycle()
      }
    }, 15 * 60 * 1000)
  }

  /**
   * Stop autonomous monitoring
   */
  async stopAutonomousMonitoring() {
    this.isActive = false
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval)
      this.monitoringInterval = null
    }
    this._saveLearningModel()
    console.log('🤖 Montessori AI Agent: Stopped autonomous monitoring')
  }

  // ─── Core Agent Loop ──────────────────────────────────────────────

  /**
   * Single cycle of the observe→reason→act loop
   */
  async _runAgentCycle() {
    try {
      console.log('🤖 Agent cycle: OBSERVE...')
      const observation = await this._observe()

      console.log('🤖 Agent cycle: REASON...')
      const decisions = await this._reason(observation)

      console.log('🤖 Agent cycle: ACT...')
      await this._act(decisions)

      console.log('🤖 Agent cycle: LEARN...')
      this._learn(observation, decisions)

    } catch (error) {
      console.error('🤖 Agent cycle error:', error)
    }
  }

  /**
   * OBSERVE: Gather current state of the child and environment
   */
  async _observe() {
    const now = new Date()
    const childAgeMonths = this.profile?.age || 12
    const recentSessions = this._getRecentSessions(7) // last 7 days

    return {
      timestamp: now.toISOString(),
      timeOfDay: this._getTimeOfDay(now),
      dayOfWeek: now.getDay(),
      childAge: childAgeMonths,
      childName: this.profile?.name || 'Child',
      recentActivities: recentSessions,
      activityCounts: this._countActivitiesByCategory(recentSessions),
      missedCategories: this._findMissedCategories(recentSessions, childAgeMonths),
      engagementTrends: this._analyzeEngagement(recentSessions),
      developmentalStage: this._getDevelopmentalStage(childAgeMonths),
      learningModel: this.learningModel
    }
  }

  /**
   * REASON: Use LLM to analyze observations and decide actions
   */
  async _reason(observation) {
    const decisions = {
      recommendations: [],
      alerts: [],
      adjustments: []
    }

    try {
      const prompt = `You are a Montessori education expert AI agent autonomously monitoring a child's development.

Child: ${observation.childName}, Age: ${observation.childAge} months
Time: ${observation.timeOfDay} (${new Date().toLocaleTimeString()})
Developmental Stage: ${JSON.stringify(observation.developmentalStage)}

Recent Activity Summary (last 7 days):
${JSON.stringify(observation.activityCounts, null, 2)}

Missed Categories (not practiced recently):
${JSON.stringify(observation.missedCategories)}

Engagement Trends:
${JSON.stringify(observation.engagementTrends)}

Learning Model (child preferences):
${JSON.stringify(observation.learningModel)}

Based on this data, provide your reasoning and decisions as JSON:
{
  "reasoning": "your step-by-step analysis",
  "recommendations": [
    {
      "title": "activity title",
      "description": "what to do and why",
      "category": "practical_life|sensorial|language|math|cultural|movement",
      "priority": "high|medium|low",
      "duration": "10-15 minutes",
      "materials": ["item1", "item2"],
      "montessori_principle": "which principle this applies"
    }
  ],
  "alerts": [
    {
      "type": "developmental_gap|schedule_suggestion|milestone_approaching",
      "message": "what to be aware of",
      "urgency": "high|medium|low"
    }
  ],
  "adjustments": [
    {
      "category": "category to adjust",
      "direction": "increase|decrease|maintain",
      "reason": "why"
    }
  ]
}

Focus on:
1. Activities appropriate for ${observation.timeOfDay}
2. Categories the child hasn't explored recently
3. Building on activities the child enjoyed (high engagement)
4. Age-appropriate developmental milestones
5. Following the child's interests (Montessori principle)`

      const response = await this.llmService.chat(prompt, {
        profile: this.profile,
        task: 'agent_reasoning'
      })

      const parsed = this._parseJSONResponse(response)
      if (parsed) {
        decisions.recommendations = parsed.recommendations || []
        decisions.alerts = parsed.alerts || []
        decisions.adjustments = parsed.adjustments || []
      }
    } catch (error) {
      console.error('🤖 LLM reasoning failed, using rule-based fallback:', error)
      decisions.recommendations = this._generateFallbackRecommendations(observation)
      decisions.alerts = this._generateFallbackAlerts(observation)
    }

    return decisions
  }

  /**
   * ACT: Execute decisions - emit recommendations and alerts
   */
  async _act(decisions) {
    // Emit new recommendations
    for (const rec of decisions.recommendations) {
      this._emit({
        type: 'recommendation',
        data: {
          id: `rec_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
          ...rec,
          generatedAt: new Date().toISOString(),
          source: 'autonomous_agent'
        }
      })
    }

    // Emit alerts
    for (const alert of decisions.alerts) {
      this._emit({
        type: 'alert',
        data: {
          id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
          ...alert,
          generatedAt: new Date().toISOString()
        }
      })
    }

    // Apply adjustments to learning model
    for (const adj of decisions.adjustments) {
      this._applyAdjustment(adj)
    }

    console.log(`🤖 ACT: Emitted ${decisions.recommendations.length} recommendations, ${decisions.alerts.length} alerts, ${decisions.adjustments.length} adjustments`)
  }

  /**
   * LEARN: Update the learning model based on observations
   */
  _learn(observation, decisions) {
    // Track which categories were recommended
    for (const rec of decisions.recommendations) {
      if (!this.learningModel.categoryHistory[rec.category]) {
        this.learningModel.categoryHistory[rec.category] = []
      }
      this.learningModel.categoryHistory[rec.category].push({
        timestamp: new Date().toISOString(),
        title: rec.title,
        priority: rec.priority
      })
    }

    // Update cycle count
    this.learningModel.cycleCount = (this.learningModel.cycleCount || 0) + 1
    this.learningModel.lastCycleAt = new Date().toISOString()

    this._saveLearningModel()
  }

  // ─── Observation Helpers ──────────────────────────────────────────

  _getTimeOfDay(date) {
    const hour = date.getHours()
    if (hour < 6) return 'early_morning'
    if (hour < 9) return 'morning'
    if (hour < 12) return 'late_morning'
    if (hour < 14) return 'early_afternoon'
    if (hour < 17) return 'afternoon'
    if (hour < 20) return 'evening'
    return 'night'
  }

  _getRecentSessions(days) {
    const cutoff = new Date()
    cutoff.setDate(cutoff.getDate() - days)
    return this.activityHistory.filter(a => new Date(a.timestamp) > cutoff)
  }

  _countActivitiesByCategory(sessions) {
    const counts = {}
    sessions.forEach(s => {
      counts[s.category] = (counts[s.category] || 0) + 1
    })
    return counts
  }

  _findMissedCategories(sessions, ageMonths) {
    const allCategories = ['practical_life', 'sensorial', 'language', 'math', 'cultural', 'movement']
    const recentCategories = new Set(sessions.map(s => s.category))
    const missed = allCategories.filter(c => !recentCategories.has(c))

    // Filter by age-appropriateness
    if (ageMonths < 12) {
      return missed.filter(c => ['sensorial', 'movement', 'practical_life', 'language'].includes(c))
    }
    if (ageMonths < 24) {
      return missed.filter(c => c !== 'math') // math comes later
    }
    return missed
  }

  _analyzeEngagement(sessions) {
    if (sessions.length === 0) return { averageEngagement: 0, topCategories: [], trends: 'no_data' }

    const byCategory = {}
    sessions.forEach(s => {
      if (!byCategory[s.category]) byCategory[s.category] = []
      byCategory[s.category].push(s.engagement || 0.5)
    })

    const avgByCategory = {}
    Object.entries(byCategory).forEach(([cat, scores]) => {
      avgByCategory[cat] = scores.reduce((a, b) => a + b, 0) / scores.length
    })

    const topCategories = Object.entries(avgByCategory)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([cat]) => cat)

    return {
      averageEngagement: sessions.reduce((a, s) => a + (s.engagement || 0.5), 0) / sessions.length,
      topCategories,
      trends: sessions.length > 5 ? 'sufficient_data' : 'building_data'
    }
  }

  _getDevelopmentalStage(ageMonths) {
    if (ageMonths < 6) return { stage: 'infant', focus: ['sensorial', 'movement'], skills: ['grasping', 'tracking', 'tummy_time'] }
    if (ageMonths < 12) return { stage: 'older_infant', focus: ['sensorial', 'movement', 'practical_life'], skills: ['crawling', 'standing', 'object_permanence'] }
    if (ageMonths < 18) return { stage: 'young_toddler', focus: ['practical_life', 'language', 'movement'], skills: ['walking', 'first_words', 'self_feeding'] }
    if (ageMonths < 24) return { stage: 'toddler', focus: ['practical_life', 'language', 'sensorial'], skills: ['vocabulary_explosion', 'independence', 'sorting'] }
    if (ageMonths < 36) return { stage: 'older_toddler', focus: ['practical_life', 'language', 'sensorial', 'math'], skills: ['sentences', 'pouring', 'counting'] }
    return { stage: 'preschool', focus: ['practical_life', 'language', 'math', 'cultural', 'sensorial'], skills: ['reading_readiness', 'writing', 'math_concepts'] }
  }

  // ─── Fallback Reasoning (when LLM unavailable) ───────────────────

  _generateFallbackRecommendations(observation) {
    const stage = observation.developmentalStage
    const missed = observation.missedCategories
    const recs = []

    const activityDB = {
      practical_life: [
        { title: 'Pouring Practice', description: 'Practice pouring water between small pitchers', duration: '10-15 minutes', materials: ['2 small pitchers', 'tray', 'sponge'] },
        { title: 'Spooning Exercise', description: 'Transfer beans between bowls using a spoon', duration: '10 minutes', materials: ['2 bowls', 'spoon', 'dried beans'] },
        { title: 'Folding Cloths', description: 'Practice folding small washcloths', duration: '5-10 minutes', materials: ['small washcloths'] }
      ],
      sensorial: [
        { title: 'Texture Basket', description: 'Explore different textures: smooth, rough, soft, bumpy', duration: '10-15 minutes', materials: ['fabric swatches', 'sandpaper', 'cotton'] },
        { title: 'Sound Cylinders', description: 'Match pairs of containers by the sounds they make', duration: '10 minutes', materials: ['small containers', 'rice', 'beans', 'sand'] },
        { title: 'Color Sorting', description: 'Sort objects by color into matching containers', duration: '10-15 minutes', materials: ['colored objects', 'matching bowls'] }
      ],
      language: [
        { title: 'Object Naming', description: 'Explore real objects and name them together', duration: '10 minutes', materials: ['household objects', 'picture cards'] },
        { title: 'Story Time', description: 'Read a short picture book, pointing to and naming objects', duration: '10-15 minutes', materials: ['age-appropriate picture book'] },
        { title: 'Singing & Rhymes', description: 'Sing songs with hand movements and repetition', duration: '5-10 minutes', materials: [] }
      ],
      movement: [
        { title: 'Obstacle Course', description: 'Simple indoor course with pillows, tunnels, stepping stones', duration: '15-20 minutes', materials: ['pillows', 'blanket tunnel', 'tape lines'] },
        { title: 'Ball Rolling', description: 'Roll a ball back and forth, practicing tracking and coordination', duration: '10 minutes', materials: ['soft ball'] },
        { title: 'Walking on the Line', description: 'Follow a taped line on the floor, practicing balance', duration: '10 minutes', materials: ['masking tape'] }
      ],
      math: [
        { title: 'Counting Objects', description: 'Count real objects one by one', duration: '10 minutes', materials: ['small countable objects'] },
        { title: 'Size Ordering', description: 'Arrange objects from smallest to largest', duration: '10 minutes', materials: ['nesting cups', 'stacking rings'] }
      ],
      cultural: [
        { title: 'Nature Walk', description: 'Observe and collect natural items outdoors', duration: '15-20 minutes', materials: ['basket', 'magnifying glass'] },
        { title: 'Water Play', description: 'Explore sinking and floating with different objects', duration: '15 minutes', materials: ['basin', 'various objects'] }
      ]
    }

    // Prioritize missed categories
    const priorityCategories = missed.length > 0 ? missed : stage.focus
    for (const category of priorityCategories.slice(0, 3)) {
      const activities = activityDB[category] || []
      if (activities.length > 0) {
        const activity = activities[Math.floor(Math.random() * activities.length)]
        recs.push({
          ...activity,
          category,
          priority: missed.includes(category) ? 'high' : 'medium',
          montessori_principle: 'Follow the child'
        })
      }
    }

    return recs
  }

  _generateFallbackAlerts(observation) {
    const alerts = []
    if (observation.missedCategories.length >= 3) {
      alerts.push({
        type: 'developmental_gap',
        message: `${observation.missedCategories.length} activity categories haven't been practiced recently: ${observation.missedCategories.join(', ')}`,
        urgency: 'medium'
      })
    }
    return alerts
  }

  // ─── Learning Model Persistence ───────────────────────────────────

  _loadLearningModel() {
    try {
      const saved = localStorage.getItem('montessori_learning_model')
      if (saved) return JSON.parse(saved)
    } catch (e) { /* ignore */ }
    return {
      preferredCategories: [],
      engagementScores: {},
      categoryHistory: {},
      cycleCount: 0,
      lastCycleAt: null
    }
  }

  _saveLearningModel() {
    try {
      localStorage.setItem('montessori_learning_model', JSON.stringify(this.learningModel))
    } catch (e) { /* ignore */ }
  }

  _applyAdjustment(adjustment) {
    if (!this.learningModel.engagementScores[adjustment.category]) {
      this.learningModel.engagementScores[adjustment.category] = 0.5
    }
    if (adjustment.direction === 'increase') {
      this.learningModel.engagementScores[adjustment.category] = Math.min(1, this.learningModel.engagementScores[adjustment.category] + 0.1)
    } else if (adjustment.direction === 'decrease') {
      this.learningModel.engagementScores[adjustment.category] = Math.max(0, this.learningModel.engagementScores[adjustment.category] - 0.1)
    }
    this._saveLearningModel()
  }

  // ─── Response Parsing ─────────────────────────────────────────────

  _parseJSONResponse(text) {
    try {
      // Try direct parse
      return JSON.parse(text)
    } catch {
      // Try extracting JSON from markdown code block
      const match = text.match(/```(?:json)?\s*([\s\S]*?)```/)
      if (match) {
        try { return JSON.parse(match[1]) } catch { /* fall through */ }
      }
      // Try finding JSON object
      const braceMatch = text.match(/\{[\s\S]*\}/)
      if (braceMatch) {
        try { return JSON.parse(braceMatch[0]) } catch { /* fall through */ }
      }
      return null
    }
  }

  // ─── Public API ───────────────────────────────────────────────────

  /**
   * Generate recommendations using the full agent reasoning cycle
   */
  async generateRecommendations(count = 5) {
    if (!this.isInitialized || !this.profile) {
      return []
    }

    // Run a full observe→reason cycle
    const observation = await this._observe()
    const decisions = await this._reason(observation)

    return (decisions.recommendations || []).slice(0, count).map((rec, i) => ({
      id: `ai_rec_${Date.now()}_${i}`,
      ...rec
    }))
  }

  recordInteraction(activityId, interactionType, data = {}) {
    const record = {
      activityId,
      interactionType,
      timestamp: new Date().toISOString(),
      ...data
    }
    this.activityHistory.push(record)
    console.log(`Recording interaction: ${activityId} - ${interactionType}`)

    // Update engagement in learning model
    if (data.category && data.engagement !== undefined) {
      if (!this.learningModel.engagementScores[data.category]) {
        this.learningModel.engagementScores[data.category] = 0.5
      }
      // Exponential moving average
      this.learningModel.engagementScores[data.category] =
        0.7 * this.learningModel.engagementScores[data.category] + 0.3 * data.engagement
      this._saveLearningModel()
    }
  }

  recordSession(sessionData) {
    this.activityHistory.push({
      ...sessionData,
      timestamp: sessionData.timestamp || new Date().toISOString()
    })
    console.log('Recording session:', sessionData)
  }

  getAgentStatus() {
    return {
      isActive: this.isActive,
      isInitialized: this.isInitialized,
      cycleCount: this.learningModel.cycleCount || 0,
      lastCycleAt: this.learningModel.lastCycleAt,
      provider: this.llmService?.getStatus?.()?.provider || 'fallback'
    }
  }
}

// Create and export singleton instance
export const montessoriAIAgent = new MontessoriAIAgent()
export default MontessoriAIAgent
