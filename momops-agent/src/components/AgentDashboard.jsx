import { useState, useEffect } from 'react'

function AgentDashboard({ activities, babyBirthDate, babyName, embedded }) {
  const [goals, setGoals] = useState([])
  const [agentNotifications, setAgentNotifications] = useState([])
  const [showGoalModal, setShowGoalModal] = useState(false)

  useEffect(() => {
    // Load goals from localStorage
    const saved = localStorage.getItem('babyGoals')
    if (saved) {
      setGoals(JSON.parse(saved))
    }
    
    // Load agent notifications
    loadAgentNotifications()
  }, [])

  useEffect(() => {
    // Listen for new agent notifications
    const handleAgentNotification = (event) => {
      loadAgentNotifications()
    }

    window.addEventListener('agentNotification', handleAgentNotification)
    
    return () => {
      window.removeEventListener('agentNotification', handleAgentNotification)
    }
  }, [])

  useEffect(() => {
    localStorage.setItem('babyGoals', JSON.stringify(goals))
  }, [goals])

  const loadAgentNotifications = () => {
    const notifications = JSON.parse(localStorage.getItem('agentNotifications') || '[]')
    setAgentNotifications(notifications)
  }

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'feeding': return '🍼'
      case 'sleep': return '💤'
      case 'development': return '📈'
      case 'environment': return '🌡️'
      case 'routine': return '⏰'
      case 'growth': return '📊'
      default: return '🔍'
    }
  }

  const getCategoryColor = (category) => {
    switch (category) {
      case 'feeding': return '#3B82F6'
      case 'sleep': return '#8B5CF6'
      case 'development': return '#10B981'
      case 'environment': return '#F59E0B'
      case 'routine': return '#EF4444'
      case 'growth': return '#06B6D4'
      default: return '#6B7280'
    }
  }

  const formatTimeAgo = (timestamp) => {
    const minutes = Math.floor((Date.now() - new Date(timestamp).getTime()) / 60000)
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    const days = Math.floor(hours / 24)
    return `${days}d ago`
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return '#ff4444'
      case 'high': return '#ff8800'
      case 'medium': return '#ffaa00'
      case 'low': return '#00aa88'
      default: return '#666666'
    }
  }

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'critical': return '🚨'
      case 'high': return '⚠️'
      case 'medium': return '💡'
      case 'low': return 'ℹ️'
      default: return '🤖'
    }
  }

  const calculateGoalProgress = (goal, activities) => {
    // Simple progress calculation based on goal type
    const today = activities.filter(a => {
      const date = new Date(a.timestamp)
      return date.toDateString() === new Date().toDateString()
    })

    if (goal.type === 'sleep') {
      const naps = today.filter(a => a.type === 'nap')
      const totalSleep = naps.reduce((sum, n) => sum + (n.duration || 0), 0)
      return Math.min(100, (totalSleep / goal.target) * 100)
    }

    if (goal.type === 'feeding') {
      const feeds = today.filter(a => a.type === 'feed')
      return Math.min(100, (feeds.length / goal.target) * 100)
    }

    return 50 // Default
  }

  const addGoal = (goalData) => {
    const newGoal = {
      id: Date.now(),
      ...goalData,
      status: 'active',
      createdAt: new Date().toISOString()
    }
    setGoals([...goals, newGoal])
    setShowGoalModal(false)
  }

  const handleNotificationAction = (notification, actionType) => {
    console.log('🤖 Dashboard action:', actionType, notification)
    
    // Mark notification as acted upon
    const updatedNotifications = agentNotifications.map(n => 
      n.id === notification.id 
        ? { ...n, actedUpon: true, userAction: actionType, actionTime: new Date().toISOString() }
        : n
    )
    localStorage.setItem('agentNotifications', JSON.stringify(updatedNotifications))
    setAgentNotifications(updatedNotifications)
    
    // Convert to goal if accepted
    if (actionType === 'accept') {
      addGoal({
        title: notification.title,
        type: 'custom',
        target: 100,
        reasoning: notification.reasoning || 'Agent recommendation',
        plan: ['Follow agent guidance', 'Monitor progress', 'Adjust as needed']
      })
    }
  }

  const dismissNotification = (notification) => {
    const updatedNotifications = agentNotifications.map(n => 
      n.id === notification.id 
        ? { ...n, dismissed: true, dismissTime: new Date().toISOString() }
        : n
    )
    localStorage.setItem('agentNotifications', JSON.stringify(updatedNotifications))
    setAgentNotifications(updatedNotifications)
  }

  // Sample recommendations for demo - professional, no emojis, dynamic baby name
  const sampleRecommendations = [
    {
      id: 'sample-1',
      title: 'Feeding Pattern Optimization',
      message: `Agent detected ${babyName || 'your baby'} feeds optimally every 3h 15m. Current schedule varies by 45 minutes, which may affect sleep quality.`,
      reasoning: 'Consistent feeding intervals improve digestion efficiency and promote better sleep patterns',
      confidence: 0.87,
      priority: 'medium',
      category: 'feeding',
      timestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
      actedUpon: false,
      dismissed: false
    },
    {
      id: 'sample-2', 
      title: 'Natural Sleep Window Identified',
      message: `${babyName || 'Your baby'} consistently shows sleep cues at 2:30 PM daily. Establishing an afternoon nap routine could improve overall sleep quality.`,
      reasoning: 'Predictable sleep windows indicate healthy circadian rhythm development and should be reinforced',
      confidence: 0.92,
      priority: 'high',
      category: 'sleep',
      timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
      actedUpon: true,
      userAction: 'accept'
    },
    {
      id: 'sample-3',
      title: 'Development Milestone Tracking',
      message: `At 4 months, ${babyName || 'your baby'} should demonstrate increased head control. Current tummy time sessions may be insufficient.`,
      reasoning: 'Tummy time strengthens neck and shoulder muscles essential for sitting up and motor development',
      confidence: 0.78,
      priority: 'medium',
      category: 'development',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      actedUpon: false,
      dismissed: true
    },
    {
      id: 'sample-4',
      title: 'Environmental Sleep Correlation',
      message: `${babyName || 'Your baby'} sleeps 20% longer on days with morning outdoor exposure. Today's weather conditions are optimal.`,
      reasoning: 'Natural light exposure regulates circadian rhythms and promotes deeper, more restorative sleep',
      confidence: 0.85,
      priority: 'low',
      category: 'environment',
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      actedUpon: false,
      dismissed: false
    },
    {
      id: 'sample-5',
      title: 'Bedtime Routine Efficiency',
      message: `Current bedtime routine duration is 45 minutes. Optimization to 30 minutes may improve ${babyName || 'your baby'}'s sleep onset latency.`,
      reasoning: 'Extended routines can overstimulate infants, while optimal routines promote faster sleep transitions',
      confidence: 0.73,
      priority: 'low',
      category: 'routine',
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      actedUpon: false,
      dismissed: false
    },
    {
      id: 'sample-6',
      title: 'Temperature Optimization Analysis',
      message: `${babyName || 'Your baby'}'s sleep duration increases 30 minutes when room temperature is maintained at 68-70°F versus 72°F+.`,
      reasoning: 'Cooler temperatures support natural thermoregulation and promote deeper sleep phases',
      confidence: 0.89,
      priority: 'medium',
      category: 'environment',
      timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
      actedUpon: true,
      userAction: 'accept'
    },
    {
      id: 'sample-7',
      title: 'Acoustic Environment Calibration',
      message: `White noise at 50dB increases ${babyName || 'your baby'}'s nap duration by 25%. Current audio levels appear suboptimal.`,
      reasoning: 'Consistent background noise masks environmental disruptions that fragment infant sleep',
      confidence: 0.81,
      priority: 'low',
      category: 'environment',
      timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
      actedUpon: false,
      dismissed: false
    },
    {
      id: 'sample-8',
      title: 'Growth Phase Detection',
      message: `${babyName || 'Your baby'}'s feeding frequency has increased 40% over 3 days, indicating probable growth spurt initiation.`,
      reasoning: 'Growth spurts require increased nutritional intake and typically last 2-7 days',
      confidence: 0.94,
      priority: 'high',
      category: 'growth',
      timestamp: new Date(Date.now() - 18 * 60 * 60 * 1000).toISOString(),
      actedUpon: true,
      userAction: 'accept'
    }
  ]

  // Merge real notifications with samples for demo
  const allNotifications = [...agentNotifications, ...sampleRecommendations]
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .slice(0, 10) // Show last 10

  const content = (
    <>
      {embedded && (
        <div className="modal-header">
          <div className="header-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="3" stroke="#86EFAC" strokeWidth="2.5"/>
              <path d="M12 2V6M12 18V22M22 12H18M6 12H2" stroke="#86EFAC" strokeWidth="2.5" strokeLinecap="round"/>
              <path d="M17.5 6.5L15 9M9 15L6.5 17.5M17.5 17.5L15 15M9 9L6.5 6.5" stroke="#86EFAC" strokeWidth="2.5" strokeLinecap="round"/>
            </svg>
          </div>
          <h2>AI Agent Dashboard</h2>
        </div>
      )}

      <div className="agent-content">
        <div className="agent-intro">
          <h3>Autonomous Care Intelligence</h3>
          <p>Advanced pattern recognition and predictive analytics for optimal infant care.</p>
          <div className="agent-status-indicators">
            <div className="status-indicator">
              <span className="status-dot active"></span>
              <span>Real-time Monitoring</span>
            </div>
            <div className="status-indicator">
              <span className="status-dot learning"></span>
              <span>Pattern Learning</span>
            </div>
            <div className="status-indicator">
              <span className="status-dot adaptive"></span>
              <span>Adaptive Recommendations</span>
            </div>
          </div>
        </div>

        <div className="agent-activity-section">
          <div className="section-header-enhanced">
            <div className="section-title">
              <h4>Agent Intelligence Center</h4>
              <p className="section-subtitle">Autonomous recommendations based on pattern analysis</p>
            </div>
            <div className="activity-stats">
              <div className="stat-item">
                <span className="stat-number">{allNotifications.filter(n => !n.dismissed && !n.actedUpon).length}</span>
                <span className="stat-label">Active</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">{allNotifications.filter(n => n.actedUpon).length}</span>
                <span className="stat-label">Accepted</span>
              </div>
            </div>
          </div>
          {allNotifications.length === 0 ? (
            <div className="no-notifications">
              <div className="success-icon">✓</div>
              <h4>All Systems Optimal</h4>
              <p>Agent is monitoring... No recommendations yet.</p>
            </div>
          ) : (
            <div className="notifications-list">
              {allNotifications.map(notification => (
                <div 
                  key={notification.id} 
                  className={`agent-notification-item ${notification.dismissed ? 'dismissed' : ''} ${notification.actedUpon ? 'acted-upon' : ''}`}
                  style={{ borderLeftColor: getCategoryColor(notification.category) }}
                >
                  <div className="notification-header">
                    <div className="notification-category">
                      <div className="category-icon" style={{ backgroundColor: getCategoryColor(notification.category) }}>
                        {getCategoryIcon(notification.category)}
                      </div>
                      <div className="category-info">
                        <span className="category-name">{notification.category || 'analysis'}</span>
                        <span className="priority-badge priority-{notification.priority}">{notification.priority}</span>
                      </div>
                    </div>
                    <span className="notification-time">
                      {formatTimeAgo(notification.timestamp)}
                    </span>
                  </div>
                  
                  <h5 className="notification-title">{notification.title}</h5>
                  <p className="notification-message">{notification.message}</p>
                  
                  {notification.reasoning && (
                    <div className="notification-reasoning">
                      <div className="reasoning-label">Analysis</div>
                      <div className="reasoning-text">{notification.reasoning}</div>
                    </div>
                  )}
                  
                  {notification.confidence && (
                    <div className="notification-confidence">
                      <div className="confidence-label">Confidence</div>
                      <div className="confidence-bar">
                        <div 
                          className="confidence-fill" 
                          style={{ 
                            width: `${notification.confidence * 100}%`,
                            backgroundColor: getCategoryColor(notification.category)
                          }}
                        />
                      </div>
                      <span className="confidence-text">
                        {Math.round(notification.confidence * 100)}%
                      </span>
                    </div>
                  )}
                  
                  {!notification.actedUpon && !notification.dismissed && (
                    <div className="notification-actions">
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => handleNotificationAction(notification, 'accept')}
                      >
                        Accept Recommendation
                      </button>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => dismissNotification(notification)}
                      >
                        Dismiss
                      </button>
                    </div>
                  )}
                  
                  {notification.actedUpon && (
                    <div className="notification-status accepted">
                      <div className="status-icon">✓</div>
                      <span>Recommendation accepted</span>
                    </div>
                  )}
                  
                  {notification.dismissed && !notification.actedUpon && (
                    <div className="notification-status dismissed">
                      <div className="status-icon">×</div>
                      <span>Dismissed by user</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="goals-section">
          <div className="section-header">
            <h4>Active Goals</h4>
            <button className="btn btn-primary" onClick={() => setShowGoalModal(true)}>
              + New Goal
            </button>
          </div>
          
          {goals.filter(g => g.status === 'active').length === 0 ? (
            <div className="empty-state">
              <p>No active goals. Accept agent recommendations or create custom goals!</p>
            </div>
          ) : (
            <div className="goals-list">
              {goals.filter(g => g.status === 'active').map(goal => (
                <div key={goal.id} className="goal-card">
                  <h5>{goal.title}</h5>
                  <div className="goal-progress">
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${calculateGoalProgress(goal, activities)}%` }}
                      />
                    </div>
                    <span>{Math.round(calculateGoalProgress(goal, activities))}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {showGoalModal && (
        <GoalModal 
          onClose={() => setShowGoalModal(false)}
          onSave={addGoal}
        />
      )}
    </>
  )

  if (embedded) {
    return <div className="embedded-view">{content}</div>
  }

  return content
}

function GoalModal({ onClose, onSave }) {
  const [formData, setFormData] = useState({
    title: '',
    type: 'sleep',
    target: 100,
    reasoning: '',
    plan: ['']
  })

  const goalTemplates = {
    sleep: {
      title: 'Improve Sleep Duration',
      target: 720, // 12 hours in minutes
      reasoning: 'Adequate sleep is crucial for baby development and mood regulation',
      plan: [
        'Establish consistent bedtime routine',
        'Create optimal sleep environment (dark, quiet, cool)',
        'Watch for sleep cues and respond promptly',
        'Track sleep patterns for 7 days'
      ]
    },
    feeding: {
      title: 'Establish Feeding Routine',
      target: 8, // 8 feedings per day
      reasoning: 'Consistent feeding schedule helps with digestion and sleep',
      plan: [
        'Feed every 2-3 hours during day',
        'Track feeding amounts and times',
        'Burp thoroughly after each feeding',
        'Monitor for hunger cues'
      ]
    },
    development: {
      title: 'Daily Developmental Activities',
      target: 3, // 3 activities per day
      reasoning: 'Regular stimulation supports cognitive and motor development',
      plan: [
        'Tummy time 3-4 times daily',
        'Reading time before naps',
        'Sensory play with age-appropriate toys',
        'Outdoor time for fresh air and stimulation'
      ]
    }
  }

  const handleTemplateSelect = (type) => {
    setFormData({
      ...formData,
      ...goalTemplates[type],
      type
    })
  }

  const handleSubmit = () => {
    if (!formData.title) {
      alert('Please enter a goal title')
      return
    }
    onSave(formData)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Goal</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">
          <div className="form-group">
            <label>Goal Template</label>
            <div className="button-group">
              <button 
                className={`option-btn ${formData.type === 'sleep' ? 'active' : ''}`}
                onClick={() => handleTemplateSelect('sleep')}
              >
                Sleep
              </button>
              <button 
                className={`option-btn ${formData.type === 'feeding' ? 'active' : ''}`}
                onClick={() => handleTemplateSelect('feeding')}
              >
                Feeding
              </button>
              <button 
                className={`option-btn ${formData.type === 'development' ? 'active' : ''}`}
                onClick={() => handleTemplateSelect('development')}
              >
                Development
              </button>
            </div>
          </div>

          <div className="form-group">
            <label>Goal Title</label>
            <input 
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              className="input"
            />
          </div>

          <div className="form-group">
            <label>Reasoning</label>
            <textarea 
              value={formData.reasoning}
              onChange={(e) => setFormData({...formData, reasoning: e.target.value})}
              className="textarea"
              rows="2"
            />
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSubmit}>Create Goal</button>
        </div>
      </div>
    </div>
  )
}

export default AgentDashboard
