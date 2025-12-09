import { useState } from 'react'

function DiaperModal({ onClose, onSave }) {
  const [diaperType, setDiaperType] = useState('pee')
  const [date, setDate] = useState(new Date().toISOString().slice(0, 16))
  const [notes, setNotes] = useState('')

  const handleSave = () => {
    onSave('diaper', {
      diaperType,
      timestamp: new Date(date).toISOString(),
      notes: notes || undefined
    })
    onClose()
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Log Diaper Change</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="form-group">
            <label>Type</label>
            <div className="button-group">
              <button 
                className={`option-btn ${diaperType === 'pee' ? 'active' : ''}`}
                onClick={() => setDiaperType('pee')}
              >
                Pee
              </button>
              <button 
                className={`option-btn ${diaperType === 'poop' ? 'active' : ''}`}
                onClick={() => setDiaperType('poop')}
              >
                Poop
              </button>
              <button 
                className={`option-btn ${diaperType === 'both' ? 'active' : ''}`}
                onClick={() => setDiaperType('both')}
              >
                Both
              </button>
            </div>
          </div>

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
            <label>Notes (optional)</label>
            <textarea 
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Color, consistency, etc..."
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

export default DiaperModal
