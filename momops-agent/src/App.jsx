import { useState, useEffect } from 'react'
import './App.css'
import FeedModal from './components/FeedModal'
import NapModal from './components/NapModal'
import DiaperModal from './components/DiaperModal'
import MedicationModal from './components/MedicationModal'
import OtherModal from './components/OtherModal'
import ImportModal from './components/ImportModal'
import ExportModal from './components/ExportModal'
import ChatAgent from './components/ChatAgent'
import Analytics from './components/Analytics'
import CalendarView from './components/CalendarView'
import ScheduleManager from './components/ScheduleManager'
import AgentDashboard from './components/AgentDashboard'
import InsightsView from './components/InsightsView'
import { generateSampleData, generateSampleSchedules } from './sampleData'
import { HomeIcon, CalendarIcon, ChartIcon, ScheduleIcon, ChatIcon, ProfileIcon, LogoIcon } from './components/Icons'
import WelcomeScreen from './components/WelcomeScreen'
import BabyProfile from './components/BabyProfile'
import { FeedIcon, NapIcon, DiaperIcon, MedicationIcon, OtherIcon } from './components/ActivityIcons'

function App() {
  const [activities, setActivities] = useState([])
  const [schedules, setSchedules] = useState([])
  const [activeNap, setActiveNap] = useState(null)
  const [showFeedModal, setShowFeedModal] = useState(false)
  const [showNapModal, setShowNapModal] = useState(false)
  const [showDiaperModal, setShowDiaperModal] = useState(false)
  const [showMedicationModal, setShowMedicationModal] = useState(false)
  const [showOtherModal, setShowOtherModal] = useState(false)
  const [showImportModal, setShowImportModal] = useState(false)
  const [showExportModal, setShowExportModal] = useState(false)
  const [showMenu, setShowMenu] = useState(false)
  const [activeTab, setActiveTab] = useState('home')
  const [babyName, setBabyName] = useState('')
  const [babyBirthDate, setBabyBirthDate] = useState('')
  const [babyImage, setBabyImage] = useState('')
  const [showWelcome, setShowWelcome] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem('babyActivities')
    if (saved) {
      const parsed = JSON.parse(saved)
      setActivities(parsed.activities || [])
      setActiveNap(parsed.activeNap || null)
      setSchedules(parsed.schedules || [])
      setBabyName(parsed.babyName || '')
      setBabyBirthDate(parsed.babyBirthDate || '')
      setBabyImage(parsed.babyImage || '')
    }
    
    // Show welcome screen if no baby name or birthdate
    if (!saved || !JSON.parse(saved).babyName || !JSON.parse(saved).babyBirthDate) {
      setShowWelcome(true)
    }
  }, [])

  useEffect(() => {
    localStorage.setItem('babyActivities', JSON.stringify({ activities, activeNap, schedules, babyName, babyBirthDate, babyImage }))
  }, [activities, activeNap, schedules, babyName, babyBirthDate, babyImage])

  const addActivity = (type, details = {}) => {
    const newActivity = {
      id: Date.now(),
      type,
      timestamp: details.timestamp || new Date().toISOString(),
      ...details
    }
    setActivities([newActivity, ...activities].sort((a, b) => 
      new Date(b.timestamp) - new Date(a.timestamp)
    ))
  }

  const startNap = () => {
    const napStart = {
      id: Date.now(),
      type: 'nap',
      startTime: new Date().toISOString()
    }
    setActiveNap(napStart)
  }

  const endNap = () => {
    if (activeNap) {
      const duration = Math.round((new Date() - new Date(activeNap.startTime)) / 60000)
      addActivity('nap', { 
        startTime: activeNap.startTime,
        endTime: new Date().toISOString(),
        duration: duration
      })
      setActiveNap(null)
    }
  }

  const formatTime = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })
  }

  const formatDate = (timestamp) => {
    const date = new Date(timestamp)
    const today = new Date()
    if (date.toDateString() === today.toDateString()) {
      return 'Today'
    }
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday'
    }
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  const handleImport = (data) => {
    if (data.activities && Array.isArray(data.activities)) {
      const existingIds = new Set(activities.map(a => a.id))
      const imported = data.activities.map((a, index) => ({
        ...a,
        id: a.id && !existingIds.has(a.id) ? a.id : Date.now() + Math.random() * 10000 + index
      }))
      const merged = [...imported, ...activities]
      const sorted = merged.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
      const unique = sorted.filter((activity, index, self) => 
        index === self.findIndex(a => 
          a.timestamp === activity.timestamp && 
          a.type === activity.type &&
          JSON.stringify(a) === JSON.stringify(activity)
        )
      )
      setActivities(unique)
    }
  }

  const handleScheduleSave = (schedule, deleteId = null) => {
    if (deleteId) {
      setSchedules(schedules.filter(s => s.id !== deleteId))
    } else {
      const existing = schedules.find(s => s.id === schedule.id)
      if (existing) {
        setSchedules(schedules.map(s => s.id === schedule.id ? schedule : s))
      } else {
        setSchedules([...schedules, schedule])
      }
    }
  }

  const getActivityIcon = (activity) => {
    if (activity.type === 'feed') {
      return <FeedIcon type={activity.feedType} />
    }
    if (activity.type === 'diaper') {
      return <DiaperIcon />
    }
    if (activity.type === 'medication') {
      return <MedicationIcon />
    }
    if (activity.type === 'nap') {
      return <NapIcon />
    }
    if (activity.type === 'other') {
      return <OtherIcon type={activity.activityType} />
    }
    return '·'
  }

  const handleWelcomeComplete = (data) => {
    setBabyName(data.name)
    setBabyBirthDate(data.birthDate)
    if (data.image) setBabyImage(data.image)
    setShowWelcome(false)
  }

  const getActivityDetails = (activity) => {
    if (activity.type === 'feed') {
      const type = activity.feedType === 'breast' ? 'Breastfed' : 'Bottle'
      const side = activity.side ? ` (${activity.side})` : ''
      const amount = activity.amount ? ` • ${activity.amount}oz` : ''
      return `${type}${side}${amount}`
    }
    if (activity.type === 'nap') {
      const duration = activity.duration
      const hours = Math.floor(duration / 60)
      const mins = duration % 60
      return `Nap • ${hours > 0 ? `${hours}h ${mins}m` : `${mins}m`}`
    }
    if (activity.type === 'diaper') {
      const type = activity.diaperType === 'both' ? 'Pee & Poop' : 
                   activity.diaperType === 'poop' ? 'Poop' : 'Pee'
      return `Diaper • ${type}`
    }
    if (activity.type === 'medication') {
      const dosage = activity.dosage ? ` • ${activity.dosage}` : ''
      return `${activity.medicationName}${dosage}`
    }
    if (activity.type === 'other') {
      return activity.activityType.charAt(0).toUpperCase() + activity.activityType.slice(1)
    }
    return ''
  }

  const getLastActivity = (type) => {
    const last = activities.find(a => a.type === type)
    if (!last) return null
    const minutes = Math.round((new Date() - new Date(last.timestamp)) / 60000)
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    return `${hours}h ${minutes % 60}m ago`
  }

  const getNextActivity = (type) => {
    const last = activities.find(a => a.type === type)
    if (!last) return 'Track first'
    
    const minutesSince = Math.round((new Date() - new Date(last.timestamp)) / 60000)
    
    const schedules = {
      feed: { interval: 180, label: '3 hours' },
      nap: { interval: 120, label: '2 hours' },
      diaper: { interval: 180, label: '3 hours' }
    }
    
    const schedule = schedules[type]
    const minutesUntil = schedule.interval - minutesSince
    
    if (minutesUntil <= 0) {
      return 'Due now!'
    } else if (minutesUntil < 60) {
      return `in ${minutesUntil}m`
    } else {
      const hours = Math.floor(minutesUntil / 60)
      const mins = minutesUntil % 60
      return mins > 0 ? `in ${hours}h ${mins}m` : `in ${hours}h`
    }
  }

  if (showWelcome) {
    return <WelcomeScreen onComplete={handleWelcomeComplete} />
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <div className="app-logo">
              <div className="logo-icon">
                <LogoIcon />
              </div>
              <span className="app-name">MomOps</span>
            </div>
            <div className="baby-name">
              <div className="baby-avatar">
                {babyImage ? (
                  <img src={babyImage} alt={babyName} className="baby-avatar-img" />
                ) : (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="8" r="4" fill="white"/>
                    <path d="M6 21C6 17.134 8.686 14 12 14C15.314 14 18 17.134 18 21" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
                  </svg>
                )}
              </div>
              <span>{babyName || 'Baby'}</span>
            </div>
          </div>
          <button className="menu-btn" onClick={() => setShowMenu(!showMenu)}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="10" cy="4" r="1.5" fill="white"/>
              <circle cx="10" cy="10" r="1.5" fill="white"/>
              <circle cx="10" cy="16" r="1.5" fill="white"/>
            </svg>
          </button>
        </div>
        {showMenu && (
          <div className="dropdown-menu">
            <button onClick={() => { setShowImportModal(true); setShowMenu(false); }}>
              Import Data
            </button>
            <button onClick={() => { setShowExportModal(true); setShowMenu(false); }}>
              Export Data
            </button>
            <button onClick={() => { 
              const sampleActivities = generateSampleData()
              const sampleSchedules = generateSampleSchedules()
              setActivities(sampleActivities)
              setSchedules(sampleSchedules)
              setShowMenu(false)
              
              // Set default baby info if not already set
              const sampleBabyName = babyName || 'Emma'
              const sampleBirthDate = babyBirthDate || new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] // 3 months ago
              
              if (!babyName) setBabyName(sampleBabyName)
              if (!babyBirthDate) setBabyBirthDate(sampleBirthDate)
              
              localStorage.setItem('babyActivities', JSON.stringify({ 
                activities: sampleActivities, 
                activeNap: null, 
                schedules: sampleSchedules,
                babyName: sampleBabyName,
                babyBirthDate: sampleBirthDate,
                babyImage
              }))
              alert(`Loaded ${sampleActivities.length} activities and ${sampleSchedules.length} schedules! Baby name set to ${sampleBabyName}.`)
            }}>
              Load Sample Data
            </button>
            {activities.length > 0 && (
              <button onClick={() => { 
                if (confirm('Clear all data? This cannot be undone.')) {
                  setActivities([])
                  setActiveNap(null)
                  setShowMenu(false)
                }
              }}>
                Clear All Data
              </button>
            )}
          </div>
        )}
      </header>

      {activeTab === 'home' && (
        <div className="home-content">
          <div className="quick-stats">
            <div className="stat">
              <span className="stat-label">Last Feed</span>
              <span className="stat-value">{getLastActivity('feed') || 'None'}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Last Nap</span>
              <span className="stat-value">{getLastActivity('nap') || 'None'}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Last Diaper</span>
              <span className="stat-value">{getLastActivity('diaper') || 'None'}</span>
            </div>
          </div>

          <div className="predictions">
            <h3>Predicted Next</h3>
            <div className="prediction-grid">
              <div className="prediction-item">
                <span className="prediction-label">Feed</span>
                <span className="prediction-time">{getNextActivity('feed')}</span>
              </div>
              <div className="prediction-item">
                <span className="prediction-label">Nap</span>
                <span className="prediction-time">{getNextActivity('nap')}</span>
              </div>
              <div className="prediction-item">
                <span className="prediction-label">Diaper</span>
                <span className="prediction-time">{getNextActivity('diaper')}</span>
              </div>
            </div>
          </div>

          <div className="actions">
            <button className="action-btn feed" onClick={() => setShowFeedModal(true)}>
              Feed
            </button>
            
            {activeNap ? (
              <button className="action-btn nap active" onClick={endNap}>
                End Nap
              </button>
            ) : (
              <button className="action-btn nap" onClick={startNap}>
                Start Nap
              </button>
            )}
            
            <button className="action-btn diaper" onClick={() => setShowDiaperModal(true)}>
              Diaper
            </button>
          </div>

          <div className="secondary-actions">
            <button className="action-btn medication" onClick={() => setShowMedicationModal(true)}>
              Medication
            </button>
            <button className="action-btn other" onClick={() => setShowOtherModal(true)}>
              Other
            </button>
          </div>

          <div className="home-milestones">
            <h3>Milestones & Memories</h3>
            <div className="milestone-preview">
              <div className="milestone-preview-item">
                <span className="milestone-preview-icon">◉</span>
                <div>
                  <div className="milestone-preview-title">First Smile</div>
                  <div className="milestone-preview-desc">
                    {babyBirthDate && Math.floor((new Date() - new Date(babyBirthDate)) / (1000 * 60 * 60 * 24)) >= 45 
                      ? 'Captured! ✓' 
                      : 'Coming soon (6-8 weeks)'}
                  </div>
                </div>
              </div>
              <div className="milestone-preview-item">
                <span className="milestone-preview-icon">♪</span>
                <div>
                  <div className="milestone-preview-title">First Laugh</div>
                  <div className="milestone-preview-desc">
                    {babyBirthDate && Math.floor((new Date() - new Date(babyBirthDate)) / (1000 * 60 * 60 * 24 * 30)) >= 3 
                      ? 'Captured! ✓' 
                      : 'Coming soon (3-4 months)'}
                  </div>
                </div>
              </div>
            </div>
            <button className="view-all-btn" onClick={() => setActiveTab('profile')}>
              View All Milestones →
            </button>
          </div>

          {activeNap && (
            <div className="active-nap-banner">
              Nap in progress since {formatTime(activeNap.startTime)}
              <button className="log-nap-btn" onClick={() => setShowNapModal(true)}>
                Log Manually
              </button>
            </div>
          )}

        </div>
      )}

      {activeTab === 'schedule' && (
        <div className="tab-content">
          <CalendarView 
            activities={activities}
            schedules={schedules}
            embedded={true}
            onAddActivity={addActivity}
            babyBirthDate={babyBirthDate}
            babyName={babyName}
            formatTime={formatTime}
            formatDate={formatDate}
            getActivityIcon={getActivityIcon}
            getActivityDetails={getActivityDetails}
          />
        </div>
      )}

      {activeTab === 'analytics' && (
        <div className="tab-content">
          <InsightsView 
            activities={activities}
            babyBirthDate={babyBirthDate}
            babyName={babyName}
          />
        </div>
      )}

      {activeTab === 'nannies' && (
        <div className="tab-content">
          <ScheduleManager 
            schedules={schedules}
            onSave={handleScheduleSave}
            embedded={true}
          />
        </div>
      )}

      {activeTab === 'agent' && (
        <div className="tab-content">
          <AgentDashboard 
            activities={activities}
            babyBirthDate={babyBirthDate}
            babyName={babyName}
            embedded={true}
          />
        </div>
      )}

      {activeTab === 'chat' && (
        <div className="tab-content">
          <ChatAgent 
            activities={activities}
            babyName={babyName}
            babyBirthDate={babyBirthDate}
            embedded={true}
          />
        </div>
      )}

      {activeTab === 'profile' && (
        <div className="tab-content">
          <BabyProfile 
            babyName={babyName}
            babyBirthDate={babyBirthDate}
            babyImage={babyImage}
            onUpdate={(name, birthDate, image) => {
              setBabyName(name)
              setBabyBirthDate(birthDate)
              if (image !== undefined) setBabyImage(image)
            }}
            embedded={true}
          />
        </div>
      )}

      <nav className="bottom-nav">
        <button 
          className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
          onClick={() => setActiveTab('home')}
        >
          <HomeIcon active={activeTab === 'home'} />
          <span>Home</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'schedule' ? 'active' : ''}`}
          onClick={() => setActiveTab('schedule')}
        >
          <CalendarIcon active={activeTab === 'schedule'} />
          <span>Schedule</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          <ChartIcon active={activeTab === 'analytics'} />
          <span>Insights</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'nannies' ? 'active' : ''}`}
          onClick={() => setActiveTab('nannies')}
        >
          <ScheduleIcon active={activeTab === 'nannies'} />
          <span>Caregivers</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <ChatIcon active={activeTab === 'chat'} />
          <span>Chat</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          <ProfileIcon active={activeTab === 'profile'} />
          <span>Profile</span>
        </button>
      </nav>

      {showFeedModal && (
        <FeedModal 
          onClose={() => setShowFeedModal(false)}
          onSave={addActivity}
        />
      )}

      {showNapModal && (
        <NapModal 
          onClose={() => setShowNapModal(false)}
          onSave={addActivity}
        />
      )}

      {showDiaperModal && (
        <DiaperModal 
          onClose={() => setShowDiaperModal(false)}
          onSave={addActivity}
        />
      )}

      {showMedicationModal && (
        <MedicationModal 
          onClose={() => setShowMedicationModal(false)}
          onSave={addActivity}
        />
      )}

      {showOtherModal && (
        <OtherModal 
          onClose={() => setShowOtherModal(false)}
          onSave={addActivity}
        />
      )}

      {showImportModal && (
        <ImportModal 
          onClose={() => setShowImportModal(false)}
          onImport={handleImport}
        />
      )}

      {showExportModal && (
        <ExportModal 
          activities={activities}
          onClose={() => setShowExportModal(false)}
        />
      )}
    </div>
  )
}

export default App
