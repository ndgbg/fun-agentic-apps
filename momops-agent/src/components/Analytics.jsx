import { useState, useEffect } from 'react'

function Analytics({ activities, babyBirthDate, babyName, onClose, embedded }) {
  if (embedded) {
    return (
      <div className="embedded-view">
        <div className="modal-header">
          <div className="header-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 3V21H21" stroke="#93C5FD" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M7 16L12 11L16 15L21 8" stroke="#93C5FD" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              <circle cx="21" cy="8" r="2" fill="#93C5FD"/>
              <circle cx="16" cy="15" r="2" fill="#93C5FD"/>
              <circle cx="12" cy="11" r="2" fill="#93C5FD"/>
              <circle cx="7" cy="16" r="2" fill="#93C5FD"/>
            </svg>
          </div>
          <h2>Insights</h2>
        </div>
        <AnalyticsContent activities={activities} babyBirthDate={babyBirthDate} babyName={babyName} />
      </div>
    )
  }
  const [timeRange, setTimeRange] = useState('week')
  
  const getFilteredActivities = () => {
    const now = new Date()
    const cutoff = new Date()
    
    if (timeRange === 'day') {
      cutoff.setDate(cutoff.getDate() - 1)
    } else if (timeRange === 'week') {
      cutoff.setDate(cutoff.getDate() - 7)
    } else {
      cutoff.setDate(cutoff.getDate() - 30)
    }
    
    return activities.filter(a => new Date(a.timestamp) >= cutoff)
  }
  
  const filtered = getFilteredActivities()
  
  const stats = {
    feeds: filtered.filter(a => a.type === 'feed').length,
    breastFeeds: filtered.filter(a => a.type === 'feed' && a.feedType === 'breast').length,
    bottleFeeds: filtered.filter(a => a.type === 'feed' && a.feedType === 'bottle').length,
    naps: filtered.filter(a => a.type === 'nap').length,
    diapers: filtered.filter(a => a.type === 'diaper').length,
    medications: filtered.filter(a => a.type === 'medication').length
  }
  
  const naps = filtered.filter(a => a.type === 'nap' && a.duration)
  const avgNapDuration = naps.length > 0 
    ? Math.round(naps.reduce((sum, n) => sum + n.duration, 0) / naps.length)
    : 0
  
  const totalSleepTime = naps.reduce((sum, n) => sum + (n.duration || 0), 0)
  
  const bottles = filtered.filter(a => a.type === 'feed' && a.feedType === 'bottle' && a.amount)
  const avgBottleAmount = bottles.length > 0
    ? (bottles.reduce((sum, b) => sum + parseFloat(b.amount), 0) / bottles.length).toFixed(1)
    : 0
  
  const feedsByHour = Array.from({ length: 24 }, (_, hour) => {
    const count = filtered.filter(a => {
      if (a.type !== 'feed') return false
      const activityHour = new Date(a.timestamp).getHours()
      return activityHour === hour
    }).length
    return { hour, count }
  })
  
  const maxFeeds = Math.max(...feedsByHour.map(f => f.count), 1)
  
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="analytics-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Analytics</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        <AnalyticsContent activities={activities} />
      </div>
    </div>
  )
}

function AnalyticsContent({ activities, babyBirthDate, babyName }) {
  const [timeRange, setTimeRange] = useState('week')
  const [activeTab, setActiveTab] = useState('insights')
  
  const getFilteredActivities = () => {
    const now = new Date()
    const cutoff = new Date()
    
    if (timeRange === 'day') {
      cutoff.setDate(cutoff.getDate() - 1)
    } else if (timeRange === 'week') {
      cutoff.setDate(cutoff.getDate() - 7)
    } else {
      cutoff.setDate(cutoff.getDate() - 30)
    }
    
    return activities.filter(a => new Date(a.timestamp) >= cutoff)
  }
  
  const filtered = getFilteredActivities()
  
  // Get insights
  const getInsights = () => {
    const insights = []
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    
    const todayActivities = activities.filter(a => {
      const date = new Date(a.timestamp)
      return date.toDateString() === today.toDateString()
    })
    
    const yesterdayActivities = activities.filter(a => {
      const date = new Date(a.timestamp)
      return date.toDateString() === yesterday.toDateString()
    })
    
    // Nap insights
    const todayNaps = todayActivities.filter(a => a.type === 'nap' && a.duration)
    const yesterdayNaps = yesterdayActivities.filter(a => a.type === 'nap' && a.duration)
    
    if (todayNaps.length > 0 && yesterdayNaps.length > 0) {
      const todayTotal = todayNaps.reduce((sum, n) => sum + n.duration, 0)
      const yesterdayTotal = yesterdayNaps.reduce((sum, n) => sum + n.duration, 0)
      const diff = todayTotal - yesterdayTotal
      
      if (Math.abs(diff) > 30) {
        insights.push({
          icon: '◐',
          text: `${diff > 0 ? 'More' : 'Less'} sleep today: ${Math.abs(Math.floor(diff / 60))}h ${Math.abs(diff % 60)}m ${diff > 0 ? 'more' : 'less'} than yesterday`,
          type: diff > 0 ? 'positive' : 'neutral'
        })
      }
    }
    
    // Poop correlation
    const poopDiapers = todayActivities.filter(a => a.type === 'diaper' && (a.diaperType === 'poop' || a.diaperType === 'both'))
    if (poopDiapers.length > 3) {
      insights.push({
        icon: '◆',
        text: `High poop count today (${poopDiapers.length}). Monitor for digestive comfort.`,
        type: 'warning'
      })
    }
    
    // Bath to sleep correlation
    const bathActivities = todayActivities.filter(a => a.type === 'other' && a.activityType === 'bath')
    if (bathActivities.length > 0 && todayNaps.length > 0) {
      const bathTimes = bathActivities.map(b => new Date(b.timestamp).getTime())
      const napsAfterBath = todayNaps.filter(n => {
        const napTime = new Date(n.startTime).getTime()
        return bathTimes.some(bt => napTime > bt && napTime - bt < 3600000) // within 1 hour
      })
      
      if (napsAfterBath.length > 0) {
        const avgDuration = Math.round(napsAfterBath.reduce((sum, n) => sum + n.duration, 0) / napsAfterBath.length)
        insights.push({
          icon: '◎',
          text: `Bath time helps! Naps after bath averaged ${Math.floor(avgDuration / 60)}h ${avgDuration % 60}m`,
          type: 'positive'
        })
      }
    }
    
    // Feeding pattern
    const feeds = todayActivities.filter(a => a.type === 'feed')
    if (feeds.length > 0) {
      const intervals = []
      for (let i = 1; i < feeds.length; i++) {
        const diff = (new Date(feeds[i].timestamp) - new Date(feeds[i-1].timestamp)) / 60000
        intervals.push(diff)
      }
      if (intervals.length > 0) {
        const avgInterval = Math.round(intervals.reduce((a, b) => a + b, 0) / intervals.length)
        insights.push({
          icon: '●',
          text: `Feeding every ${Math.floor(avgInterval / 60)}h ${avgInterval % 60}m on average today`,
          type: 'neutral'
        })
      }
    }
    
    return insights
  }
  
  const insights = getInsights()
  
  const stats = {
    feeds: filtered.filter(a => a.type === 'feed').length,
    breastFeeds: filtered.filter(a => a.type === 'feed' && a.feedType === 'breast').length,
    bottleFeeds: filtered.filter(a => a.type === 'feed' && a.feedType === 'bottle').length,
    naps: filtered.filter(a => a.type === 'nap').length,
    diapers: filtered.filter(a => a.type === 'diaper').length,
    medications: filtered.filter(a => a.type === 'medication').length
  }
  
  const naps = filtered.filter(a => a.type === 'nap' && a.duration)
  const avgNapDuration = naps.length > 0 
    ? Math.round(naps.reduce((sum, n) => sum + n.duration, 0) / naps.length)
    : 0
  
  const totalSleepTime = naps.reduce((sum, n) => sum + (n.duration || 0), 0)
  
  const bottles = filtered.filter(a => a.type === 'feed' && a.feedType === 'bottle' && a.amount)
  const avgBottleAmount = bottles.length > 0
    ? (bottles.reduce((sum, b) => sum + parseFloat(b.amount), 0) / bottles.length).toFixed(1)
    : 0
  
  const feedsByHour = Array.from({ length: 24 }, (_, hour) => {
    const count = filtered.filter(a => {
      if (a.type !== 'feed') return false
      const activityHour = new Date(a.timestamp).getHours()
      return activityHour === hour
    }).length
    return { hour, count }
  })
  
  const maxFeeds = Math.max(...feedsByHour.map(f => f.count), 1)

  return (
    <div className="analytics-content">
          <div className="schedule-tabs">
            <button 
              className={`tab-btn ${activeTab === 'insights' ? 'active' : ''}`}
              onClick={() => setActiveTab('insights')}
            >
              Insights
            </button>
            <button 
              className={`tab-btn ${activeTab === 'agent' ? 'active' : ''}`}
              onClick={() => setActiveTab('agent')}
            >
              AI Agent
            </button>
            <button 
              className={`tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
              onClick={() => setActiveTab('analytics')}
            >
              Analytics
            </button>
          </div>

          {activeTab === 'insights' && (
            <>
              {insights.length > 0 && (
                <div className="insights-section">
                  <h4>Today's Insights</h4>
                  <div className="insights-list">
                    {insights.map((insight, idx) => (
                      <div key={idx} className={`insight-card ${insight.type}`}>
                        <span className="insight-icon">{insight.icon}</span>
                        <span className="insight-text">{insight.text}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {insights.length === 0 && (
                <div className="no-recommendations">
                  <div className="success-icon">✓</div>
                  <h4>All Looking Good!</h4>
                  <p>No immediate insights. Everything is on track!</p>
                </div>
              )}
            </>
          )}

          {activeTab === 'agent' && (
            <AgentSection 
              activities={activities}
              babyBirthDate={babyBirthDate}
              babyName={babyName}
            />
          )}

          {activeTab === 'analytics' && (
            <>
              <div className="time-range-selector">
            <button 
              className={`range-btn ${timeRange === 'day' ? 'active' : ''}`}
              onClick={() => setTimeRange('day')}
            >
              24h
            </button>
            <button 
              className={`range-btn ${timeRange === 'week' ? 'active' : ''}`}
              onClick={() => setTimeRange('week')}
            >
              7d
            </button>
            <button 
              className={`range-btn ${timeRange === 'month' ? 'active' : ''}`}
              onClick={() => setTimeRange('month')}
            >
              30d
            </button>
          </div>
          
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-value">{stats.feeds}</div>
              <div className="stat-label">Total Feeds</div>
              <div className="stat-breakdown">
                {stats.breastFeeds} breast • {stats.bottleFeeds} bottle
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-value">{stats.naps}</div>
              <div className="stat-label">Naps</div>
              <div className="stat-breakdown">
                Avg {Math.floor(avgNapDuration / 60)}h {avgNapDuration % 60}m
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-value">{Math.floor(totalSleepTime / 60)}h</div>
              <div className="stat-label">Total Sleep</div>
              <div className="stat-breakdown">
                {totalSleepTime % 60}m additional
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-value">{stats.diapers}</div>
              <div className="stat-label">Diapers</div>
              <div className="stat-breakdown">
                {(stats.diapers / (timeRange === 'day' ? 1 : timeRange === 'week' ? 7 : 30)).toFixed(1)}/day
              </div>
            </div>
            
            {avgBottleAmount > 0 && (
              <div className="stat-card">
                <div className="stat-value">{avgBottleAmount}oz</div>
                <div className="stat-label">Avg Bottle</div>
                <div className="stat-breakdown">
                  {bottles.length} bottles tracked
                </div>
              </div>
            )}
            
            {stats.medications > 0 && (
              <div className="stat-card">
                <div className="stat-value">{stats.medications}</div>
                <div className="stat-label">Medications</div>
              </div>
            )}
          </div>
          
          <div className="chart-section">
            <h4>Feeding Pattern</h4>
            <div className="bar-chart">
              {feedsByHour.map(({ hour, count }) => (
                <div key={hour} className="bar-item">
                  <div 
                    className="bar" 
                    style={{ height: `${(count / maxFeeds) * 100}%` }}
                  >
                    {count > 0 && <span className="bar-value">{count}</span>}
                  </div>
                  <div className="bar-label">
                    {hour === 0 ? '12a' : hour < 12 ? `${hour}a` : hour === 12 ? '12p' : `${hour-12}p`}
                  </div>
                </div>
              ))}
            </div>
          </div>
            </>
          )}
        </div>
  )
}

// Agent Section Component
function AgentSection({ activities, babyBirthDate, babyName }) {
  const [goals, setGoals] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [showGoalModal, setShowGoalModal] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem('babyGoals')
    if (saved) {
      setGoals(JSON.parse(saved))
    }
    generateRecommendations()
  }, [activities, babyBirthDate])

  useEffect(() => {
    localStorage.setItem('babyGoals', JSON.stringify(goals))
  }, [goals])

  const generateRecommendations = () => {
    const recs = []
    const now = new Date()
    const today = activities.filter(a => {
      const date = new Date(a.timestamp)
      return date.toDateString() === now.toDateString()
    })

    // Sleep optimization
    const naps = today.filter(a => a.type === 'nap')
    const totalSleep = naps.reduce((sum, n) => sum + (n.duration || 0), 0)
    
    if (totalSleep < 180 && naps.length < 3) {
      recs.push({
        id: 'sleep-1',
        type: 'critical',
        category: 'sleep',
        title: 'Sleep Deficit Detected',
        description: `${babyName} has only slept ${Math.floor(totalSleep / 60)}h ${totalSleep % 60}m today. Babies need 12-16 hours.`,
        icon: '◐',
        priority: 'high',
        reasoning: 'Insufficient sleep affects development and mood. Immediate intervention recommended.',
        plan: [
          'Put baby down for nap within 30 minutes',
          'Create dark, quiet environment',
          'Use white noise machine',
          'Watch for sleep cues'
        ]
      })
    }

    // Feeding pattern
    const feeds = today.filter(a => a.type === 'feed')
    if (feeds.length > 0) {
      const lastFeed = feeds[0]
      const hoursSinceLastFeed = (now - new Date(lastFeed.timestamp)) / (1000 * 60 * 60)
      
      if (hoursSinceLastFeed > 3.5) {
        recs.push({
          id: 'feed-1',
          type: 'warning',
          category: 'feeding',
          title: 'Feeding Window Approaching',
          description: `Last feed was ${Math.floor(hoursSinceLastFeed)}h ago.`,
          icon: '●',
          priority: 'medium',
          reasoning: 'Babies typically feed every 2-3 hours. Proactive preparation prevents crying.',
          plan: [
            'Prepare bottle or feeding area',
            'Check diaper before feeding',
            'Have burp cloth ready',
            'Create calm environment'
          ]
        })
      }
    }

    // Developmental activities
    const age = babyBirthDate ? Math.floor((now - new Date(babyBirthDate)) / (1000 * 60 * 60 * 24 * 30)) : 6
    const todayActivities = today.filter(a => a.type === 'other')
    const hasTummyTime = todayActivities.some(a => a.activityType === 'tummytime')
    
    if (!hasTummyTime && age < 6) {
      recs.push({
        id: 'dev-1',
        type: 'info',
        category: 'development',
        title: 'Tummy Time Recommended',
        description: 'No tummy time recorded today. Crucial for motor development.',
        icon: '▲',
        priority: 'medium',
        reasoning: 'Tummy time strengthens neck, back, and shoulder muscles.',
        plan: [
          'Wait 30 minutes after feeding',
          'Place baby on play mat',
          'Start with 3-5 minutes',
          'Use toys to encourage'
        ]
      })
    }

    setRecommendations(recs.sort((a, b) => {
      const priority = { high: 3, medium: 2, low: 1 }
      return priority[b.priority] - priority[a.priority]
    }))
  }

  const calculateGoalProgress = (goal, activities) => {
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

    return 50
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

  const dismissRecommendation = (id) => {
    setRecommendations(recs => recs.filter(r => r.id !== id))
  }

  const acceptRecommendation = (rec) => {
    addGoal({
      title: rec.title,
      type: rec.category,
      target: 100,
      reasoning: rec.reasoning,
      plan: rec.plan
    })
    dismissRecommendation(rec.id)
  }

  return (
    <div className="agent-section">
      <div className="agent-intro-small">
        <h4>🤖 AI Agent Recommendations</h4>
        <p>Autonomous analysis of {babyName}'s patterns with proactive suggestions</p>
      </div>

      {recommendations.length > 0 ? (
        <div className="recommendations-section">
          {recommendations.map(rec => (
            <div key={rec.id} className={`recommendation-card ${rec.type}`}>
              <div className="rec-header">
                <span className="rec-icon">{rec.icon}</span>
                <div className="rec-title-section">
                  <h5>{rec.title}</h5>
                  <span className={`priority-badge ${rec.priority}`}>{rec.priority} priority</span>
                </div>
              </div>
              <p className="rec-description">{rec.description}</p>
              <div className="rec-reasoning">
                <strong>Agent Reasoning:</strong> {rec.reasoning}
              </div>
              <div className="rec-plan">
                <strong>Action Plan:</strong>
                <ol>
                  {rec.plan.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
              <div className="rec-actions">
                <button className="btn btn-primary" onClick={() => acceptRecommendation(rec)}>
                  Accept & Create Goal
                </button>
                <button className="btn btn-secondary" onClick={() => dismissRecommendation(rec.id)}>
                  Dismiss
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="no-recommendations">
          <div className="success-icon">✓</div>
          <h4>All Systems Optimal</h4>
          <p>Agent found no immediate concerns. Great job!</p>
        </div>
      )}

      <div className="goals-section">
        <div className="section-header">
          <h4>Active Goals</h4>
          <button className="btn btn-primary" onClick={() => setShowGoalModal(true)}>
            + New Goal
          </button>
        </div>
        
        {goals.filter(g => g.status === 'active').length === 0 ? (
          <div className="empty-state">
            <p>No active goals. Set a goal and let the agent help you achieve it!</p>
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

      {showGoalModal && (
        <GoalModal 
          onClose={() => setShowGoalModal(false)}
          onSave={addGoal}
        />
      )}
    </div>
  )
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
      target: 720,
      reasoning: 'Adequate sleep is crucial for baby development and mood regulation',
      plan: [
        'Establish consistent bedtime routine',
        'Create optimal sleep environment',
        'Watch for sleep cues',
        'Track patterns for 7 days'
      ]
    },
    feeding: {
      title: 'Establish Feeding Routine',
      target: 8,
      reasoning: 'Consistent feeding schedule helps with digestion and sleep',
      plan: [
        'Feed every 2-3 hours during day',
        'Track amounts and times',
        'Burp thoroughly',
        'Monitor hunger cues'
      ]
    },
    development: {
      title: 'Daily Developmental Activities',
      target: 3,
      reasoning: 'Regular stimulation supports cognitive and motor development',
      plan: [
        'Tummy time 3-4 times daily',
        'Reading before naps',
        'Sensory play',
        'Outdoor time'
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

export default Analytics
