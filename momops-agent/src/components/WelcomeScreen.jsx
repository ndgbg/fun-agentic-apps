import { useState } from 'react'

function WelcomeScreen({ onComplete }) {
  const [babyName, setBabyName] = useState('')
  const [birthDate, setBirthDate] = useState('')
  const [babyImage, setBabyImage] = useState('')

  const handleImageUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setBabyImage(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (babyName.trim() && birthDate) {
      onComplete({ name: babyName.trim(), birthDate, image: babyImage })
    }
  }

  return (
    <div className="welcome-overlay">
      <div className="welcome-modal">
        <div className="welcome-header">
          <div className="welcome-logo">
            <svg width="64" height="64" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="16" cy="16" r="14" fill="url(#gradient)" />
              <path d="M16 8C13 8 11 10 11 13C11 16 13 18 16 18C19 18 21 16 21 13C21 10 19 8 16 8Z" fill="white" opacity="0.9"/>
              <circle cx="16" cy="22" r="2" fill="white" opacity="0.9"/>
              <defs>
                <linearGradient id="gradient" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#A78BFA"/>
                  <stop offset="1" stopColor="#F9A8D4"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1>Welcome to MomOps</h1>
          <p>Let's get started with your baby's information</p>
        </div>
        
        <form onSubmit={handleSubmit} className="welcome-form">
          <div className="form-group">
            <label>Baby's Name</label>
            <input 
              type="text"
              value={babyName}
              onChange={(e) => setBabyName(e.target.value)}
              placeholder="Enter baby's name"
              className="input"
              required
              autoFocus
            />
          </div>
          
          <div className="form-group">
            <label>Birth Date</label>
            <input 
              type="date"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
              className="input"
              required
              max={new Date().toISOString().split('T')[0]}
            />
          </div>

          <div className="form-group">
            <label className="photo-upload-wrapper">
              <input 
                type="file" 
                accept="image/*" 
                onChange={handleImageUpload}
                style={{ display: 'none' }}
              />
              <div className="photo-upload-area">
                {babyImage ? (
                  <>
                    <img src={babyImage} alt="Baby" className="uploaded-photo" />
                    <div className="photo-overlay">
                      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M23 19C23 19.5304 22.7893 20.0391 22.4142 20.4142C22.0391 20.7893 21.5304 21 21 21H3C2.46957 21 1.96086 20.7893 1.58579 20.4142C1.21071 20.0391 1 19.5304 1 19V8C1 7.46957 1.21071 6.96086 1.58579 6.58579C1.96086 6.21071 2.46957 6 3 6H7L9 3H15L17 6H21C21.5304 6 22.0391 6.21071 22.4142 6.58579C22.7893 6.96086 23 7.46957 23 8V19Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <circle cx="12" cy="13" r="4" stroke="white" strokeWidth="2"/>
                      </svg>
                      <span>Change Photo</span>
                    </div>
                  </>
                ) : (
                  <div className="photo-upload-prompt">
                    <div className="upload-icon-circle">
                      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M23 19C23 19.5304 22.7893 20.0391 22.4142 20.4142C22.0391 20.7893 21.5304 21 21 21H3C2.46957 21 1.96086 20.7893 1.58579 20.4142C1.21071 20.0391 1 19.5304 1 19V8C1 7.46957 1.21071 6.96086 1.58579 6.58579C1.96086 6.21071 2.46957 6 3 6H7L9 3H15L17 6H21C21.5304 6 22.0391 6.21071 22.4142 6.58579C22.7893 6.96086 23 7.46957 23 8V19Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        <circle cx="12" cy="13" r="4" stroke="currentColor" strokeWidth="2"/>
                      </svg>
                    </div>
                    <h4>Add Baby's Photo</h4>
                    <p>Click to upload or drag and drop</p>
                    <span className="optional-badge">Optional</span>
                  </div>
                )}
              </div>
            </label>
          </div>
          
          <button type="submit" className="btn btn-primary btn-large">
            Get Started
          </button>
        </form>
      </div>
    </div>
  )
}

export default WelcomeScreen
