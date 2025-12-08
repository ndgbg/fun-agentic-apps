import { useState } from 'react'

function ChatAgent({ activities, babyName, babyBirthDate, onClose, embedded }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: `Hi! I'm your MomOps assistant${babyName ? ` for ${babyName}` : ''}. Ask me anything about your baby's schedule, patterns, or get parenting advice!` }
  ])
  const [input, setInput] = useState('')
  
  const getBabyAge = () => {
    if (!babyBirthDate) return null
    const birth = new Date(babyBirthDate)
    const now = new Date()
    const diffTime = Math.abs(now - birth)
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
    const months = Math.floor(diffDays / 30)
    const days = diffDays % 30
    return { months, days, totalDays: diffDays }
  }

  const analyzeSchedule = () => {
    const feeds = activities.filter(a => a.type === 'feed')
    const naps = activities.filter(a => a.type === 'nap')
    const diapers = activities.filter(a => a.type === 'diaper')
    
    return {
      totalFeeds: feeds.length,
      totalNaps: naps.length,
      totalDiapers: diapers.length,
      avgNapDuration: naps.length > 0 
        ? Math.round(naps.reduce((sum, n) => sum + (n.duration || 0), 0) / naps.length)
        : 0,
      lastFeed: feeds[0],
      lastNap: naps[0]
    }
  }

  const generateResponse = (question) => {
    const q = question.toLowerCase()
    const stats = analyzeSchedule()
    const age = getBabyAge()
    const babyRef = babyName || 'your baby'
    
    // Feeding questions
    if (q.includes('feed') || q.includes('eat') || q.includes('hungry') || q.includes('bottle') || q.includes('breast')) {
      if (stats.lastFeed) {
        const minutesAgo = Math.round((new Date() - new Date(stats.lastFeed.timestamp)) / 60000)
        const hoursAgo = Math.floor(minutesAgo / 60)
        return `${babyRef} last fed ${hoursAgo}h ${minutesAgo % 60}m ago. Babies typically feed every 2-3 hours. ${minutesAgo > 180 ? "It might be time for another feeding soon!" : "You're on track!"}\n\nTip: Watch for hunger cues like rooting, sucking on hands, or fussiness.`
      }
      return "I don't see any feeding records yet. Start tracking to get personalized insights!"
    }
    
    // Sleep questions
    if (q.includes('nap') || q.includes('sleep') || q.includes('tired') || q.includes('bedtime')) {
      if (stats.lastNap) {
        const minutesAgo = Math.round((new Date() - new Date(stats.lastNap.timestamp)) / 60000)
        const avgDuration = stats.avgNapDuration
        return `Last nap was ${Math.floor(minutesAgo / 60)}h ${minutesAgo % 60}m ago. Average nap duration: ${Math.floor(avgDuration / 60)}h ${avgDuration % 60}m.\n\nBabies under 1 year typically need 2-4 naps per day. Look for sleep cues like yawning, eye rubbing, or fussiness.`
      }
      return "Track some naps first, and I'll help you identify sleep patterns! Tip: Babies need 12-16 hours of sleep per day."
    }
    
    // Pattern/schedule questions
    if (q.includes('pattern') || q.includes('schedule') || q.includes('routine')) {
      return `Today's summary for ${babyRef}:\n• ${stats.totalFeeds} feedings\n• ${stats.totalNaps} naps\n• ${stats.totalDiapers} diaper changes\n\nYou're doing great! Consistency helps establish routines. Try to keep feeding and nap times similar each day.`
    }
    
    // Diaper questions
    if (q.includes('diaper') || q.includes('poop') || q.includes('pee')) {
      return `You've logged ${stats.totalDiapers} diaper changes. Newborns typically need 8-12 changes per day.\n\nWatch for at least 6 wet diapers daily as a sign of good hydration. Poop frequency varies - some babies go after every feeding, others once a day.`
    }
    
    // Age/milestone questions
    if (q.includes('age') || q.includes('old') || q.includes('milestone')) {
      if (age) {
        return `${babyRef} is ${age.months} months and ${age.days} days old!\n\nAt this age, typical milestones include:\n• Social smiles (6-8 weeks)\n• Holding head up (3-4 months)\n• Rolling over (4-6 months)\n• Sitting up (6-8 months)\n\nEvery baby develops at their own pace!`
      }
      return "Set your baby's birthdate in the Profile tab to get age-specific advice!"
    }
    
    // Tummy time
    if (q.includes('tummy') || q.includes('development') || q.includes('motor')) {
      return "Tummy time is crucial for motor development!\n\n• Start with 3-5 minutes, 2-3 times per day\n• Wait 30 minutes after feeding\n• Use toys to encourage head lifting\n• Gradually increase duration as baby gets stronger\n\nTummy time strengthens neck, back, and shoulder muscles."
    }
    
    // Crying/fussy
    if (q.includes('cry') || q.includes('fussy') || q.includes('calm') || q.includes('soothe')) {
      return "Babies cry to communicate! Common reasons:\n\n• Hungry (most common)\n• Tired or overstimulated\n• Needs diaper change\n• Too hot or cold\n• Wants to be held\n\nSoothing techniques:\n• Swaddling\n• White noise\n• Gentle rocking or bouncing\n• Pacifier\n• Skin-to-skin contact"
    }
    
    // Bath time
    if (q.includes('bath') || q.includes('wash') || q.includes('clean')) {
      return "Bath time tips:\n\n• Newborns need 2-3 baths per week\n• Use warm (not hot) water - test with elbow\n• Keep it short (5-10 minutes)\n• Never leave baby unattended\n• Bath before bedtime can help with sleep routine\n\nUse mild, fragrance-free baby soap."
    }
    
    // White noise
    if (q.includes('white noise') || q.includes('sound machine') || q.includes('noise machine')) {
      return "White noise is generally safe and beneficial for babies!\n\n✅ Benefits:\n• Mimics womb sounds\n• Blocks out household noise\n• Helps babies fall asleep faster\n• Can extend sleep duration\n\n⚠️ Safety tips:\n• Keep volume at 50 decibels or lower (about shower level)\n• Place machine at least 7 feet from crib\n• Don't play continuously all night - use for naps and initial sleep\n• Avoid sudden, jarring sounds\n\nMany pediatricians recommend white noise as a safe sleep aid!"
    }
    
    // Pacifier questions
    if (q.includes('pacifier') || q.includes('binky') || q.includes('soother')) {
      return "Pacifiers can be helpful!\n\n✅ Benefits:\n• May reduce SIDS risk\n• Satisfies sucking reflex\n• Can help soothe baby\n\n⚠️ Considerations:\n• Wait until breastfeeding is established (3-4 weeks)\n• Don't force it if baby refuses\n• Clean regularly\n• Wean by age 2-4 to prevent dental issues\n\nIt's okay if your baby doesn't want one - not all babies do!"
    }
    
    // Screen time
    if (q.includes('screen') || q.includes('tv') || q.includes('phone') || q.includes('ipad') || q.includes('video')) {
      return "Screen time recommendations by age:\n\n👶 Under 18 months: Avoid screens (except video calls)\n👶 18-24 months: Very limited, high-quality content only\n👶 2-5 years: Max 1 hour per day of quality programming\n\nWhy limit screens?\n• Babies learn best through interaction\n• Screens can interfere with sleep\n• May delay language development\n\nFocus on face-to-face interaction, reading, and play!"
    }
    
    // Teething
    if (q.includes('teeth') || q.includes('teething') || q.includes('gums')) {
      return "Teething typically starts around 6 months but varies!\n\n🦷 Signs of teething:\n• Drooling\n• Chewing on objects\n• Irritability\n• Swollen, tender gums\n• Mild temperature (not fever)\n\n💡 Relief methods:\n• Cold teething rings\n• Gentle gum massage\n• Cold washcloth to chew\n• Teething toys\n• Infant pain reliever (consult pediatrician)\n\nAvoid teething gels with benzocaine - they can be dangerous."
    }
    
    // Vaccines
    if (q.includes('vaccine') || q.includes('shot') || q.includes('immunization')) {
      return "Vaccines are crucial for protecting your baby!\n\n📅 Typical schedule:\n• Birth: Hepatitis B\n• 2 months: DTaP, Polio, Hib, PCV, Rotavirus\n• 4 months: Same as 2 months\n• 6 months: Same plus flu vaccine\n• 12 months: MMR, Varicella, Hepatitis A\n\n💉 After shots:\n• Mild fever and fussiness are normal\n• Give infant pain reliever if needed\n• Comfort and cuddle\n• Watch injection site for redness\n\nConsult your pediatrician about your specific schedule!"
    }
    
    // General help
    if (q.includes('help') || q.includes('what') || q.includes('can you')) {
      return `I can help you with:\n\n📊 ${babyRef}'s Data:\n• Feeding schedules and patterns\n• Sleep tracking and tips\n• Diaper change frequency\n• Daily summaries\n\n👶 Parenting Advice:\n• Age-appropriate milestones\n• Soothing techniques\n• Development activities\n• General baby care tips\n\nJust ask me anything!`
    }
    
    // Default response with suggestions
    return `I'm here to help with ${babyRef}'s care! I can answer questions about:\n\n📊 Baby's Data:\n• Feeding, sleep, and diaper patterns\n• Daily summaries and schedules\n\n👶 Parenting Topics:\n• Sleep training & white noise\n• Soothing techniques\n• Milestones & development\n• Tummy time\n• Teething\n• Pacifiers\n• Screen time\n• Vaccines\n• Bath time\n\nTry asking: "Is white noise safe?" or "How to soothe crying baby?"`
  }

  const handleSend = () => {
    if (!input.trim()) return
    
    const userMessage = { role: 'user', text: input }
    setMessages([...messages, userMessage])
    
    setTimeout(() => {
      const response = generateResponse(input)
      setMessages(prev => [...prev, { role: 'assistant', text: response }])
    }, 500)
    
    setInput('')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const content = (
    <>
      {!embedded && (
        <div className="modal-header">
          <h2>Assistant</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
      )}
      {embedded && (
        <div className="modal-header">
          <div className="header-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="#86EFAC" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              <circle cx="8" cy="10" r="1.5" fill="#86EFAC"/>
              <circle cx="12" cy="10" r="1.5" fill="#86EFAC"/>
              <circle cx="16" cy="10" r="1.5" fill="#86EFAC"/>
            </svg>
          </div>
          <h2>Chat Assistant</h2>
        </div>
      )}
        
        <div className="chat-messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={`chat-message ${msg.role}`}>
              <div className="message-bubble">
                {msg.text}
              </div>
            </div>
          ))}
        </div>

        <div className="chat-input-container">
          <input 
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about feeding, naps, patterns..."
            className="chat-input"
          />
          <button className="send-btn" onClick={handleSend}>
            Send
          </button>
        </div>
    </>
  )
  
  if (embedded) {
    return <div className="embedded-view chat-embedded">{content}</div>
  }
  
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="chat-modal" onClick={(e) => e.stopPropagation()}>
        {content}
      </div>
    </div>
  )
}

export default ChatAgent
