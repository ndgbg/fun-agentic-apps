import { useState } from 'react'

function NapModal({ onClose, onSave }) {
  const [startTime, setStartTime] = useState(new Date().toISOString().slice(0, 16))
  const [endTime, setEndTime] = useState(new Date().toISOString().slice(0, 16))
  const [notes, setNotes] = useState('')

  const calculateDuration = () => {
    const start = new Date(startTime)
    const end = new Date(endTime)
    const minutes = Math.round((end - start) / 60000)
    return minutes > 0 ? minutes : 0
  }

  const handleSave = () => {
    const duration = calculateDuration()
    if (duration <= 0) {
      alert('End time must be after start time')
      return
    }
    
    onSave('nap', {
      startTime: new Date(startTime).toISOString(),
      endTime: new Date(endTime).toISOString(),
      duration,
      timestamp: new Date(startTime).toISOString(),
      notes: notes || undefined
    })
    onClose()
  }

  const duration = calculateDuration()
  const hours = Math.floor(duration / 60)
  const mins = duration % 60

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Log Nap</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="form-group">
            <label>Start Time</label>
            <input 
              type="datetime-local" 
              value={startTime}
              onChange={(e) => setStartTime(e.target.value)}
              className="input"
            />
          </div>

          <div className="form-group">
            <label>End Time</label>
            <input 
              type="datetime-local" 
              value={endTime}
              onChange={(e) => setEndTime(e.target.value)}
              className="input"
            />
          </div>

          {duration > 0 && (
            <div className="duration-display">
              Duration: {hours > 0 ? `${hours}h ` : ''}{mins}m
            </div>
          )}

          <div className="form-group">
            <label>Notes (optional)</label>
            <textarea 
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Sleep quality, location, etc..."
              className="textarea"
              rows="2"
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

export default NapModal
