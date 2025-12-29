import { useState, useEffect } from 'react'
import { llmService } from '../services/LLMService'

function LLMStatus() {
  const [status, setStatus] = useState('not_initialized')
  const [progress, setProgress] = useState(0)
  const [progressText, setProgressText] = useState('')

  useEffect(() => {
    const checkStatus = () => {
      const currentStatus = llmService.getStatus()
      setStatus(currentStatus)
    }

    // Listen for Llama loading progress
    const handleProgress = (event) => {
      setProgress(event.detail.progress)
      setProgressText(event.detail.text)
    }

    window.addEventListener('llmProgress', handleProgress)

    // Check status every second
    const interval = setInterval(checkStatus, 1000)
    checkStatus() // Initial check

    return () => {
      clearInterval(interval)
      window.removeEventListener('llmProgress', handleProgress)
    }
  }, [])

  if (status === 'demo_ready' || status === 'llama_ready') return null // Hide when ready

  return (
    <div className="llm-status-banner">
      <div className="llm-status-content">
        <div className="llm-status-icon">
          {status === 'loading_llama' ? '🦙' : '🧠'}
        </div>
        <div className="llm-status-text">
          {status === 'loading_llama' && `Loading Llama ${progress}%: ${progressText}`}
          {status === 'not_initialized' && 'Preparing AI assistant...'}
        </div>
      </div>
      {status === 'loading_llama' && (
        <div className="llm-progress">
          <div className="llm-progress-bar" style={{ width: `${progress}%` }} />
        </div>
      )}
    </div>
  )
}

export default LLMStatus