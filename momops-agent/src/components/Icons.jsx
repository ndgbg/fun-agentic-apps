// Custom SVG icons for MomOps with pastel theme

export const HomeIcon = ({ active }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path 
      d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" 
      stroke={active ? "#A78BFA" : "#94A3B8"}
      strokeWidth="2.5" 
      strokeLinecap="round" 
      strokeLinejoin="round"
      fill={active ? "#A78BFA" : "none"}
      fillOpacity={active ? "0.2" : "0"}
    />
    <path 
      d="M9 22V12H15V22" 
      stroke={active ? "#A78BFA" : "#94A3B8"}
      strokeWidth="2.5" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
  </svg>
)

export const CalendarIcon = ({ active }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect 
      x="3" 
      y="4" 
      width="18" 
      height="18" 
      rx="2" 
      stroke={active ? "#F9A8D4" : "#94A3B8"}
      strokeWidth="2.5" 
      strokeLinecap="round" 
      strokeLinejoin="round"
      fill={active ? "#F9A8D4" : "none"}
      fillOpacity={active ? "0.2" : "0"}
    />
    <path 
      d="M16 2V6M8 2V6M3 10H21" 
      stroke={active ? "#F9A8D4" : "#94A3B8"}
      strokeWidth="2.5" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
    <circle cx="8" cy="14" r="1.5" fill={active ? "#F9A8D4" : "#94A3B8"} />
    <circle cx="12" cy="14" r="1.5" fill={active ? "#F9A8D4" : "#94A3B8"} />
    <circle cx="16" cy="14" r="1.5" fill={active ? "#F9A8D4" : "#94A3B8"} />
  </svg>
)

export const ChartIcon = ({ active }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path 
      d="M3 3V21H21" 
      stroke={active ? "#93C5FD" : "#94A3B8"}
      strokeWidth="2.5" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
    <path 
      d="M7 16L12 11L16 15L21 8" 
      stroke={active ? "#93C5FD" : "#94A3B8"}
      strokeWidth="2.5" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
    <circle 
      cx="21" 
      cy="8" 
      r="2" 
      fill={active ? "#93C5FD" : "#94A3B8"}
    />
    <circle 
      cx="16" 
      cy="15" 
      r="2" 
      fill={active ? "#93C5FD" : "#94A3B8"}
    />
    <circle 
      cx="12" 
      cy="11" 
      r="2" 
      fill={active ? "#93C5FD" : "#94A3B8"}
    />
    <circle 
      cx="7" 
      cy="16" 
      r="2" 
      fill={active ? "#93C5FD" : "#94A3B8"}
    />
  </svg>
)

export const ScheduleIcon = ({ active }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle 
      cx="9" 
      cy="7" 
      r="3" 
      stroke={active ? "#FCD34D" : "#94A3B8"}
      strokeWidth="2.5"
      fill={active ? "#FCD34D" : "none"}
      fillOpacity={active ? "0.3" : "0"}
    />
    <path 
      d="M3 21C3 17.686 5.686 15 9 15C12.314 15 15 17.686 15 21" 
      stroke={active ? "#FCD34D" : "#94A3B8"}
      strokeWidth="2.5" 
      strokeLinecap="round"
    />
    <circle 
      cx="17" 
      cy="7" 
      r="2.5" 
      stroke={active ? "#FCD34D" : "#94A3B8"}
      strokeWidth="2.5"
      fill={active ? "#FCD34D" : "none"}
      fillOpacity={active ? "0.3" : "0"}
    />
    <path 
      d="M16 15C18.5 15 21 16.5 21 19.5" 
      stroke={active ? "#FCD34D" : "#94A3B8"}
      strokeWidth="2.5" 
      strokeLinecap="round"
    />
  </svg>
)

export const ChatIcon = ({ active }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path 
      d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" 
      stroke={active ? "#86EFAC" : "#94A3B8"}
      strokeWidth="2.5" 
      strokeLinecap="round" 
      strokeLinejoin="round"
      fill={active ? "#86EFAC" : "none"}
      fillOpacity={active ? "0.2" : "0"}
    />
    <circle cx="8" cy="10" r="1.5" fill={active ? "#86EFAC" : "#94A3B8"} />
    <circle cx="12" cy="10" r="1.5" fill={active ? "#86EFAC" : "#94A3B8"} />
    <circle cx="16" cy="10" r="1.5" fill={active ? "#86EFAC" : "#94A3B8"} />
  </svg>
)

export const LogoIcon = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="16" cy="16" r="14" fill="url(#gradient)" />
    <path 
      d="M16 8C13 8 11 10 11 13C11 16 13 18 16 18C19 18 21 16 21 13C21 10 19 8 16 8Z" 
      fill="white" 
      opacity="0.9"
    />
    <circle cx="16" cy="22" r="2" fill="white" opacity="0.9" />
    <defs>
      <linearGradient id="gradient" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
        <stop stopColor="#A78BFA" />
        <stop offset="1" stopColor="#F9A8D4" />
      </linearGradient>
    </defs>
  </svg>
)


export function ProfileIcon({ active }) {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle 
        cx="12" 
        cy="8" 
        r="4" 
        stroke={active ? '#1E293B' : '#94A3B8'} 
        strokeWidth="2.5"
        fill={active ? '#F9A8D4' : 'none'}
      />
      <path 
        d="M6 21C6 17.134 8.686 14 12 14C15.314 14 18 17.134 18 21" 
        stroke={active ? '#1E293B' : '#94A3B8'} 
        strokeWidth="2.5" 
        strokeLinecap="round"
      />
    </svg>
  )
}


export function AgentIcon({ active }) {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle 
        cx="12" 
        cy="12" 
        r="3" 
        stroke={active ? '#86EFAC' : '#94A3B8'} 
        strokeWidth="2.5"
        fill={active ? '#86EFAC' : 'none'}
        fillOpacity={active ? '0.3' : '0'}
      />
      <path 
        d="M12 2V6M12 18V22M22 12H18M6 12H2" 
        stroke={active ? '#86EFAC' : '#94A3B8'} 
        strokeWidth="2.5" 
        strokeLinecap="round"
      />
      <path 
        d="M17.5 6.5L15 9M9 15L6.5 17.5M17.5 17.5L15 15M9 9L6.5 6.5" 
        stroke={active ? '#86EFAC' : '#94A3B8'} 
        strokeWidth="2.5" 
        strokeLinecap="round"
      />
    </svg>
  )
}
