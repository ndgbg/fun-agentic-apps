import { useState } from 'react'
import AgentDashboard from './AgentDashboard'

function InsightsView({ activities, babyBirthDate, babyName }) {
  const [activeInsightTab, setActiveInsightTab] = useState('insights')
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
    
    // Feeding pattern
    const feeds = todayActivities.filter(a => a.type === 'feed')
    if (feeds.length > 1) {
      const intervals = []
      for (let i = 1; i < feeds.length; i++) {
        const diff = Math.abs((new Date(feeds[i].timestamp) - new Date(feeds[i-1].timestamp)) / 60000)
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

  const filtered = getFilteredActivities()
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
    <div className="insights-view">
      <div className="insights-tabs">
        <button 
          className={`insight-tab ${activeInsightTab === 'insights' ? 'active' : ''}`}
          onClick={() => setActiveInsightTab('insights')}
        >
          Insights
        </button>
        <button 
          className={`insight-tab ${activeInsightTab === 'agent' ? 'active' : ''}`}
          onClick={() => setActiveInsightTab('agent')}
        >
          AI Agent
        </button>
      </div>

      {activeInsightTab === 'insights' && (
        <div className="insights-content-wrapper">
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
        </div>
      )}

      {activeInsightTab === 'agent' && (
        <AgentDashboard 
          activities={activities}
          babyBirthDate={babyBirthDate}
          babyName={babyName}
          embedded={true}
        />
      )}
    </div>
  )
}

export default InsightsView


