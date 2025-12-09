import { useState } from 'react'

function ExportModal({ activities, onClose }) {
  const [exportFormat, setExportFormat] = useState('json')

  const exportAsJSON = () => {
    const data = JSON.stringify({ activities }, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `momops-export-${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
    onClose()
  }

  const exportAsCSV = () => {
    const headers = ['type', 'timestamp', 'feedType', 'side', 'amount', 'diaperType', 'duration', 'medicationName', 'dosage', 'activityType', 'notes']
    const rows = [headers.join(',')]
    
    activities.forEach(activity => {
      const row = headers.map(header => {
        const value = activity[header] || ''
        return `"${value}"`
      })
      rows.push(row.join(','))
    })
    
    const csv = rows.join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `momops-export-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
    onClose()
  }

  const handleExport = () => {
    if (exportFormat === 'json') {
      exportAsJSON()
    } else {
      exportAsCSV()
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Export Data</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="info-box">
            <p>Export your baby's data to backup or transfer to another app.</p>
            <p><strong>{activities.length}</strong> activities will be exported.</p>
          </div>

          <div className="form-group">
            <label>Export Format</label>
            <div className="button-group">
              <button 
                className={`option-btn ${exportFormat === 'json' ? 'active' : ''}`}
                onClick={() => setExportFormat('json')}
              >
                JSON
              </button>
              <button 
                className={`option-btn ${exportFormat === 'csv' ? 'active' : ''}`}
                onClick={() => setExportFormat('csv')}
              >
                CSV
              </button>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={handleExport}>Export</button>
        </div>
      </div>
    </div>
  )
}

export default ExportModal
