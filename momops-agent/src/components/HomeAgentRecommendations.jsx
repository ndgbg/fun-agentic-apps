import { useState, useEffect } from 'react'

function HomeAgentRecommendations({ babyName, activities, onViewAll }) {
  const [recommendations, setRecommendations] = useState([])

  const generateRecommendations = (activities, babyName) => {
    if (!activities || activities.length === 0) {
      return []
    }

    const now = new Date()
    const recommendations = []

    // Analyze feeding patterns
    const feeds = activities.filter(a => a.type === 'feed')
    if (feeds.length >= 2) {
      const lastFeed = feeds[0]
      const timeSinceLastFeed = Math.round((now - new Date(lastFeed.timestamp)) / 60000)
      
      if (timeSinceLastFeed > 150) { // 2.5 hours
        recommendations.push({
          id: 'feed-due',
          title: 'Feeding Time',
          message: `${babyName} last fed ${Math.floor(timeSinceLastFeed / 60)}h ${timeSinceLastFeed % 60}m ago. Consider feeding soon.`,
          category: 'feeding',
          priority: 'high',
          confidence: 0.89,
          iconType: 'feed'
        })
      } else {
        const avgInterval = feeds.slice(0, 3).reduce((acc, feed, i, arr) => {
          if (i === arr.length - 1) return acc
          return acc + (new Date(arr[i].timestamp) - new Date(arr[i + 1].timestamp)) / 60000
        }, 0) / Math.max(1, feeds.length - 1)
        
        recommendations.push({
          id: 'feed-pattern',
          title: 'Feeding Pattern',
          message: `${babyName} feeds every ${Math.round(avgInterval / 60)} hours on average. Next feeding in ${Math.round((avgInterval - timeSinceLastFeed) / 60)}h.`,
          category: 'feeding',
          priority: 'medium',
          confidence: 0.82,
          iconType: 'feed'
        })
      }
    }

    // Analyze sleep patterns
    const naps = activities.filter(a => a.type === 'nap')
    if (naps.length >= 1) {
      const lastNap = naps[0]
      const timeSinceLastNap = Math.round((now - new Date(lastNap.timestamp)) / 60000)
      
      if (timeSinceLastNap > 120) { // 2 hours
        recommendations.push({
          id: 'nap-due',
          title: 'Sleep Time',
          message: `${babyName} has been awake for ${Math.floor(timeSinceLastNap / 60)}h ${timeSinceLastNap % 60}m. Watch for sleep cues.`,
          category: 'sleep',
          priority: 'high',
          confidence: 0.91,
          iconType: 'nap'
        })
      } else if (naps.length >= 3) {
        const avgNapDuration = naps.slice(0, 3).reduce((acc, nap) => acc + (nap.duration || 60), 0) / 3
        recommendations.push({
          id: 'sleep-pattern',
          title: 'Sleep Quality',
          message: `${babyName} averages ${Math.round(avgNapDuration)} minute naps. Current awake time: ${Math.floor(timeSinceLastNap / 60)}h ${timeSinceLastNap % 60}m.`,
          category: 'sleep',
          priority: 'medium',
          confidence: 0.85,
          iconType: 'nap'
        })
      }
    }

    // Analyze diaper patterns
    const diapers = activities.filter(a => a.type === 'diaper')
    if (diapers.length >= 1) {
      const lastDiaper = diapers[0]
      const timeSinceLastDiaper = Math.round((now - new Date(lastDiaper.timestamp)) / 60000)
      
      if (timeSinceLastDiaper > 180) { // 3 hours
        recommendations.push({
          id: 'diaper-check',
          title: 'Diaper Check',
          message: `Last diaper change was ${Math.floor(timeSinceLastDiaper / 60)}h ${timeSinceLastDiaper % 60}m ago. Time for a check.`,
          category: 'diaper',
          priority: 'medium',
          confidence: 0.78,
          iconType: 'diaper'
        })
      }
    }

    // Development insights
    if (activities.length >= 10) {
      const totalActivities = activities.length
      const daysOfData = Math.max(1, Math.round((now - new Date(activities[activities.length - 1].timestamp)) / (24 * 60 * 60 * 1000)))
      const activitiesPerDay = Math.round(totalActivities / daysOfData)
      
      recommendations.push({
        id: 'development-insight',
        title: 'Development Tracking',
        message: `Tracking ${activitiesPerDay} activities per day. ${babyName} is developing consistent daily patterns.`,
        category: 'development',
        priority: 'low',
        confidence: 0.76,
        iconType: 'development'
      })
    }

    return recommendations.slice(0, 3) // Top 3 recommendations
  }

  useEffect(() => {
    const recs = generateRecommendations(activities, babyName)
    setRecommendations(recs)
  }, [activities, babyName])

  // Don't render if no recommendations
  if (recommendations.length === 0) {
    return null
  }

  const getIconContent = (iconType) => {
    switch (iconType) {
      case 'feed':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C13.1 2 14 2.9 14 4V8C14 9.1 13.1 10 12 10C10.9 10 10 9.1 10 8V4C10 2.9 10.9 2 12 2Z" fill="white"/>
            <path d="M12 12C13.1 12 14 12.9 14 14V20C14 21.1 13.1 22 12 22C10.9 22 10 21.1 10 20V14C10 12.9 10.9 12 12 12Z" fill="white"/>
          </svg>
        )
      case 'nap':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 3C16.97 3 21 7.03 21 12C21 16.97 16.97 21 12 21C7.03 21 3 16.97 3 12C3 7.03 7.03 3 12 3ZM12 7C9.24 7 7 9.24 7 12C7 14.76 9.24 17 12 17C14.76 17 17 14.76 17 12C17 9.24 14.76 7 12 7Z" fill="white"/>
          </svg>
        )
      case 'diaper':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="white"/>
          </svg>
        )
      case 'development':
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 11H7V9H9V11ZM13 11H11V9H13V11ZM17 11H15V9H17V11ZM19 3H18V1H16V3H8V1H6V3H5C3.89 3 3.01 3.9 3.01 5L3 19C3 20.1 3.89 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3ZM19 19H5V8H19V19Z" fill="white"/>
          </svg>
        )
      default:
        return (
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" fill="white"/>
          </svg>
        )
    }
  }

  return (
    <div className="home-agent-section">
      <div className="home-agent-header">
        <h3>AI Recommendations</h3>
        <button className="view-all-btn" onClick={onViewAll}>
          View All
        </button>
      </div>
      
      <div className="home-recommendations">
        {recommendations.map((rec) => (
          <div key={rec.id} className="home-recommendation-card">
            <div className="rec-icon-home">
              {getIconContent(rec.iconType)}
            </div>
            <div className="rec-content-home">
              <h4>{rec.title}</h4>
              <p>{rec.message}</p>
              <div className="rec-meta">
                <span className={`priority-dot ${rec.priority}`}></span>
                <span className="confidence">{Math.round(rec.confidence * 100)}% confidence</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default HomeAgentRecommendations