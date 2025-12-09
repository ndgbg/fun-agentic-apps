import { useState } from 'react'

function OtherModal({ onClose, onSave }) {
  const [activityType, setActivityType] = useState('bath')
  const [customType, setCustomType] = useState('')
  const [date, setDate] = useState(new Date().toISOString().slice(0, 16))
  const [notes, setNotes] = useState('')

  const predefinedTypes = [
    { value: 'bath', label: 'Bath', icon: 'B' },
    { value: 'tummytime', label: 'Tummy Time', icon: 'T' },
    { value: 'temperature', label: 'Temperature', icon: '°' },
    { value: 'weight', label: 'Weight', icon: 'W' },
    { value: 'milestone', label: 'Milestone', icon: 'M' },
    { value: 'custom', label: 'Custom', icon: '·' }
  ]

  const handleSave = () => {
    const type = activityType === 'custom' ? customType : activityType
    if (!type.trim()) {
      alert('Please enter activity type')
      return
    }
    
    onSave('other', {
      activityType: type,
      timestamp: new Date(date).toISOString(),
      notes: notes || undefined
    })
    onClose()
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Log Activity</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="form-group">
            <label>Activity Type</label>
            <div className="activity-grid">
              {predefinedTypes.map(type => (
                <button 
                  key={type.value}
                  className={`activity-option ${activityType === type.value ? 'active' : ''}`}
                  onClick={() => setActivityType(type.value)}
                >
                  <span className="activity-icon">{type.icon}</span>
                  <span className="activity-label">{type.label}</span>
                </button>
              ))}
            </div>
          </div>

          {activityType === 'custom' && (
            <div className="form-group">
              <label>Custom Activity</label>
              <input 
                type="text" 
                value={customType}
                onChange={(e) => setCustomType(e.target.value)}
                placeholder="e.g., Doctor visit, Playtime"
                className="input"
              />
            </div>
          )}

          <div className="form-group">
            <label>Date & Time</label>
            <input 
              type="datetime-local" 
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="input"
            />
          </div>

          <div className="form-group">
            <label>Details</label>
            <textarea 
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add details about this activity..."
              className="textarea"
              rows="3"
            />
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSave}>Save</button>
        </div>
      </div>
    </div>
  )
}

export default OtherModal
