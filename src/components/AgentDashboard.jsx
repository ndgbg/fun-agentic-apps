import { useState, useEffect } from 'react'

function AgentDashboard({ activities, babyBirthDate, babyName, embedded }) {
  const [goals, setGoals] = useState([])
  const [recommendations, setRecommendations] = useState([])
  const [activeGoal, setActiveGoal] = useState(null)
  const [showGoalModal, setShowGoalModal] = useState(false)

  useEffect(() => {
    // Load goals from localStorage
    const saved = localStorage.getItem('babyGoals')
    if (saved) {
      setGoals(JSON.parse(saved))
    }
    
    // Generate autonomous recommendations
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

    // Analyze patterns and generate proactive recommendations
    
    // 1. Sleep optimization
    const naps = today.filter(a => a.type === 'nap')
    const totalSleep = naps.reduce((sum, n) => sum + (n.duration || 0), 0)
    
    if (totalSleep < 180 && naps.length < 3) {
      recs.push({
        id: 'sleep-1',
        type: 'critical',
        category: 'sleep',
        title: 'Sleep Deficit Detected',
        description: `${babyName || 'Baby'} has only slept ${Math.floor(totalSleep / 60)}h ${totalSleep % 60}m today. Babies need 12-16 hours of sleep.`,
        action: 'Create optimal nap schedule',
        icon: '◐',
        priority: 'high',
        reasoning: 'Insufficient sleep can affect development and mood. Agent recommends immediate intervention.',
        plan: [
          'Put baby down for nap within next 30 minutes',
          'Create dark, quiet environment',
          'Use white noise machine',
          'Watch for sleep cues (yawning, eye rubbing)'
        ]
      })
    }

    // 2. Feeding pattern analysis
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
          description: `Last feed was ${Math.floor(hoursSinceLastFeed)}h ${Math.round((hoursSinceLastFeed % 1) * 60)}m ago.`,
          action: 'Prepare for feeding',
          icon: '●',
          priority: 'medium',
          reasoning: 'Babies typically feed every 2-3 hours. Proactive preparation prevents crying.',
          plan: [
            'Prepare bottle or find comfortable feeding spot',
            'Check diaper before feeding',
            'Have burp cloth ready',
            'Create calm environment'
          ]
        })
      }
    }

    // 3. Developmental activities
    const age = babyBirthDate ? Math.floor((now - new Date(babyBirthDate)) / (1000 * 60 * 60 * 24 * 30)) : 6
    const todayActivities = today.filter(a => a.type === 'other')
    const hasTummyTime = todayActivities.some(a => a.activityType === 'tummytime')
    
    if (!hasTummyTime && age < 6) {
      recs.push({
        id: 'dev-1',
        type: 'info',
        category: 'development',
        title: 'Tummy Time Recommended',
        description: 'No tummy time recorded today. This is crucial for motor development.',
        action: 'Schedule tummy time',
        icon: '▲',
        priority: 'medium',
        reasoning: 'Tummy time strengthens neck, back, and shoulder muscles. Essential for development.',
        plan: [
          'Wait 30 minutes after feeding',
          'Place baby on play mat',
          'Start with 3-5 minutes',
          'Use toys to encourage head lifting',
          'Stay close and encourage'
        ]
      })
    }

    // 4. Diaper change prediction
    const diapers = today.filter(a => a.type === 'diaper')
    if (diapers.length > 0) {
      const lastDiaper = diapers[0]
      const hoursSinceLastDiaper = (now - new Date(lastDiaper.timestamp)) / (1000 * 60 * 60)
      
      if (hoursSinceLastDiaper > 2.5) {
        recs.push({
          id: 'diaper-1',
          type: 'info',
          category: 'hygiene',
          title: 'Diaper Check Recommended',
          description: `Last diaper change was ${Math.floor(hoursSinceLastDiaper)}h ago.`,
          action: 'Check diaper',
          icon: '◆',
          priority: 'low',
          reasoning: 'Regular diaper changes prevent rashes and discomfort.',
          plan: [
            'Check diaper for wetness',
            'Have changing supplies ready',
            'Use this as opportunity for bonding',
            'Apply diaper cream if needed'
          ]
        })
      }
    }

    // 5. Routine optimization
    if (feeds.length > 0 && naps.length > 0) {
      const feedTimes = feeds.map(f => new Date(f.timestamp).getHours())
      const napTimes = naps.map(n => new Date(n.timestamp).getHours())
      
      // Check if feeding before naps
      const feedsBeforeNaps = napTimes.filter(nt => 
        feedTimes.some(ft => Math.abs(ft - nt) < 1)
      ).length
      
      if (feedsBeforeNaps < naps.length * 0.5) {
        recs.push({
          id: 'routine-1',
          type: 'insight',
          category: 'routine',
          title: 'Optimize Feed-Sleep Routine',
          description: 'Agent detected inconsistent feeding before naps.',
          action: 'Establish routine',
          icon: '◎',
          priority: 'low',
          reasoning: 'Feeding before naps helps baby sleep longer and more soundly.',
          plan: [
            'Feed baby 15-30 minutes before nap time',
            'Burp thoroughly after feeding',
            'Create consistent pre-nap routine',
            'Track results over next 3 days'
          ]
        })
      }
    }

    // 6. Goal-based recommendations
    goals.forEach(goal => {
      if (goal.status === 'active') {
        const progress = calculateGoalProgress(goal, activities)
        if (progress < 50) {
          recs.push({
            id: `goal-${goal.id}`,
            type: 'goal',
            category: 'goal',
            title: `Goal Progress: ${goal.title}`,
            description: `Current progress: ${progress}%. Agent suggests adjustments.`,
            action: 'Review goal plan',
            icon: '◉',
            priority: 'medium',
            reasoning: goal.reasoning,
            plan: goal.plan
          })
        }
      }
    })

    setRecommendations(recs.sort((a, b) => {
      const priority = { high: 3, medium: 2, low: 1 }
      return priority[b.priority] - priority[a.priority]
    }))
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

  const dismissRecommendation = (id) => {
    setRecommendations(recs => recs.filter(r => r.id !== id))
  }

  const acceptRecommendation = (rec) => {
    // Convert recommendation to goal
    addGoal({
      title: rec.title,
      type: rec.category,
      target: 100,
      reasoning: rec.reasoning,
      plan: rec.plan
    })
    dismissRecommendation(rec.id)
  }

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
          <h2>AI Agent</h2>
        </div>
      )}

      <div className="agent-content">
        <div className="agent-intro">
          <h3>🤖 Your Autonomous Care Assistant</h3>
          <p>I continuously analyze {babyName || 'your baby'}'s patterns and proactively suggest interventions to optimize care.</p>
        </div>

        {recommendations.length > 0 && (
          <div className="recommendations-section">
            <h4>Proactive Recommendations</h4>
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
        )}

        {recommendations.length === 0 && (
          <div className="no-recommendations">
            <div className="success-icon">✓</div>
            <h4>All Systems Optimal</h4>
            <p>Agent has analyzed all patterns and found no immediate concerns. Great job!</p>
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
