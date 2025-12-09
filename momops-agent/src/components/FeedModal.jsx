import { useState } from 'react'

function FeedModal({ onClose, onSave }) {
  const [feedType, setFeedType] = useState('breast')
  const [side, setSide] = useState('left')
  const [amount, setAmount] = useState('')
  const [date, setDate] = useState(new Date().toISOString().slice(0, 16))
  const [notes, setNotes] = useState('')

  const handleSave = () => {
    onSave('feed', {
      feedType,
      side: feedType === 'breast' ? side : undefined,
      amount: feedType === 'bottle' && amount ? amount : undefined,
      timestamp: new Date(date).toISOString(),
      notes: notes || undefined
    })
    onClose()
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Log Feeding</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="form-group">
            <label>Type</label>
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

          {feedType === 'breast' && (
            <div className="form-group">
              <label>Side</label>
              <div className="button-group">
                <button 
                  className={`option-btn ${side === 'left' ? 'active' : ''}`}
                  onClick={() => setSide('left')}
                >
                  Left
                </button>
                <button 
                  className={`option-btn ${side === 'right' ? 'active' : ''}`}
                  onClick={() => setSide('right')}
                >
                  Right
                </button>
                <button 
                  className={`option-btn ${side === 'both' ? 'active' : ''}`}
                  onClick={() => setSide('both')}
                >
                  Both
                </button>
              </div>
            </div>
          )}

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
              placeholder="Any observations..."
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

export default FeedModal
