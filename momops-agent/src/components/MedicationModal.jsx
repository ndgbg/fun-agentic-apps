import { useState } from 'react'

function MedicationModal({ onClose, onSave }) {
  const [medicationName, setMedicationName] = useState('')
  const [dosage, setDosage] = useState('')
  const [date, setDate] = useState(new Date().toISOString().slice(0, 16))
  const [notes, setNotes] = useState('')

  const handleSave = () => {
    if (!medicationName.trim()) {
      alert('Please enter medication name')
      return
    }
    
    onSave('medication', {
      medicationName,
      dosage: dosage || undefined,
      timestamp: new Date(date).toISOString(),
      notes: notes || undefined
    })
    onClose()
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Log Medication</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="form-group">
            <label>Medication Name</label>
            <input 
              type="text" 
              value={medicationName}
              onChange={(e) => setMedicationName(e.target.value)}
              placeholder="e.g., Tylenol, Vitamin D"
              className="input"
            />
          </div>

          <div className="form-group">
            <label>Dosage (optional)</label>
            <input 
              type="text" 
              value={dosage}
              onChange={(e) => setDosage(e.target.value)}
              placeholder="e.g., 2.5ml, 1 drop"
              className="input"
            />
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
              placeholder="Reason, reaction, etc..."
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

export default MedicationModal
