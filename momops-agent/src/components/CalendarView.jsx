import { useState } from 'react'
import PlanActivityModal from './PlanActivityModal'

function CalendarView({ activities, schedules, onClose, embedded, onAddActivity, babyBirthDate, babyName, formatTime, formatDate, getActivityIcon, getActivityDetails }) {
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [showPlanModal, setShowPlanModal] = useState(false)
  const [activeTab, setActiveTab] = useState('daily')
  const [editableSchedule, setEditableSchedule] = useState([])
  const [editingItem, setEditingItem] = useState(null)
  
  const getDayActivities = (date) => {
    return activities.filter(a => {
      const activityDate = new Date(a.timestamp)
      return activityDate.toDateString() === date.toDateString()
    })
  }
  
  const getScheduleForDate = (date) => {
    const dayOfWeek = date.toLocaleDateString('en-US', { weekday: 'long' })
    return schedules.filter(s => s.days.includes(dayOfWeek))
  }
  
  const dayActivities = getDayActivities(selectedDate)
  const daySchedules = getScheduleForDate(selectedDate)
  
  // Group activities by hour for timeline view
  const activityTimeline = Array.from({ length: 24 }, (_, hour) => {
    const hourActivities = dayActivities.filter(a => {
      const activityHour = new Date(a.timestamp).getHours()
      return activityHour === hour
    })
    return { hour, activities: hourActivities }
  })
  
  const formatHour = (hour) => {
    if (hour === 0) return '12 AM'
    if (hour < 12) return `${hour} AM`
    if (hour === 12) return '12 PM'
    return `${hour - 12} PM`
  }
  
  const changeDate = (days) => {
    const newDate = new Date(selectedDate)
    newDate.setDate(newDate.getDate() + days)
    setSelectedDate(newDate)
  }
  
  const isToday = selectedDate.toDateString() === new Date().toDateString()
  
  const generateSchedule = () => {
    const age = babyBirthDate ? Math.floor((selectedDate - new Date(babyBirthDate)) / (1000 * 60 * 60 * 24 * 30)) : 6
    
    const schedule = [
      { time: '08:00', type: 'feed', title: 'Morning Milk Feed', icon: '●', notes: 'Breast milk or formula (6-8oz)', duration: '20-30 min' },
      { time: '08:30', type: 'diaper', title: 'Diaper Change', icon: '◆', notes: 'Fresh diaper after feeding' },
      { time: '08:45', type: 'other', title: 'Tummy Time', icon: '▲', notes: '10-15 minutes on play mat', duration: '10-15 min' },
      { time: '09:00', type: 'other', title: 'Music & Singing', icon: '♪', notes: 'Gentle music and nursery rhymes', duration: '15 min' },
      { time: '09:30', type: 'nap', title: 'Morning Nap', icon: '◐', notes: 'Dark room, white noise', duration: '1-2 hours' },
      { time: '11:00', type: 'feed', title: 'Mid-Morning Milk', icon: '●', notes: 'Breast milk or formula (6-8oz)', duration: '20-30 min' },
    ]
    
    if (age >= 6) {
      schedule.push({ time: '11:30', type: 'feed', title: 'Solid Food - Lunch', icon: '○', notes: 'Pureed fruits/vegetables', duration: '15-20 min' })
    }
    
    schedule.push(
      { time: '12:00', type: 'diaper', title: 'Diaper Check', icon: '◆' },
      { time: '12:15', type: 'other', title: 'Outdoor Walk', icon: '→', notes: 'Fresh air, 20-30 minutes', duration: '20-30 min' },
      { time: '13:00', type: 'nap', title: 'Afternoon Nap', icon: '◐', notes: 'Longest nap of the day', duration: '1.5-2 hours' },
      { time: '15:00', type: 'feed', title: 'Afternoon Milk', icon: '●', notes: 'Breast milk or formula (6-8oz)', duration: '20-30 min' },
      { time: '15:30', type: 'diaper', title: 'Diaper Change', icon: '◆' },
      { time: '15:45', type: 'other', title: 'Reading Time', icon: '■', notes: '2-3 board books', duration: '15-20 min' },
      { time: '16:15', type: 'other', title: 'Sensory Play', icon: '◉', notes: 'Textured toys, soft blocks', duration: '20 min' },
      { time: '16:45', type: 'nap', title: 'Late Afternoon Catnap', icon: '◐', notes: 'Short nap, 30-45 min max', duration: '30-45 min' },
      { time: '17:30', type: 'feed', title: 'Dinner Milk', icon: '●', notes: 'Breast milk or formula (6-8oz)', duration: '20-30 min' }
    )
    
    if (age >= 6) {
      schedule.push({ time: '18:00', type: 'feed', title: 'Solid Food - Dinner', icon: '○', notes: 'Variety of flavors', duration: '15-20 min' })
    }
    
    schedule.push(
      { time: '18:30', type: 'other', title: 'Bath Time', icon: '◎', notes: 'Warm bath, gentle wash', duration: '15-20 min' },
      { time: '18:50', type: 'other', title: 'Baby Massage', icon: '◈', notes: 'Calming massage with lotion', duration: '10 min' },
      { time: '19:00', type: 'diaper', title: 'Fresh Diaper & Pajamas', icon: '◆', notes: 'Night diaper and PJs' },
      { time: '19:15', type: 'feed', title: 'Bedtime Milk', icon: '●', notes: 'Final feed, dim lights', duration: '20-30 min' },
      { time: '19:45', type: 'other', title: 'Bedtime Story', icon: '■', notes: 'Quiet story, 1-2 books', duration: '10 min' },
      { time: '20:00', type: 'nap', title: 'Bedtime', icon: '◑', notes: 'Lights out, white noise, sleep sack', duration: 'overnight' }
    )
    
    setEditableSchedule(schedule.map((item, idx) => ({ ...item, id: idx })))
  }
  
  const updateScheduleItem = (id, field, value) => {
    setEditableSchedule(schedule => 
      schedule.map(item => item.id === id ? { ...item, [field]: value } : item)
    )
  }
  
  const deleteScheduleItem = (id) => {
    setEditableSchedule(schedule => schedule.filter(item => item.id !== id))
  }
  
  const generateDailySchedulePDF = () => {
    if (editableSchedule.length === 0) {
      alert('Please generate a schedule first!')
      return
    }
    
    const generateHTML = () => {
      const dateStr = selectedDate.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })
      
      // Use the editable schedule that was generated and edited
      const schedule = editableSchedule
      
      // Add caregiver info
      const caregivers = daySchedules.filter(s => s.type === 'nanny')
      
      // Old schedule generation code removed - now using editableSchedule
      if (false) {
        schedule.push({ 
          time: '08:00', 
          type: 'feed', 
          title: 'Morning Milk Feed', 
          icon: '●', 
          notes: 'Breast milk or formula (6-8oz)',
          duration: '20-30 min'
        })
        
        schedule.push({ 
          time: '08:30', 
          type: 'diaper', 
          title: 'Diaper Change', 
          icon: '◆', 
          notes: 'Fresh diaper after feeding'
        })
        
        schedule.push({ 
          time: '08:45', 
          type: 'other', 
          title: 'Tummy Time', 
          icon: '▲', 
          notes: '10-15 minutes on play mat. Encourage reaching and rolling.',
          duration: '10-15 min'
        })
        
        schedule.push({ 
          time: '09:00', 
          type: 'other', 
          title: 'Music & Singing', 
          icon: '♪', 
          notes: 'Play gentle music, sing nursery rhymes. Use rattles and musical toys.',
          duration: '15 min'
        })
        
        schedule.push({ 
          time: '09:30', 
          type: 'nap', 
          title: 'Morning Nap', 
          icon: '◐',
          notes: 'Put down for nap. Dark room, white noise. Watch for sleep cues.',
          duration: '1-2 hours'
        })
        
        // Mid-morning
        schedule.push({ 
          time: '11:00', 
          type: 'feed', 
          title: 'Mid-Morning Milk', 
          icon: '●', 
          notes: 'Breast milk or formula (6-8oz)',
          duration: '20-30 min'
        })
        
        if (babyAge >= 6) {
          schedule.push({ 
            time: '11:30', 
            type: 'feed', 
            title: 'Solid Food - Lunch', 
            icon: '○', 
            notes: `Food: ${getFoodRecommendations()}. Start with 2-3 tablespoons.`,
            duration: '15-20 min'
          })
        }
        
        schedule.push({ 
          time: '12:00', 
          type: 'diaper', 
          title: 'Diaper Check', 
          icon: '◆'
        })
        
        schedule.push({ 
          time: '12:15', 
          type: 'other', 
          title: 'Outdoor Walk', 
          icon: '→', 
          notes: 'Fresh air and sunshine. Stroller walk around neighborhood. 20-30 minutes.',
          duration: '20-30 min'
        })
        
        schedule.push({ 
          time: '13:00', 
          type: 'nap', 
          title: 'Afternoon Nap', 
          icon: '◐', 
          notes: 'Longest nap of the day. Dark room, comfortable temperature.',
          duration: '1.5-2 hours'
        })
        
        // Afternoon
        schedule.push({ 
          time: '15:00', 
          type: 'feed', 
          title: 'Afternoon Milk', 
          icon: '●', 
          notes: 'Breast milk or formula (6-8oz)',
          duration: '20-30 min'
        })
        
        schedule.push({ 
          time: '15:30', 
          type: 'diaper', 
          title: 'Diaper Change', 
          icon: '◆'
        })
        
        schedule.push({ 
          time: '15:45', 
          type: 'other', 
          title: 'Reading Time', 
          icon: '■', 
          notes: 'Read 2-3 board books. Point to pictures, use different voices. Encourage touching pages.',
          duration: '15-20 min'
        })
        
        schedule.push({ 
          time: '16:15', 
          type: 'other', 
          title: 'Sensory Play', 
          icon: '◉', 
          notes: 'Crinkle toys, textured balls, soft blocks. Let baby explore different textures.',
          duration: '20 min'
        })
        
        schedule.push({ 
          time: '16:45', 
          type: 'nap', 
          title: 'Late Afternoon Catnap', 
          icon: '◐', 
          notes: 'Short nap to bridge to bedtime. 30-45 minutes max.',
          duration: '30-45 min'
        })
        
        // Evening
        schedule.push({ 
          time: '17:30', 
          type: 'feed', 
          title: 'Dinner Milk', 
          icon: '●', 
          notes: 'Breast milk or formula (6-8oz)',
          duration: '20-30 min'
        })
        
        if (babyAge >= 6) {
          schedule.push({ 
            time: '18:00', 
            type: 'feed', 
            title: 'Solid Food - Dinner', 
            icon: '○', 
            notes: `Food: ${getFoodRecommendations()}. Offer variety of flavors.`,
            duration: '15-20 min'
          })
        }
        
        schedule.push({ 
          time: '18:30', 
          type: 'other', 
          title: 'Bath Time', 
          icon: '◎', 
          notes: 'Warm bath (not too hot). Gentle baby wash. Make it fun with bath toys. Pat dry gently.',
          duration: '15-20 min'
        })
        
        schedule.push({ 
          time: '18:50', 
          type: 'other', 
          title: 'Baby Massage', 
          icon: '◈', 
          notes: 'Gentle massage with baby lotion. Calming strokes on arms, legs, back. Helps with sleep.',
          duration: '10 min'
        })
        
        schedule.push({ 
          time: '19:00', 
          type: 'diaper', 
          title: 'Fresh Diaper & Pajamas', 
          icon: '◆', 
          notes: 'Clean diaper, comfortable pajamas for night'
        })
        
        schedule.push({ 
          time: '19:15', 
          type: 'feed', 
          title: 'Bedtime Milk', 
          icon: '●', 
          notes: 'Final feed before bed. Breast milk or formula (6-8oz). Keep lights dim.',
          duration: '20-30 min'
        })
        
        schedule.push({ 
          time: '19:45', 
          type: 'other', 
          title: 'Bedtime Story', 
          icon: '■',
          notes: 'Quiet story time. Soft voice, dim lights. 1-2 short books.',
          duration: '10 min'
        })
        
        schedule.push({ 
          time: '20:00', 
          type: 'nap', 
          title: 'Bedtime', 
          icon: '◑', 
          notes: 'Lights out. White noise on. Sleep sack. Room temperature 68-72°F.',
          duration: 'overnight'
        })
      } else {
        // Use actual activities for past/today
        dayActivities.forEach(a => {
          const time = new Date(a.timestamp).toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false
          })
          
          let title = '', icon = ''
          if (a.type === 'feed') {
            title = a.feedType === 'breast' ? 'Breastfeeding' : `Bottle Feed${a.amount ? ' (' + a.amount + 'oz)' : ''}`
            icon = '●'
          } else if (a.type === 'nap') {
            title = 'Nap'
            icon = '◐'
            if (a.duration) {
              const h = Math.floor(a.duration / 60)
              const m = a.duration % 60
              schedule.duration = h > 0 ? `${h}h ${m}m` : `${m}m`
            }
          } else if (a.type === 'diaper') {
            title = 'Diaper Change'
            icon = '◆'
          } else if (a.type === 'medication') {
            title = `${a.medicationName}${a.dosage ? ' - ' + a.dosage : ''}`
            icon = '+'
          } else if (a.type === 'other') {
            title = a.activityType.charAt(0).toUpperCase() + a.activityType.slice(1)
            icon = '◉'
          }
          
          schedule.push({ time, type: a.type, title, icon, notes: a.notes, duration: schedule.duration })
        })
      }
      
      // Sort by time
      schedule.sort((a, b) => a.time.localeCompare(b.time))
      
      // Generate beautiful HTML
      return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      padding: 40px 20px;
      color: #1e293b;
    }
    .container {
      max-width: 800px;
      margin: 0 auto;
      background: white;
      border-radius: 24px;
      overflow: hidden;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    .header {
      background: linear-gradient(135deg, #A78BFA 0%, #F9A8D4 100%);
      padding: 40px;
      text-align: center;
      color: white;
    }
    .header h1 {
      font-size: 36px;
      font-weight: 800;
      margin-bottom: 8px;
      letter-spacing: -1px;
    }
    .header .date {
      font-size: 18px;
      opacity: 0.95;
      font-weight: 500;
    }
    .header .baby-name {
      font-size: 24px;
      margin-top: 16px;
      padding: 12px 24px;
      background: rgba(255,255,255,0.2);
      border-radius: 20px;
      display: inline-block;
      backdrop-filter: blur(10px);
    }
    .content {
      padding: 40px;
    }
    .section {
      margin-bottom: 40px;
    }
    .section-title {
      font-size: 20px;
      font-weight: 700;
      margin-bottom: 20px;
      color: #A78BFA;
      display: flex;
      align-items: center;
      gap: 12px;
      padding-bottom: 12px;
      border-bottom: 3px solid #F3F4F6;
    }
    .caregiver-card {
      background: #F8FAFC;
      padding: 20px;
      border-radius: 16px;
      margin-bottom: 16px;
      border-left: 4px solid #A78BFA;
    }
    .caregiver-card .name {
      font-size: 18px;
      font-weight: 700;
      margin-bottom: 8px;
    }
    .caregiver-card .time {
      color: #64748B;
      font-size: 16px;
      font-weight: 600;
    }
    .schedule-item {
      display: flex;
      gap: 20px;
      padding: 20px;
      margin-bottom: 12px;
      background: #F8FAFC;
      border-radius: 16px;
      border-left: 4px solid #E2E8F0;
      transition: all 0.2s;
    }
    .schedule-item:hover {
      background: #F1F5F9;
      transform: translateX(4px);
    }
    .schedule-item.feed { border-left-color: #93C5FD; }
    .schedule-item.nap { border-left-color: #A78BFA; }
    .schedule-item.diaper { border-left-color: #FCD34D; }
    .schedule-item.medication { border-left-color: #FCA5A5; }
    .schedule-item.other { border-left-color: #86EFAC; }
    .time-badge {
      font-size: 16px;
      font-weight: 700;
      color: #475569;
      min-width: 80px;
      padding: 8px 16px;
      background: white;
      border-radius: 12px;
      text-align: center;
      align-self: flex-start;
    }
    .activity-content {
      flex: 1;
    }
    .activity-title {
      font-size: 18px;
      font-weight: 700;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .activity-notes {
      color: #64748B;
      font-size: 14px;
      margin-top: 4px;
      font-style: italic;
    }
    .activity-duration {
      color: #A78BFA;
      font-size: 14px;
      font-weight: 600;
      margin-top: 4px;
    }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-top: 20px;
    }
    .summary-card {
      background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
      padding: 24px;
      border-radius: 16px;
      text-align: center;
      border: 2px solid #E2E8F0;
    }
    .summary-card .value {
      font-size: 32px;
      font-weight: 800;
      background: linear-gradient(135deg, #A78BFA 0%, #F9A8D4 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 8px;
    }
    .summary-card .label {
      color: #64748B;
      font-size: 14px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .notes-box {
      background: #FEF3C7;
      padding: 24px;
      border-radius: 16px;
      border-left: 4px solid #FCD34D;
    }
    .notes-box h3 {
      font-size: 18px;
      margin-bottom: 16px;
      color: #92400E;
    }
    .notes-box ul {
      list-style: none;
      padding: 0;
    }
    .notes-box li {
      padding: 8px 0;
      color: #78350F;
      font-size: 15px;
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .notes-box li:before {
      content: "✓";
      background: #FCD34D;
      color: #78350F;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      flex-shrink: 0;
    }
    .footer {
      text-align: center;
      padding: 30px;
      background: #F8FAFC;
      color: #94A3B8;
      font-size: 14px;
    }
    .footer strong {
      color: #64748B;
    }
    @media print {
      body { background: white; padding: 0; }
      .container { box-shadow: none; }
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Daily Schedule</h1>
      <div class="date">${dateStr}</div>
      <div class="baby-name">${babyName}</div>
    </div>
    
    <div class="content">
      ${caregivers.length > 0 ? `
      <div class="section">
        <div class="section-title">
          <span>◉</span>
          <span>Caregiver On Duty</span>
        </div>
        ${caregivers.map(c => `
          <div class="caregiver-card">
            <div class="name">${c.title}${c.person ? ' - ' + c.person : ''}</div>
            <div class="time">${c.startTime} - ${c.endTime}</div>
            ${c.notes ? `<div class="activity-notes">${c.notes}</div>` : ''}
          </div>
        `).join('')}
      </div>
      ` : ''}
      
      <div class="section">
        <div class="section-title">
          <span>◆</span>
          <span>Today's Schedule</span>
        </div>
        ${schedule.map(item => `
          <div class="schedule-item ${item.type}">
            <div class="time-badge">${item.time}</div>
            <div class="activity-content">
              <div class="activity-title">
                <span>${item.icon}</span>
                <span>${item.title}</span>
              </div>
              ${item.duration ? `<div class="activity-duration">Duration: ${item.duration}</div>` : ''}
              ${item.notes ? `<div class="activity-notes">${item.notes}</div>` : ''}
            </div>
          </div>
        `).join('')}
      </div>
      
      <div class="section">
        <div class="notes-box">
          <h3>◈ Important Reminders</h3>
          <ul>
            <li>Always supervise baby during activities</li>
            <li>Check diaper regularly throughout the day</li>
            <li>Watch for hunger and sleep cues</li>
            <li>Keep emergency contacts handy</li>
            <li>Call parent immediately if any concerns</li>
          </ul>
        </div>
      </div>
    </div>
    
    <div class="footer">
      <strong>Generated by MomOps</strong><br>
      ${new Date().toLocaleString()}
    </div>
  </div>
</body>
</html>
      `
    }
    
    const htmlContent = generateHTML()
    const blob = new Blob([htmlContent], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${babyName}-schedule-${selectedDate.toISOString().split('T')[0]}.html`
    a.click()
    URL.revokeObjectURL(url)
    
    // Also open in new window for printing
    const printWindow = window.open('', '_blank')
    printWindow.document.write(htmlContent)
    printWindow.document.close()
    
    console.log('Schedule items:', schedule.length)
    console.log('First item:', schedule[0])
    alert('Beautiful schedule generated! [v2.0 - Detailed] You can print it as PDF (Ctrl/Cmd + P) or save the HTML file.')
  }
  
  const content = (
    <>
      {!embedded && (
        <div className="modal-header">
          <h2>Calendar View</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
      )}
      {embedded && (
        <div className="modal-header">
          <div className="header-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="4" width="18" height="18" rx="2" stroke="#F9A8D4" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M16 2V6M8 2V6M3 10H21" stroke="#F9A8D4" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              <circle cx="8" cy="14" r="1.5" fill="#F9A8D4"/>
              <circle cx="12" cy="14" r="1.5" fill="#F9A8D4"/>
              <circle cx="16" cy="14" r="1.5" fill="#F9A8D4"/>
            </svg>
          </div>
          <h2>Calendar</h2>
        </div>
      )}
        
        <div className="calendar-content">
          <div className="date-navigator">
            <button className="nav-btn" onClick={() => changeDate(-1)}>‹</button>
            <div className="date-display">
              <h3>{selectedDate.toLocaleDateString('en-US', { weekday: 'long' })}</h3>
              <p>{selectedDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</p>
              {isToday && <span className="today-badge">Today</span>}
            </div>
            <button className="nav-btn" onClick={() => changeDate(1)}>›</button>
          </div>
          

          
          <div className="schedule-tabs">
            <button 
              className={`tab-btn ${activeTab === 'daily' ? 'active' : ''}`}
              onClick={() => setActiveTab('daily')}
            >
              List View
            </button>
            <button 
              className={`tab-btn ${activeTab === 'timeline' ? 'active' : ''}`}
              onClick={() => setActiveTab('timeline')}
            >
              Calendar View
            </button>
            <button 
              className={`tab-btn ${activeTab === 'generate' ? 'active' : ''}`}
              onClick={() => setActiveTab('generate')}
            >
              Generate Schedule
            </button>
          </div>
          
          {activeTab === 'daily' && (
            <div className="timeline-section">
              {dayActivities.length === 0 ? (
                <p className="empty-state">No activities yet. Start tracking!</p>
              ) : (
                <div className="activity-list">
                  {dayActivities.map((activity, index) => {
                    const showDate = index === 0 || 
                      (formatDate && formatDate(activity.timestamp) !== formatDate(dayActivities[index - 1].timestamp))
                    
                    return (
                      <div key={activity.id}>
                        {showDate && formatDate && (
                          <div className="date-divider">{formatDate(activity.timestamp)}</div>
                        )}
                        <div className="activity-item">
                          <span className="activity-icon">{getActivityIcon ? getActivityIcon(activity) : '●'}</span>
                          <div className="activity-details">
                            <span className="activity-type">
                              {getActivityDetails ? getActivityDetails(activity) : activity.type}
                            </span>
                            {activity.notes && (
                              <span className="activity-notes">{activity.notes}</span>
                            )}
                          </div>
                          <span className="activity-time">{formatTime ? formatTime(activity.timestamp) : new Date(activity.timestamp).toLocaleTimeString()}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          )}
          
          {activeTab === 'timeline' && (
            <div className="timeline-section">
              {daySchedules.length > 0 && (
                <div className="schedule-section" style={{ marginBottom: '1.5rem' }}>
                  <h4>Caregiver On Duty</h4>
                  {daySchedules.map((schedule, idx) => (
                    <div key={idx} className={`schedule-card ${schedule.type}`}>
                      <div className="schedule-header">
                        <span className="schedule-title">{schedule.title}</span>
                        <span className="schedule-time">{schedule.startTime} - {schedule.endTime}</span>
                      </div>
                      {schedule.person && (
                        <div className="schedule-person">{schedule.person}</div>
                      )}
                      {schedule.notes && (
                        <div className="schedule-notes">{schedule.notes}</div>
                      )}
                    </div>
                  ))}
                </div>
              )}
              
              <div className="timeline-scroll">
                {activityTimeline.map(({ hour, activities }) => (
                  <div key={hour} className="timeline-hour">
                    <div className="hour-label">{formatHour(hour)}</div>
                    <div className="hour-activities">
                      {activities.length > 0 ? (
                        activities.map(activity => (
                          <div key={activity.id} className={`timeline-activity ${activity.type}`}>
                            <span className="activity-time">
                              {new Date(activity.timestamp).toLocaleTimeString('en-US', { 
                                hour: 'numeric', 
                                minute: '2-digit' 
                              })}
                            </span>
                            <span className="activity-label">
                              {activity.type === 'feed' && (activity.feedType === 'breast' ? 'Breastfed' : 'Bottle')}
                              {activity.type === 'nap' && `Nap (${activity.duration}m)`}
                              {activity.type === 'diaper' && `Diaper (${activity.diaperType})`}
                              {activity.type === 'medication' && activity.medicationName}
                              {activity.type === 'other' && activity.activityType}
                            </span>
                          </div>
                        ))
                      ) : (
                        <div className="no-activities">—</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {activeTab === 'generate' && (
            <div className="generate-schedule-section">
              <button 
                className="btn btn-primary" 
                onClick={generateSchedule}
                style={{ width: '100%', marginBottom: '1.5rem' }}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '0.5rem' }}>
                  <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2.5"/>
                  <path d="M12 2V6M12 18V22M22 12H18M6 12H2" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"/>
                  <path d="M17.5 6.5L15 9M9 15L6.5 17.5M17.5 17.5L15 15M9 9L6.5 6.5" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"/>
                </svg>
                {editableSchedule.length > 0 ? 'Regenerate AI Schedule' : 'Generate AI Schedule'}
              </button>

              <div className="info-box" style={{ marginBottom: '1.5rem' }}>
                <p><strong>🤖 AI-Generated Daily Schedule</strong></p>
                <p>Create an intelligent schedule based on {babyName}'s age and patterns. Edit items, then download to share with your caregiver.</p>
              </div>
              
              <div className="generate-preview">
                <h4 style={{ marginBottom: '1rem' }}>Schedule for {selectedDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</h4>
                {editableSchedule.length === 0 ? (
                  <div className="empty-state" style={{ padding: '3rem 2rem', textAlign: 'center' }}>
                    <div className="empty-icon" style={{ fontSize: '3rem', marginBottom: '1rem' }}>🤖</div>
                    <h4 style={{ marginBottom: '0.5rem' }}>Ready to Generate</h4>
                    <p style={{ marginBottom: '1.5rem', color: 'var(--text-tertiary)' }}>Click the button above to create an AI-powered daily schedule</p>
                  </div>
                ) : (
                  <div className="preview-items">
                    {editableSchedule.map(item => (
                      <div key={item.id} className="preview-item editable">
                        <span className="preview-icon">{item.icon}</span>
                        {editingItem === item.id ? (
                          <div className="edit-item-form">
                            <input 
                              type="time"
                              value={item.time}
                              onChange={(e) => updateScheduleItem(item.id, 'time', e.target.value)}
                              className="input-small"
                            />
                            <input 
                              type="text"
                              value={item.title}
                              onChange={(e) => updateScheduleItem(item.id, 'title', e.target.value)}
                              className="input-small"
                              placeholder="Activity title"
                            />
                            <input 
                              type="text"
                              value={item.notes || ''}
                              onChange={(e) => updateScheduleItem(item.id, 'notes', e.target.value)}
                              className="input-small"
                              placeholder="Notes (optional)"
                            />
                            <button className="btn-icon" onClick={() => setEditingItem(null)}>✓</button>
                          </div>
                        ) : (
                          <>
                            <span className="preview-text">
                              {item.time} - {item.title}
                              {item.duration && ` (${item.duration})`}
                            </span>
                            <div className="preview-actions">
                              <button className="btn-icon" onClick={() => setEditingItem(item.id)}>✎</button>
                              <button className="btn-icon delete" onClick={() => deleteScheduleItem(item.id)}>×</button>
                            </div>
                          </>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                {editableSchedule.length > 0 && (
                  <div className="schedule-actions" style={{ marginTop: '1.5rem', display: 'flex', gap: '0.75rem' }}>
                    <button className="btn btn-secondary" onClick={() => setEditableSchedule([])}>
                      Clear Schedule
                    </button>
                    <button className="btn btn-primary" onClick={generateDailySchedulePDF} style={{ flex: 1 }}>
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '0.5rem' }}>
                        <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M12 18V12M9 15L12 18L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                      Finalize & Download PDF
                    </button>
                  </div>
                )}
              </div>

            </div>
          )}
        </div>
        
        {showPlanModal && (
          <PlanActivityModal 
            selectedDate={selectedDate}
            onClose={() => setShowPlanModal(false)}
            onSave={(type, details) => {
              if (onAddActivity) {
                onAddActivity(type, details)
              }
              setShowPlanModal(false)
            }}
          />
        )}
    </>
  )
  
  if (embedded) {
    return <div className="embedded-view">{content}</div>
  }
  
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="calendar-modal" onClick={(e) => e.stopPropagation()}>
        {content}
      </div>
    </div>
  )
}

export default CalendarView
