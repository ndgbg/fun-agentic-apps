import { useState } from 'react'

function ImportModal({ onClose, onImport }) {
  const [importType, setImportType] = useState('json')
  const [jsonData, setJsonData] = useState('')
  const [csvFile, setCsvFile] = useState(null)

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (event) => {
      try {
        if (importType === 'json') {
          const data = JSON.parse(event.target.result)
          if (!data.activities || !Array.isArray(data.activities)) {
            throw new Error('Invalid JSON format. Expected { "activities": [...] }')
          }
          onImport(data)
          alert(`Successfully imported ${data.activities.length} activities!`)
          onClose()
        } else if (importType === 'csv') {
          const csv = event.target.result
          const activities = parseCSV(csv)
          onImport({ activities })
          alert(`Successfully imported ${activities.length} activities!`)
          onClose()
        }
      } catch (error) {
        alert('Error parsing file: ' + error.message)
      }
    }
    
    reader.readAsText(file)
  }

  const parseCSV = (csv) => {
    const lines = csv.split('\n').filter(line => line.trim())
    if (lines.length < 2) {
      throw new Error('CSV file is empty or invalid')
    }
    
    const headers = lines[0].split('\t').length > 1 
      ? lines[0].split('\t').map(h => h.trim().replace(/"/g, ''))
      : lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
    
    const delimiter = lines[0].split('\t').length > 1 ? '\t' : ','
    
    const activities = []
    for (let i = 1; i < lines.length; i++) {
      // Handle quoted values with commas/tabs
      const values = []
      let currentValue = ''
      let insideQuotes = false
      
      for (let char of lines[i]) {
        if (char === '"') {
          insideQuotes = !insideQuotes
        } else if ((char === delimiter) && !insideQuotes) {
          values.push(currentValue.trim())
          currentValue = ''
        } else {
          currentValue += char
        }
      }
      values.push(currentValue.trim())
      
      const row = {}
      headers.forEach((header, index) => {
        const value = values[index]?.replace(/"/g, '').trim()
        if (value && value !== '') {
          row[header.toLowerCase()] = value
        }
      })
      
      // Convert to our format
      const activity = convertToActivity(row, i)
      if (activity) {
        activities.push(activity)
      }
    }
    
    if (activities.length === 0) {
      throw new Error('No valid activities found in CSV')
    }
    
    return activities
  }

  const convertToActivity = (row, index) => {
    const type = row.type?.toLowerCase()
    if (!type) return null
    
    // Parse timestamp from Start column
    let timestamp
    if (row.start) {
      // Handle formats like "12/4/25 10:45" or "12/4/2025 10:45"
      const dateStr = row.start.trim()
      try {
        // Try parsing as-is first
        let date = new Date(dateStr)
        
        // If invalid, try manual parsing for MM/DD/YY HH:MM format
        if (isNaN(date.getTime())) {
          const match = dateStr.match(/(\d{1,2})\/(\d{1,2})\/(\d{2,4})\s+(\d{1,2}):(\d{2})/)
          if (match) {
            let [, month, day, year, hour, minute] = match
            year = year.length === 2 ? '20' + year : year
            date = new Date(year, month - 1, day, hour, minute)
          }
        }
        
        if (!isNaN(date.getTime())) {
          timestamp = date.toISOString()
        }
      } catch (e) {
        console.warn(`Error parsing date for row ${index + 1}`)
        return null
      }
    } else if (row.timestamp) {
      timestamp = new Date(row.timestamp).toISOString()
    }
    
    if (!timestamp) return null
    
    const activity = {
      id: Date.now() + Math.random() * 10000 + index,
      type,
      timestamp
    }
    
    // Handle different activity types
    if (type === 'feed') {
      // Check Start Condition for feed type
      const startCondition = row['start condition']?.toLowerCase() || row.startcondition?.toLowerCase() || ''
      const startLocation = row['start location']?.toLowerCase() || row.startlocation?.toLowerCase() || ''
      const endCondition = row['end condition'] || row.endcondition || ''
      
      if (startCondition.includes('breast')) {
        activity.feedType = 'breast'
        activity.side = 'both' // Default, could be parsed if specified
      } else if (startCondition.includes('formula') || startLocation.includes('bottle')) {
        activity.feedType = 'bottle'
      } else {
        activity.feedType = 'bottle' // Default
      }
      
      // Parse amount from End Condition (e.g., "80ml", "30ml")
      if (endCondition) {
        const amountMatch = endCondition.match(/(\d+)\s*ml/i)
        if (amountMatch) {
          activity.amount = Math.round(parseFloat(amountMatch[1]) / 29.5735) // Convert ml to oz
        }
      }
    } else if (type === 'diaper') {
      const endCondition = row['end condition']?.toLowerCase() || row.endcondition?.toLowerCase() || ''
      if (endCondition.includes('pee') && endCondition.includes('poop')) {
        activity.diaperType = 'both'
      } else if (endCondition.includes('poop')) {
        activity.diaperType = 'poop'
      } else {
        activity.diaperType = 'pee'
      }
    } else if (type === 'nap' || type === 'sleep') {
      activity.type = 'nap'
      // Parse duration if available
      if (row.duration) {
        const durationMatch = row.duration.match(/(\d+)/)
        if (durationMatch) {
          activity.duration = parseInt(durationMatch[1])
        }
      } else if (row.start && row.end) {
        const start = new Date(row.start)
        const end = new Date(row.end)
        if (!isNaN(start.getTime()) && !isNaN(end.getTime())) {
          activity.duration = Math.round((end - start) / 60000)
        }
      }
    }
    
    // Add notes if present
    if (row.notes) {
      activity.notes = row.notes
    }
    
    return activity
  }

  const handleJsonImport = () => {
    try {
      const data = JSON.parse(jsonData)
      onImport(data)
      onClose()
    } catch (error) {
      alert('Invalid JSON format: ' + error.message)
    }
  }

  const downloadTemplate = () => {
    const template = `type,timestamp,feedType,side,amount,diaperType,duration,medicationName,dosage,activityType,notes
feed,2024-12-04T10:00:00.000Z,breast,left,,,,,,,Morning feed
feed,2024-12-04T13:00:00.000Z,bottle,,4,,,,,,
nap,2024-12-04T11:00:00.000Z,,,,,60,,,,Good nap
nap,2024-12-04T14:30:00.000Z,,,,,45,,,,Short nap
diaper,2024-12-04T12:00:00.000Z,,,pee,,,,,,
diaper,2024-12-04T15:00:00.000Z,,,poop,,,,,,
medication,2024-12-04T09:00:00.000Z,,,,,,"Vitamin D","1 drop",,Daily vitamin
other,2024-12-04T18:00:00.000Z,,,,,,,,bath,Evening bath time`
    
    const blob = new Blob([template], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'momops-import-template.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Import Data</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="modal-body">
          <div className="form-group">
            <label>Import Format</label>
            <div className="button-group">
              <button 
                className={`option-btn ${importType === 'json' ? 'active' : ''}`}
                onClick={() => setImportType('json')}
              >
                JSON
              </button>
              <button 
                className={`option-btn ${importType === 'csv' ? 'active' : ''}`}
                onClick={() => setImportType('csv')}
              >
                CSV
              </button>
            </div>
          </div>

          {importType === 'csv' && (
            <div className="info-box">
              <p><strong>CSV Import:</strong></p>
              <p>• Supports exports from Huckleberry, Baby Tracker, and other apps</p>
              <p>• Accepts tab-separated or comma-separated files</p>
              <p>• Common formats: Type, Start, End, Duration, Start Condition, etc.</p>
              <button className="link-btn" onClick={downloadTemplate}>
                Download CSV Template
              </button>
            </div>
          )}

          {importType === 'json' ? (
            <>
              <div className="form-group">
                <label>Paste JSON Data</label>
                <textarea 
                  value={jsonData}
                  onChange={(e) => setJsonData(e.target.value)}
                  placeholder='{"activities": [...]}'
                  className="textarea"
                  rows="8"
                />
              </div>
              <div className="modal-footer">
                <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
                <button className="btn btn-primary" onClick={handleJsonImport}>Import</button>
              </div>
            </>
          ) : (
            <>
              <div className="form-group">
                <label>Upload CSV File</label>
                <input 
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="file-input"
                />
              </div>
              <div className="modal-footer">
                <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default ImportModal
