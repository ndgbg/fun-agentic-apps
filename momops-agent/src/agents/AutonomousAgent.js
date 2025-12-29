// Core Autonomous Agent - Truly Agentic Implementation
// Observe → Reason → Act Loop with Continuous Monitoring
import { llmService } from '../services/LLMService';

export class AutonomousAgent {
  constructor() {
    this.isRunning = false;
    this.monitoringInterval = null;
    this.state = {
      lastObservation: null,
      currentGoals: [],
      activeInterventions: [],
      learningModel: this.loadLearningModel(),
      confidence: 0.5
    };
    
    // Agent personality and decision-making parameters
    this.personality = {
      proactiveness: 0.8, // How likely to take action
      caution: 0.6, // How conservative in recommendations
      adaptability: 0.9, // How quickly to learn from feedback
      persistence: 0.7 // How long to pursue goals
    };
    
    // Specialized sub-agents
    this.subAgents = {
      sleepAgent: new SleepOptimizationAgent(),
      feedingAgent: new FeedingPatternAgent(),
      developmentAgent: new DevelopmentTrackingAgent(),
      healthAgent: new HealthMonitoringAgent(),
      routineAgent: new RoutineOptimizationAgent()
    };
    
    this.startAutonomousMonitoring();
  }

  // Core autonomous loop - runs every 10 minutes to prevent spam
  startAutonomousMonitoring() {
    if (this.isRunning) return;
    
    this.isRunning = true;
    console.log('🤖 Autonomous Agent: Starting continuous monitoring...');
    
    // Initial observation (delayed to let app settle)
    setTimeout(() => this.performObservationCycle(), 5000);
    
    // Set up continuous monitoring - reduced frequency to prevent spam
    this.monitoringInterval = setInterval(() => {
      this.performObservationCycle();
    }, 10 * 60 * 1000); // Every 10 minutes instead of 5
    
    // Also monitor on data changes
    this.setupDataChangeListeners();
  }

  stopAutonomousMonitoring() {
    this.isRunning = false;
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
    console.log('🤖 Autonomous Agent: Monitoring stopped');
  }

  // Main observation-reasoning-action cycle
  async performObservationCycle() {
    try {
      // OBSERVE: Gather current state
      const observation = await this.observe();
      
      // REASON: Analyze and make decisions
      const decisions = await this.reason(observation);
      
      // ACT: Execute autonomous actions
      await this.act(decisions);
      
      // LEARN: Update model based on outcomes
      this.learn(observation, decisions);
      
      this.state.lastObservation = observation;
      
    } catch (error) {
      console.error('🤖 Agent Error:', error);
    }
  }

  // OBSERVE: Comprehensive environmental awareness
  async observe() {
    const data = this.loadBabyData();
    const now = new Date();
    
    const observation = {
      timestamp: now.toISOString(),
      
      // Current context
      timeOfDay: now.getHours(),
      dayOfWeek: now.getDay(),
      
      // Baby state analysis
      babyState: this.analyzeBabyState(data),
      
      // Recent activities (last 24 hours)
      recentActivities: this.getRecentActivities(data.activities, 24),
      
      // Pattern analysis
      patterns: this.analyzePatterns(data.activities),
      
      // Environmental factors
      environment: this.assessEnvironment(),
      
      // Goal progress
      goalProgress: this.assessGoalProgress(),
      
      // Parent/caregiver state
      caregiverState: this.assessCaregiverState(data),
      
      // Urgency indicators
      urgencySignals: this.detectUrgencySignals(data)
    };

    return observation;
  }

  // REASON: Advanced decision-making with LLM and multiple considerations
  async reason(observation) {
    const decisions = {
      immediateActions: [],
      plannedActions: [],
      goalAdjustments: [],
      learningUpdates: [],
      confidence: 0
    };

    // Try LLM-powered analysis first
    try {
      if (llmService.isReady()) {
        console.log('🧠 Using LLM for agent reasoning...');
        const llmDecisions = await llmService.generateAgentAnalysis(observation, this.state.activeInterventions);
        
        // Merge LLM decisions with our structure
        if (llmDecisions.immediateActions) {
          decisions.immediateActions.push(...llmDecisions.immediateActions);
        }
        if (llmDecisions.plannedActions) {
          decisions.plannedActions.push(...llmDecisions.plannedActions);
        }
        
        // Add LLM insights as low-priority notifications
        if (llmDecisions.insights && llmDecisions.insights.length > 0) {
          decisions.plannedActions.push({
            type: 'insight_notification',
            priority: 'low',
            title: '🧠 AI Insights',
            message: llmDecisions.insights.join('. '),
            reasoning: 'AI analysis of recent patterns',
            confidence: 0.7
          });
        }
      }
    } catch (error) {
      console.error('🧠 LLM reasoning failed, using rule-based fallback:', error);
    }

    // Delegate to specialized agents (rule-based backup)
    for (const [name, agent] of Object.entries(this.subAgents)) {
      const agentDecisions = await agent.reason(observation, this.state);
      this.mergeDecisions(decisions, agentDecisions, name);
    }

    // Meta-reasoning: Coordinate between agents
    decisions.coordinatedPlan = this.coordinateAgents(decisions, observation);
    
    // Risk assessment
    decisions.riskAssessment = this.assessRisks(decisions, observation);
    
    // Confidence calculation
    decisions.confidence = this.calculateConfidence(decisions, observation);

    return decisions;
  }

  // ACT: Execute autonomous actions
  async act(decisions) {
    // Execute immediate actions
    for (const action of decisions.immediateActions) {
      await this.executeAction(action);
    }

    // Schedule planned actions
    for (const action of decisions.plannedActions) {
      this.scheduleAction(action);
    }

    // Update goals
    this.updateGoals(decisions.goalAdjustments);

    // Send proactive notifications
    this.sendProactiveNotifications(decisions);
  }

  // LEARN: Continuous learning and adaptation
  learn(observation, decisions) {
    // Update learning model based on outcomes
    this.updateLearningModel(observation, decisions);
    
    // Adjust personality based on feedback
    this.adaptPersonality(observation, decisions);
    
    // Save learning state
    this.saveLearningModel();
  }

  // Execute specific actions
  async executeAction(action) {
    console.log(`🤖 Executing: ${action.type} - ${action.description}`);
    
    switch (action.type) {
      case 'proactive_notification':
        this.showProactiveNotification(action);
        break;
        
      case 'schedule_reminder':
        this.scheduleReminder(action);
        break;
        
      case 'pattern_alert':
        this.showPatternAlert(action);
        break;
        
      case 'goal_suggestion':
        this.suggestGoal(action);
        break;
        
      case 'intervention_recommendation':
        this.recommendIntervention(action);
        break;
        
      case 'data_collection':
        this.requestDataCollection(action);
        break;
        
      default:
        console.log(`🤖 Unknown action type: ${action.type}`);
    }
  }

  // Helper function to format time properly
  formatTimeAgo(minutes) {
    if (!minutes || !isFinite(minutes) || minutes < 0) {
      return 'just now';
    }
    
    const hours = Math.floor(minutes / 60);
    const mins = Math.floor(minutes % 60);
    
    if (hours === 0) {
      return `${mins}m`;
    } else if (mins === 0) {
      return `${hours}h`;
    } else {
      return `${hours}h ${mins}m`;
    }
  }

  // Proactive notification system with deduplication
  showProactiveNotification(action) {
    // Check for recent duplicate notifications
    const notifications = JSON.parse(localStorage.getItem('agentNotifications') || '[]');
    const recentDuplicate = notifications.find(n => 
      n.title === action.title && 
      Date.now() - new Date(n.timestamp).getTime() < 10 * 60 * 1000 && // Within 10 minutes
      !n.dismissed && !n.actedUpon
    );
    
    if (recentDuplicate) {
      console.log(`🤖 Skipping duplicate notification: ${action.title}`);
      return;
    }

    // Create persistent notification that user can't miss
    const notification = {
      id: `agent-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'agent-proactive',
      priority: action.priority || 'medium',
      title: action.title,
      message: action.message,
      actions: action.userActions || [],
      reasoning: action.reasoning,
      confidence: action.confidence,
      timestamp: new Date().toISOString(),
      persistent: true // Can't be easily dismissed
    };

    // Store in localStorage for persistence (keep only last 5)
    const updatedNotifications = [notification, ...notifications.slice(0, 4)];
    localStorage.setItem('agentNotifications', JSON.stringify(updatedNotifications));

    // Trigger UI update
    window.dispatchEvent(new CustomEvent('agentNotification', { detail: notification }));
    
    console.log(`🤖 Proactive Notification: ${action.title}`);
  }

  // Analyze baby's current state
  analyzeBabyState(data) {
    const now = new Date();
    const activities = data.activities || [];
    
    // Find last activities
    const lastFeed = activities.find(a => a.type === 'feed');
    const lastNap = activities.find(a => a.type === 'nap');
    const lastDiaper = activities.find(a => a.type === 'diaper');
    
    // Calculate time since last activities (handle edge cases)
    const timeSinceLastFeed = lastFeed ? Math.max(0, (now - new Date(lastFeed.timestamp)) / (1000 * 60)) : null;
    const timeSinceLastNap = lastNap ? Math.max(0, (now - new Date(lastNap.timestamp)) / (1000 * 60)) : null;
    const timeSinceLastDiaper = lastDiaper ? Math.max(0, (now - new Date(lastDiaper.timestamp)) / (1000 * 60)) : null;
    
    // Determine likely current state
    let likelyState = 'unknown';
    let needsAttention = [];
    
    // Only add alerts if we have valid time data
    if (timeSinceLastFeed !== null && timeSinceLastFeed > 180) { // 3 hours
      needsAttention.push({ type: 'feeding', urgency: 'high', minutes: timeSinceLastFeed });
    } else if (timeSinceLastFeed !== null && timeSinceLastFeed > 150) { // 2.5 hours
      needsAttention.push({ type: 'feeding', urgency: 'medium', minutes: timeSinceLastFeed });
    }
    
    if (timeSinceLastNap !== null && timeSinceLastNap > 120) { // 2 hours
      needsAttention.push({ type: 'sleep', urgency: 'high', minutes: timeSinceLastNap });
    } else if (timeSinceLastNap !== null && timeSinceLastNap > 90) { // 1.5 hours
      needsAttention.push({ type: 'sleep', urgency: 'medium', minutes: timeSinceLastNap });
    }
    
    if (timeSinceLastDiaper !== null && timeSinceLastDiaper > 180) { // 3 hours
      needsAttention.push({ type: 'diaper', urgency: 'medium', minutes: timeSinceLastDiaper });
    }

    return {
      likelyState,
      needsAttention,
      timeSinceLastFeed: timeSinceLastFeed || 0,
      timeSinceLastNap: timeSinceLastNap || 0,
      timeSinceLastDiaper: timeSinceLastDiaper || 0,
      overallUrgency: needsAttention.length > 0 ? Math.max(...needsAttention.map(n => n.urgency === 'high' ? 3 : n.urgency === 'medium' ? 2 : 1)) : 0
    };
  }

  // Pattern analysis with machine learning
  analyzePatterns(activities) {
    if (!activities || activities.length < 10) return { confidence: 0, patterns: [] };
    
    const patterns = {
      feedingPattern: this.analyzeFeedingPattern(activities),
      sleepPattern: this.analyzeSleepPattern(activities),
      dailyRoutine: this.analyzeDailyRoutine(activities),
      weeklyTrends: this.analyzeWeeklyTrends(activities)
    };
    
    return patterns;
  }

  // Load baby data from localStorage
  loadBabyData() {
    const saved = localStorage.getItem('babyActivities');
    return saved ? JSON.parse(saved) : { activities: [], babyName: '', babyBirthDate: '' };
  }

  // Load learning model
  loadLearningModel() {
    const saved = localStorage.getItem('agentLearningModel');
    return saved ? JSON.parse(saved) : {
      feedingPreferences: {},
      sleepPatterns: {},
      responseHistory: [],
      successfulInterventions: [],
      failedInterventions: [],
      parentPreferences: {}
    };
  }

  // Save learning model
  saveLearningModel() {
    localStorage.setItem('agentLearningModel', JSON.stringify(this.state.learningModel));
  }

  // Get recent activities within specified hours
  getRecentActivities(activities, hours) {
    const cutoff = new Date(Date.now() - hours * 60 * 60 * 1000);
    return (activities || []).filter(a => new Date(a.timestamp) > cutoff);
  }

  // Detect urgent situations requiring immediate attention
  detectUrgencySignals(data) {
    const signals = [];
    const babyState = this.analyzeBabyState(data);
    
    // Critical feeding window
    if (babyState.timeSinceLastFeed > 240) { // 4 hours
      signals.push({
        type: 'critical_feeding',
        urgency: 'critical',
        message: 'Baby has not fed in over 4 hours - immediate attention needed'
      });
    }
    
    // Extended wake period
    if (babyState.timeSinceLastNap > 180) { // 3 hours
      signals.push({
        type: 'overtired',
        urgency: 'high',
        message: 'Baby may be overtired - sleep intervention recommended'
      });
    }
    
    return signals;
  }

  // Setup listeners for data changes
  setupDataChangeListeners() {
    // Listen for localStorage changes
    window.addEventListener('storage', (e) => {
      if (e.key === 'babyActivities') {
        console.log('🤖 Data change detected, triggering observation cycle');
        setTimeout(() => this.performObservationCycle(), 1000);
      }
    });
  }

  // Coordinate decisions between specialized agents
  coordinateAgents(decisions, observation) {
    // Resolve conflicts between agents
    // Prioritize based on urgency and confidence
    // Create unified action plan
    
    return {
      primaryFocus: this.determinePrimaryFocus(decisions, observation),
      actionSequence: this.createActionSequence(decisions),
      conflictResolutions: this.resolveConflicts(decisions)
    };
  }

  // Calculate overall confidence in decisions
  calculateConfidence(decisions, observation) {
    // Base confidence on data quality, pattern strength, and historical success
    let confidence = 0.5;
    
    // Adjust based on data quality
    if (observation.recentActivities.length > 10) confidence += 0.2;
    if (observation.patterns.confidence > 0.7) confidence += 0.2;
    
    // Adjust based on urgency
    if (observation.urgencySignals.length > 0) confidence += 0.1;
    
    return Math.min(1.0, confidence);
  }

  // Record user feedback for learning
  recordUserFeedback(feedbackType, data) {
    console.log('🤖 Recording user feedback:', feedbackType, data);
    
    this.state.learningModel.responseHistory.push({
      type: feedbackType,
      timestamp: new Date().toISOString(),
      data: data
    });
    
    // Adjust confidence based on feedback
    if (feedbackType === 'feeding_dismissed') {
      // User said baby wasn't hungry - reduce confidence in feeding predictions
      this.personality.caution += 0.1;
      this.personality.proactiveness -= 0.05;
    }
    
    this.saveLearningModel();
  }

  // Update learning model based on outcomes
  updateLearningModel(observation, decisions) {
    // Track successful predictions
    // Adjust thresholds based on accuracy
    // Learn from user responses
    
    this.state.learningModel.lastUpdate = new Date().toISOString();
  }

  // Adapt personality based on feedback
  adaptPersonality(observation, decisions) {
    // Adjust personality traits based on user responses and outcomes
    const recentFeedback = this.state.learningModel.responseHistory.slice(-10);
    
    // If user frequently dismisses recommendations, become less proactive
    const dismissalRate = recentFeedback.filter(f => f.type.includes('dismissed')).length / recentFeedback.length;
    if (dismissalRate > 0.5) {
      this.personality.proactiveness = Math.max(0.3, this.personality.proactiveness - 0.1);
    }
  }

  // Additional helper methods for the AutonomousAgent class
  mergeDecisions(mainDecisions, agentDecisions, agentName) {
    mainDecisions.immediateActions.push(...agentDecisions.immediateActions);
    mainDecisions.plannedActions.push(...agentDecisions.plannedActions);
  }

  assessEnvironment() {
    const now = new Date();
    const hour = now.getHours();
    
    return {
      timeOfDay: hour < 6 ? 'night' : hour < 12 ? 'morning' : hour < 18 ? 'afternoon' : 'evening',
      isWeekend: now.getDay() === 0 || now.getDay() === 6,
      hour: hour
    };
  }

  assessGoalProgress() {
    return { activeGoals: 0, completedToday: 0 };
  }

  assessCaregiverState(data) {
    return { estimatedStress: 'low', availability: 'high' };
  }

  analyzeFeedingPattern(activities) {
    const feeds = activities.filter(a => a.type === 'feed').slice(0, 20);
    if (feeds.length < 3) return { confidence: 0, pattern: 'insufficient_data' };
    
    const intervals = [];
    for (let i = 1; i < feeds.length; i++) {
      const interval = (new Date(feeds[i-1].timestamp) - new Date(feeds[i].timestamp)) / (1000 * 60);
      intervals.push(interval);
    }
    
    const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
    
    return {
      confidence: 0.8,
      averageInterval: avgInterval,
      consistency: this.calculateConsistency(intervals)
    };
  }

  analyzeSleepPattern(activities) {
    const naps = activities.filter(a => a.type === 'nap' && a.duration).slice(0, 20);
    if (naps.length < 3) return { confidence: 0, pattern: 'insufficient_data' };
    
    const totalSleep = naps.reduce((sum, nap) => sum + nap.duration, 0);
    const avgNapLength = totalSleep / naps.length;
    
    return {
      confidence: 0.7,
      averageNapLength: avgNapLength,
      totalDailySleep: totalSleep,
      napCount: naps.length
    };
  }

  analyzeDailyRoutine(activities) {
    const hourlyActivity = {};
    activities.forEach(activity => {
      const hour = new Date(activity.timestamp).getHours();
      if (!hourlyActivity[hour]) hourlyActivity[hour] = [];
      hourlyActivity[hour].push(activity);
    });
    
    return {
      confidence: 0.6,
      peakHours: Object.keys(hourlyActivity).sort((a, b) => hourlyActivity[b].length - hourlyActivity[a].length).slice(0, 3),
      routineStrength: this.calculateRoutineStrength(hourlyActivity)
    };
  }

  analyzeWeeklyTrends(activities) {
    const dailyActivity = {};
    activities.forEach(activity => {
      const day = new Date(activity.timestamp).getDay();
      if (!dailyActivity[day]) dailyActivity[day] = [];
      dailyActivity[day].push(activity);
    });
    
    return {
      confidence: 0.5,
      busiestDays: Object.keys(dailyActivity).sort((a, b) => dailyActivity[b].length - dailyActivity[a].length).slice(0, 2),
      weekendPattern: this.analyzeWeekendPattern(dailyActivity)
    };
  }

  calculateConsistency(intervals) {
    if (intervals.length < 2) return 0;
    const mean = intervals.reduce((a, b) => a + b, 0) / intervals.length;
    const variance = intervals.reduce((sum, interval) => sum + Math.pow(interval - mean, 2), 0) / intervals.length;
    const stdDev = Math.sqrt(variance);
    return Math.max(0, 1 - (stdDev / mean));
  }

  calculateRoutineStrength(hourlyActivity) {
    const hours = Object.keys(hourlyActivity);
    if (hours.length < 3) return 0;
    
    let routineScore = 0;
    hours.forEach(hour => {
      const activities = hourlyActivity[hour];
      const typeCount = {};
      activities.forEach(a => {
        typeCount[a.type] = (typeCount[a.type] || 0) + 1;
      });
      
      const maxCount = Math.max(...Object.values(typeCount));
      routineScore += maxCount / activities.length;
    });
    
    return routineScore / hours.length;
  }

  analyzeWeekendPattern(dailyActivity) {
    const weekdayCount = [1,2,3,4,5].reduce((sum, day) => sum + (dailyActivity[day]?.length || 0), 0);
    const weekendCount = [0,6].reduce((sum, day) => sum + (dailyActivity[day]?.length || 0), 0);
    
    return {
      weekdayAverage: weekdayCount / 5,
      weekendAverage: weekendCount / 2,
      difference: (weekendCount / 2) - (weekdayCount / 5)
    };
  }

  determinePrimaryFocus(decisions, observation) {
    const urgencyScores = { critical: 4, high: 3, medium: 2, low: 1 };
    
    let maxUrgency = 0;
    let primaryFocus = 'monitoring';
    
    decisions.immediateActions.forEach(action => {
      const urgency = urgencyScores[action.priority] || 1;
      if (urgency > maxUrgency) {
        maxUrgency = urgency;
        primaryFocus = action.type;
      }
    });
    
    return primaryFocus;
  }

  createActionSequence(decisions) {
    const immediate = decisions.immediateActions.sort((a, b) => {
      const priorities = { critical: 4, high: 3, medium: 2, low: 1 };
      return (priorities[b.priority] || 1) - (priorities[a.priority] || 1);
    });
    
    return {
      immediate: immediate,
      planned: decisions.plannedActions,
      sequence: [...immediate, ...decisions.plannedActions]
    };
  }

  resolveConflicts(decisions) {
    return { conflicts: [], resolutions: [] };
  }

  assessRisks(decisions, observation) {
    const risks = [];
    
    const recentNotifications = JSON.parse(localStorage.getItem('agentNotifications') || '[]');
    const recentCount = recentNotifications.filter(n => 
      Date.now() - new Date(n.timestamp).getTime() < 60 * 60 * 1000
    ).length;
    
    if (recentCount > 3) {
      risks.push({
        type: 'notification_fatigue',
        severity: 'medium',
        description: 'High notification frequency may cause user fatigue'
      });
    }
    
    return risks;
  }

  scheduleAction(action) {
    console.log(`🤖 Scheduling action: ${action.type} for ${action.scheduledTime || 'later'}`);
  }

  updateGoals(goalAdjustments) {
    goalAdjustments.forEach(adjustment => {
      console.log(`🤖 Goal adjustment: ${adjustment.type}`);
    });
  }

  sendProactiveNotifications(decisions) {
    decisions.immediateActions
      .filter(action => action.type === 'proactive_notification')
      .forEach(action => this.showProactiveNotification(action));
  }
}

// Specialized Sleep Optimization Agent
class SleepOptimizationAgent {
  async reason(observation, agentState) {
    const decisions = { immediateActions: [], plannedActions: [] };
    
    const sleepNeeds = this.assessSleepNeeds(observation);
    
    if (sleepNeeds.urgency === 'high' && sleepNeeds.awakeTime > 0) {
      const timeFormatted = this.formatTimeAgo(sleepNeeds.awakeTime);
      decisions.immediateActions.push({
        type: 'proactive_notification',
        priority: 'high',
        title: '😴 Sleep Intervention Needed',
        message: `Baby has been awake for ${timeFormatted}. Overtiredness can make it harder to fall asleep.`,
        reasoning: 'Extended wake periods lead to overtiredness and sleep difficulties',
        confidence: 0.9,
        userActions: [
          { label: 'Start Nap Routine', action: 'start_nap' },
          { label: 'Remind Me in 15min', action: 'snooze_15' }
        ]
      });
    }
    
    return decisions;
  }
  
  assessSleepNeeds(observation) {
    const awakeTime = observation.babyState?.timeSinceLastNap || 0;
    let urgency = 'low';
    
    // Only create alerts if we have valid time data
    if (!isFinite(awakeTime) || awakeTime <= 0) {
      return { awakeTime: 0, urgency: 'low' };
    }
    
    if (awakeTime > 180) urgency = 'high';
    else if (awakeTime > 120) urgency = 'medium';
    
    return { awakeTime, urgency };
  }
  
  formatTimeAgo(minutes) {
    if (!minutes || !isFinite(minutes) || minutes < 0) return 'just now';
    const hours = Math.floor(minutes / 60);
    const mins = Math.floor(minutes % 60);
    if (hours === 0) return `${mins}m`;
    if (mins === 0) return `${hours}h`;
    return `${hours}h ${mins}m`;
  }
}

// Specialized Feeding Pattern Agent
class FeedingPatternAgent {
  async reason(observation, agentState) {
    const decisions = { immediateActions: [], plannedActions: [] };
    
    const feedingNeeds = this.assessFeedingNeeds(observation);
    
    if (feedingNeeds.urgency === 'high' && feedingNeeds.timeSinceFeed > 0) {
      const timeFormatted = this.formatTimeAgo(feedingNeeds.timeSinceFeed);
      decisions.immediateActions.push({
        type: 'proactive_notification',
        priority: 'high',
        title: '🍼 Feeding Time Approaching',
        message: `Last feed was ${timeFormatted} ago. Baby typically feeds every ${feedingNeeds.expectedInterval} minutes.`,
        reasoning: 'Proactive feeding prevents crying and maintains routine',
        confidence: 0.8,
        userActions: [
          { label: 'Start Feeding', action: 'start_feed' },
          { label: 'Baby Not Hungry', action: 'dismiss_feed' }
        ]
      });
    }
    
    return decisions;
  }
  
  assessFeedingNeeds(observation) {
    const timeSinceFeed = observation.babyState?.timeSinceLastFeed || 0;
    const expectedInterval = this.calculateExpectedInterval(observation);
    
    // Only create alerts if we have valid time data
    if (!isFinite(timeSinceFeed) || timeSinceFeed <= 0) {
      return { timeSinceFeed: 0, expectedInterval, urgency: 'low' };
    }
    
    let urgency = 'low';
    if (timeSinceFeed > expectedInterval + 30) urgency = 'high';
    else if (timeSinceFeed > expectedInterval) urgency = 'medium';
    
    return { timeSinceFeed, expectedInterval, urgency };
  }
  
  calculateExpectedInterval(observation) {
    // Analyze feeding patterns to predict next feeding time
    return 180; // Default 3 hours, should be learned from data
  }
  
  formatTimeAgo(minutes) {
    if (!minutes || !isFinite(minutes) || minutes < 0) return 'just now';
    const hours = Math.floor(minutes / 60);
    const mins = Math.floor(minutes % 60);
    if (hours === 0) return `${mins}m`;
    if (mins === 0) return `${hours}h`;
    return `${hours}h ${mins}m`;
  }
}

// Specialized Development Tracking Agent
class DevelopmentTrackingAgent {
  async reason(observation, agentState) {
    const decisions = { immediateActions: [], plannedActions: [] };
    
    // Check for missed developmental activities
    const devNeeds = this.assessDevelopmentNeeds(observation);
    
    if (devNeeds.missedActivities.length > 0) {
      decisions.plannedActions.push({
        type: 'goal_suggestion',
        title: 'Developmental Activity Suggestion',
        message: `No ${devNeeds.missedActivities.join(', ')} recorded today. These activities support healthy development.`,
        reasoning: 'Regular developmental activities are crucial for motor and cognitive growth',
        confidence: 0.7
      });
    }
    
    return decisions;
  }
  
  assessDevelopmentNeeds(observation) {
    const todayActivities = observation.recentActivities.filter(a => {
      const today = new Date().toDateString();
      return new Date(a.timestamp).toDateString() === today;
    });
    
    const missedActivities = [];
    
    // Check for tummy time
    if (!todayActivities.some(a => a.type === 'other' && a.activityType === 'tummytime')) {
      missedActivities.push('tummy time');
    }
    
    return { missedActivities };
  }
}

// Specialized Health Monitoring Agent
class HealthMonitoringAgent {
  async reason(observation, agentState) {
    const decisions = { immediateActions: [], plannedActions: [] };
    
    // Monitor for health concerns
    const healthConcerns = this.assessHealthConcerns(observation);
    
    if (healthConcerns.length > 0) {
      decisions.immediateActions.push({
        type: 'pattern_alert',
        priority: 'medium',
        title: '⚠️ Health Pattern Alert',
        message: healthConcerns.join('. '),
        reasoning: 'Early detection of health issues allows for timely intervention',
        confidence: 0.6
      });
    }
    
    return decisions;
  }
  
  assessHealthConcerns(observation) {
    const concerns = [];
    
    // Check diaper frequency
    const diaperCount = observation.recentActivities.filter(a => a.type === 'diaper').length;
    if (diaperCount < 6) {
      concerns.push('Low diaper count may indicate dehydration');
    }
    
    return concerns;
  }
}

// Specialized Routine Optimization Agent
class RoutineOptimizationAgent {
  async reason(observation, agentState) {
    const decisions = { immediateActions: [], plannedActions: [] };
    
    // Analyze routine consistency
    const routineAnalysis = this.analyzeRoutine(observation);
    
    if (routineAnalysis.inconsistencies.length > 0) {
      decisions.plannedActions.push({
        type: 'intervention_recommendation',
        title: 'Routine Optimization',
        message: `Detected routine inconsistencies: ${routineAnalysis.inconsistencies.join(', ')}`,
        reasoning: 'Consistent routines help babies feel secure and sleep better',
        confidence: 0.5
      });
    }
    
    return decisions;
  }
  
  analyzeRoutine(observation) {
    // Analyze patterns for routine consistency
    return { inconsistencies: [] };
  }
}
