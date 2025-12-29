import { useState, useEffect } from 'react'

function AgentNotifications({ onAction }) {
  const [notifications, setNotifications] = useState([])
  const [showNotification, setShowNotification] = useState(false)
  const [currentNotification, setCurrentNotification] = useState(null)

  useEffect(() => {
    // Load existing notifications
    loadNotifications()

    // Listen for new agent notifications
    const handleAgentNotification = (event) => {
      const notification = event.detail
      console.log('🔔 New agent notification:', notification)
      
      // Add to notifications list
      setNotifications(prev => [notification, ...prev.slice(0, 9)])
      
      // Show as popup if high priority
      if (notification.priority === 'high' || notification.priority === 'critical') {
        setCurrentNotification(notification)
        setShowNotification(true)
      }
    }

    window.addEventListener('agentNotification', handleAgentNotification)
    
    return () => {
      window.removeEventListener('agentNotification', handleAgentNotification)
    }
  }, [])

  const loadNotifications = () => {
    const saved = localStorage.getItem('agentNotifications')
    if (saved) {
      const parsed = JSON.parse(saved)
      setNotifications(parsed)
      
      // Check if there's a high priority notification to show
      const highPriority = parsed.find(n => 
        (n.priority === 'high' || n.priority === 'critical') && 
        !n.dismissed &&
        Date.now() - new Date(n.timestamp).getTime() < 30 * 60 * 1000 // Within 30 minutes
      )
      
      if (highPriority) {
        setCurrentNotification(highPriority)
        setShowNotification(true)
      }
    }
  }

  const handleNotificationAction = (notification, actionType, actionData) => {
    console.log('🤖 User action:', actionType, actionData)
    
    // Mark notification as acted upon
    const updatedNotifications = notifications.map(n => 
      n.id === notification.id 
        ? { ...n, actedUpon: true, userAction: actionType, actionTime: new Date().toISOString() }
        : n
    )
    setNotifications(updatedNotifications)
    localStorage.setItem('agentNotifications', JSON.stringify(updatedNotifications))
    
    // Close popup
    setShowNotification(false)
    setCurrentNotification(null)
    
    // Execute the action
    if (onAction) {
      onAction(actionType, actionData, notification)
    }
  }

  const dismissNotification = (notification) => {
    const updatedNotifications = notifications.map(n => 
      n.id === notification.id 
        ? { ...n, dismissed: true, dismissTime: new Date().toISOString() }
        : n
    )
    setNotifications(updatedNotifications)
    localStorage.setItem('agentNotifications', JSON.stringify(updatedNotifications))
    
    setShowNotification(false)
    setCurrentNotification(null)
  }

  const snoozeNotification = (notification, minutes = 15) => {
    const updatedNotifications = notifications.map(n => 
      n.id === notification.id 
        ? { ...n, snoozedUntil: new Date(Date.now() + minutes * 60 * 1000).toISOString() }
        : n
    )
    setNotifications(updatedNotifications)
    localStorage.setItem('agentNotifications', JSON.stringify(updatedNotifications))
    
    setShowNotification(false)
    setCurrentNotification(null)
    
    // Set timer to show again
    setTimeout(() => {
      setCurrentNotification(notification)
      setShowNotification(true)
    }, minutes * 60 * 1000)
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

  // Proactive notification popup
  const NotificationPopup = ({ notification }) => (
    <div className="notification-overlay">
      <div className="notification-popup">
        <div className="notification-header">
          <div className="notification-priority">
            <span className="priority-icon">{getPriorityIcon(notification.priority)}</span>
            <span className="priority-text">{notification.priority} priority</span>
          </div>
          <div className="notification-agent-badge">
            🤖 Autonomous Agent
          </div>
        </div>
        
        <div className="notification-content">
          <h3 className="notification-title">{notification.title}</h3>
          <p className="notification-message">{notification.message}</p>
          
          {notification.reasoning && (
            <div className="notification-reasoning">
              <strong>Agent Reasoning:</strong> {notification.reasoning}
            </div>
          )}
          
          <div className="notification-confidence">
            <div className="confidence-bar">
              <div 
                className="confidence-fill" 
                style={{ width: `${(notification.confidence || 0.5) * 100}%` }}
              />
            </div>
            <span className="confidence-text">
              {Math.round((notification.confidence || 0.5) * 100)}% confidence
            </span>
          </div>
        </div>
        
        <div className="notification-actions">
          {notification.actions && notification.actions.map((action, idx) => (
            <button
              key={idx}
              className={`notification-action-btn ${action.action === 'start_nap' || action.action === 'start_feed' ? 'primary' : 'secondary'}`}
              onClick={() => handleNotificationAction(notification, action.action, action)}
            >
              {action.label}
            </button>
          ))}
          
          <div className="notification-secondary-actions">
            <button
              className="notification-snooze-btn"
              onClick={() => snoozeNotification(notification, 15)}
            >
              Snooze 15m
            </button>
            <button
              className="notification-dismiss-btn"
              onClick={() => dismissNotification(notification)}
            >
              Dismiss
            </button>
          </div>
        </div>
        
        <div className="notification-timestamp">
          Agent observation at {formatTimeAgo(notification.timestamp)}
        </div>
      </div>
    </div>
  )

  // Notification history list
  const NotificationHistory = () => (
    <div className="notification-history">
      <h4>🤖 Agent Activity</h4>
      {notifications.length === 0 ? (
        <div className="no-notifications">
          <p>Agent is monitoring... No recommendations yet.</p>
        </div>
      ) : (
        <div className="notifications-list">
          {notifications.slice(0, 5).map(notification => (
            <div 
              key={notification.id} 
              className={`notification-item ${notification.dismissed ? 'dismissed' : ''} ${notification.actedUpon ? 'acted-upon' : ''}`}
            >
              <div className="notification-item-header">
                <span className="notification-item-icon">
                  {getPriorityIcon(notification.priority)}
                </span>
                <span className="notification-item-title">{notification.title}</span>
                <span className="notification-item-time">
                  {formatTimeAgo(notification.timestamp)}
                </span>
              </div>
              <div className="notification-item-message">
                {notification.message}
              </div>
              {notification.actedUpon && (
                <div className="notification-item-status">
                  ✓ Action taken: {notification.userAction}
                </div>
              )}
              {notification.dismissed && !notification.actedUpon && (
                <div className="notification-item-status dismissed">
                  Dismissed by user
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )

  return (
    <>
      {showNotification && currentNotification && (
        <NotificationPopup notification={currentNotification} />
      )}
      <NotificationHistory />
    </>
  )
}

export default AgentNotifications