import { useState } from 'react'

function BabyProfile({ babyName, babyBirthDate, babyImage, onUpdate, embedded }) {
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    name: babyName || '',
    birthDate: babyBirthDate || '',
    image: babyImage || ''
  })
  
  const handleImageUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setFormData({...formData, image: reader.result})
      }
      reader.readAsDataURL(file)
    }
  }
  
  const calculateAge = () => {
    if (!babyBirthDate) return { months: 0, days: 0 }
    const birth = new Date(babyBirthDate)
    const now = new Date()
    const diffTime = Math.abs(now - birth)
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
    const months = Math.floor(diffDays / 30)
    const days = diffDays % 30
    return { months, days, totalDays: diffDays }
  }
  
  const age = calculateAge()
  
  const getMilestones = () => {
    const months = age.months
    const milestones = []
    
    if (months < 2) {
      milestones.push({ title: 'First Smile', description: 'Coming soon! (6-8 weeks)', icon: '◉', upcoming: true })
      milestones.push({ title: 'Tracks Objects', description: 'Coming soon! (2 months)', icon: '◎', upcoming: true })
    } else if (months < 4) {
      milestones.push({ title: 'First Smile', description: 'Achieved! ✓', icon: '◉', achieved: true })
      milestones.push({ title: 'Holds Head Up', description: 'Coming soon! (4 months)', icon: '▲', upcoming: true })
      milestones.push({ title: 'Laughs Out Loud', description: 'Coming soon! (4 months)', icon: '♪', upcoming: true })
    } else if (months < 6) {
      milestones.push({ title: 'Rolls Over', description: 'Coming soon! (4-6 months)', icon: '◐', upcoming: true })
      milestones.push({ title: 'Sits with Support', description: 'Coming soon! (6 months)', icon: '●', upcoming: true })
    } else if (months < 9) {
      milestones.push({ title: 'Sits Independently', description: 'Achieved! ✓', icon: '●', achieved: true })
      milestones.push({ title: 'First Solid Foods', description: 'Achieved! ✓', icon: '○', achieved: true })
      milestones.push({ title: 'Crawling', description: 'Coming soon! (7-10 months)', icon: '→', upcoming: true })
    } else if (months < 12) {
      milestones.push({ title: 'Crawling', description: 'Achieved! ✓', icon: '→', achieved: true })
      milestones.push({ title: 'Pulls to Stand', description: 'Coming soon! (9-12 months)', icon: '▲', upcoming: true })
      milestones.push({ title: 'First Words', description: 'Coming soon! (10-14 months)', icon: '♪', upcoming: true })
    } else {
      milestones.push({ title: 'First Steps', description: 'Coming soon! (12-15 months)', icon: '▲', upcoming: true })
      milestones.push({ title: 'First Words', description: 'Coming soon! (12-18 months)', icon: '♪', upcoming: true })
    }
    
    return milestones
  }
  
  const memories = [
    { title: 'First Smile', date: age.totalDays >= 45 ? 'Captured!' : 'Coming soon', icon: '◉' },
    { title: 'First Laugh', date: age.totalDays >= 90 ? 'Captured!' : 'Coming soon', icon: '♪' },
    { title: 'First Solid Food', date: age.months >= 6 ? 'Captured!' : 'Coming soon', icon: '○' },
  ]
  
  const handleSave = () => {
    onUpdate(formData.name, formData.birthDate, formData.image)
    setIsEditing(false)
  }
  

  
  const content = (
    <>
      {embedded && (
        <div className="modal-header">
          <div className="header-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="8" r="4" stroke="#F9A8D4" strokeWidth="2.5"/>
              <path d="M6 21C6 17.134 8.686 14 12 14C15.314 14 18 17.134 18 21" stroke="#F9A8D4" strokeWidth="2.5" strokeLinecap="round"/>
            </svg>
          </div>
          <h2>Baby Profile</h2>
        </div>
      )}
      
      <div className="profile-content">
        <div className="profile-card">
          <div className="profile-avatar-large">
            {babyImage || formData.image ? (
              <img src={babyImage || formData.image} alt={babyName} className="profile-avatar-img" />
            ) : (
              <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="8" r="4" fill="white"/>
                <path d="M6 21C6 17.134 8.686 14 12 14C15.314 14 18 17.134 18 21" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
              </svg>
            )}
            {isEditing && (
              <label className="upload-photo-btn">
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={handleImageUpload}
                  style={{ display: 'none' }}
                />
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M23 19C23 19.5304 22.7893 20.0391 22.4142 20.4142C22.0391 20.7893 21.5304 21 21 21H3C2.46957 21 1.96086 20.7893 1.58579 20.4142C1.21071 20.0391 1 19.5304 1 19V8C1 7.46957 1.21071 6.96086 1.58579 6.58579C1.96086 6.21071 2.46957 6 3 6H7L9 3H15L17 6H21C21.5304 6 22.0391 6.21071 22.4142 6.58579C22.7893 6.96086 23 7.46957 23 8V19Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <circle cx="12" cy="13" r="4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </label>
            )}
          </div>
          
          {!isEditing ? (
            <>
              <h3 className="profile-name">{babyName || 'Baby'}</h3>
              <p className="profile-age">{age.months} months, {age.days} days old</p>
              <p className="profile-birthdate">Born: {babyBirthDate ? new Date(babyBirthDate).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) : 'Not set'}</p>
              <button className="btn btn-secondary" onClick={() => setIsEditing(true)} style={{ marginTop: '1rem' }}>
                Edit Profile
              </button>
            </>
          ) : (
            <div className="profile-edit-form">
              <div className="form-group">
                <label>Baby's Name</label>
                <input 
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="input"
                />
              </div>
              <div className="form-group">
                <label>Birth Date</label>
                <input 
                  type="date"
                  value={formData.birthDate}
                  onChange={(e) => setFormData({...formData, birthDate: e.target.value})}
                  className="input"
                />
              </div>
              <div className="form-group">
                <label>Baby Photo</label>
                <input 
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="input"
                  style={{ padding: '0.5rem' }}
                />
                <p style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.7)', marginTop: '0.5rem' }}>
                  Upload a photo to display next to baby's name
                </p>
              </div>
              <div className="form-actions">
                <button className="btn btn-secondary" onClick={() => setIsEditing(false)}>Cancel</button>
                <button className="btn btn-primary" onClick={handleSave}>Save</button>
              </div>
            </div>
          )}
        </div>
        
        <div className="milestones-section">
          <h4>Upcoming Milestones</h4>
          <div className="milestones-list">
            {getMilestones().map((milestone, idx) => (
              <div key={idx} className={`milestone-card ${milestone.achieved ? 'achieved' : ''}`}>
                <div className="milestone-icon">{milestone.icon}</div>
                <div className="milestone-content">
                  <div className="milestone-title">{milestone.title}</div>
                  <div className="milestone-description">{milestone.description}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="memories-section">
          <h4>Precious Memories</h4>
          <div className="memories-list">
            {memories.map((memory, idx) => (
              <div key={idx} className="memory-card">
                <div className="memory-icon">{memory.icon}</div>
                <div className="memory-content">
                  <div className="memory-title">{memory.title}</div>
                  <div className="memory-date">{memory.date}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  )
  
  if (embedded) {
    return <div className="embedded-view">{content}</div>
  }
  
  return content
}

export default BabyProfile
