import { useState } from 'react'

function PlanActivityModal({ onClose, onSave, selectedDate }) {
  const [activityType, setActivityType] = useState('feed')
  const [time, setTime] = useState('09:00')
  const [notes, setNotes] = useState('')
  const [feedType, setFeedType] = useState('bottle')
  const [amount, setAmount] = useState('')
  const [napDuration, setNapDuration] = useState('60')
  const [specificActivity, setSpecificActivity] = useState('')

  const handleSave = () => {
    const dateTime = new Date(selectedDate)
    const [hours, minutes] = time.split(':')
    dateTime.setHours(parseInt(hours), parseInt(minutes))
    
    const activity = {
      type: activityType,
      timestamp: dateTime.toISOString(),
      notes: notes || undefined,
      planned: true
    }
    
    if (activityType === 'feed') {
      activity.feedType = feedType
      if (feedType === 'bottle' && amount) {
        activity.amount = amount
      }
    } else if (activityType === 'nap') {
      activity.duration = parseInt(napDuration)
    } else if (activityType === 'other') {
      activity.activityType = specificActivity || 'activity'
    }
    
    onSave('planned', activity)
    onClose()
  }

  const activityOptions = [
    { value: 'tummytime', label: 'Tummy Time' },
    { value: 'bath', label: 'Bath Time' },
    { value: 'reading', label: 'Reading' },
    { value: 'music', label: 'Music & Singing' },
    { value: 'walk', label: 'Outdoor Walk' },
    { value: 'sensory', label: 'Sensory Play' },
    { value: 'massage', label: 'Baby Massage' },
    { value: 'playtime', label: 'Playtime' }
  ]

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Plan Activity</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="form-group">
            <label>Activity Type</label>
            <div className="button-group">
              <button 
                className={`option-btn ${activityType === 'feed' ? 'active' : ''}`}
                onClick={() => setActivityType('feed')}
              >
                Feed
              </button>
              <button 
                className={`option-btn ${activityType === 'nap' ? 'active' : ''}`}
                onClick={() => setActivityType('nap')}
              >
                Nap
              </button>
              <button 
                className={`option-btn ${activityType === 'diaper' ? 'active' : ''}`}
                onClick={() => setActivityType('diaper')}
              >
                Diaper
              </button>
              <button 
                className={`option-btn ${activityType === 'other' ? 'active' : ''}`}
                onClick={() => setActivityType('other')}
              >
                Activity
              </button>
            </div>
          </div>

          {activityType === 'other' && (
            <div className="form-group">
              <label>Select Activity</label>
              <div className="activity-select-grid">
                {activityOptions.map(opt => (
                  <button
                    key={opt.value}
                    className={`option-btn ${specificActivity === opt.value ? 'active' : ''}`}
                    onClick={() => setSpecificActivity(opt.value)}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {activityType === 'feed' && (
            <>
              <div className="form-group">
                <label>Feed Type</label>
                <div className="button-group">
                  <button 
                    className={`option-btn ${feedType === 'breast' ? 'active' : ''}`}
                    onClick={() => setFeedType('breast')}
                  >
                    Breast
                  </button>
                  <button 
                    className={`option-btn ${feedType === 'bottle' ? 'active' : ''}`}
                    onClick={() => setFeedType('bottle')}
                  >
                    Bottle
                  </button>
                </div>
              </div>
              
              {feedType === 'bottle' && (
                <div className="form-group">
                  <label>Amount (oz)</label>
                  <input 
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="e.g., 4"
                    className="input"
                  />
                </div>
              )}
            </>
          )}

          {activityType === 'nap' && (
            <div className="form-group">
              <label>Expected Duration (minutes)</label>
              <input 
                type="number"
                value={napDuration}
                onChange={(e) => setNapDuration(e.target.value)}
                placeholder="e.g., 60"
                className="input"
              />
            </div>
          )}

          <div className="form-group">
            <label>Time</label>
            <input 
              type="time"
              value={time}
              onChange={(e) => setTime(e.target.value)}
              className="input"
            />
          </div>

          <div className="form-group">
            <label>Notes for Nanny (optional)</label>
            <textarea 
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Special instructions..."
              className="textarea"
              rows="2"
            />
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleSave}>Add to Schedule</button>
        </div>
      </div>
    </div>
  )
}

export default PlanActivityModal
