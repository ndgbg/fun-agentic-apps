// Enhanced activity icons with better visuals

export const FeedIcon = ({ type }) => {
  if (type === 'breast') {
    return (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="10" r="6" stroke="white" strokeWidth="2" fill="none"/>
        <circle cx="12" cy="10" r="2" fill="white"/>
        <path d="M12 16V20" stroke="white" strokeWidth="2" strokeLinecap="round"/>
      </svg>
    )
  }
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M6 8L6 18C6 19 7 20 8 20L16 20C17 20 18 19 18 18L18 8" stroke="white" strokeWidth="2" strokeLinecap="round"/>
      <path d="M4 8L20 8" stroke="white" strokeWidth="2" strokeLinecap="round"/>
      <path d="M12 4L12 8" stroke="white" strokeWidth="2" strokeLinecap="round"/>
      <circle cx="12" cy="3" r="1.5" fill="white"/>
    </svg>
  )
}

export const NapIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M3 12L5 10L7 12L9 10L11 12L13 10L15 12L17 10L19 12L21 10" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M3 18L21 18" stroke="white" strokeWidth="2" strokeLinecap="round"/>
    <circle cx="8" cy="8" r="1" fill="white"/>
    <circle cx="12" cy="6" r="1" fill="white"/>
    <circle cx="16" cy="8" r="1" fill="white"/>
  </svg>
)

export const DiaperIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4 8C4 6 5 4 7 4H17C19 4 20 6 20 8V16C20 18 19 20 17 20H7C5 20 4 18 4 16V8Z" stroke="white" strokeWidth="2" strokeLinecap="round"/>
    <path d="M8 12H16" stroke="white" strokeWidth="2" strokeLinecap="round"/>
    <circle cx="12" cy="12" r="2" stroke="white" strokeWidth="2"/>
  </svg>
)

export const MedicationIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="6" y="8" width="12" height="12" rx="2" stroke="white" strokeWidth="2"/>
    <path d="M12 11V17M9 14H15" stroke="white" strokeWidth="2" strokeLinecap="round"/>
    <path d="M9 4L9 8M15 4L15 8" stroke="white" strokeWidth="2" strokeLinecap="round"/>
  </svg>
)

export const OtherIcon = ({ type }) => {
  if (type === 'bath') {
    return (
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4 12H20V18C20 19 19 20 18 20H6C5 20 4 19 4 18V12Z" stroke="white" strokeWidth="2"/>
        <path d="M4 12V10C4 9 5 8 6 8H7" stroke="white" strokeWidth="2" strokeLinecap="round"/>
        <circle cx="8" cy="15" r="1" fill="white"/>
        <circle cx="12" cy="16" r="1" fill="white"/>
        <circle cx="16" cy="15" r="1" fill="white"/>
      </svg>
    )
  }
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="8" stroke="white" strokeWidth="2"/>
      <path d="M12 8V12L15 15" stroke="white" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  )
}
