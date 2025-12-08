// Sample data for testing MomOps
export const generateSampleData = () => {
  const now = new Date()
  const activities = []
  
  // Helper to create timestamps going back in time
  const hoursAgo = (hours) => {
    const date = new Date(now)
    date.setHours(date.getHours() - hours)
    return date.toISOString()
  }
  
  const daysAgo = (days, hours = 0, minutes = 0) => {
    const date = new Date(now)
    date.setDate(date.getDate() - days)
    date.setHours(date.getHours() - hours)
    date.setMinutes(date.getMinutes() - minutes)
    return date.toISOString()
  }
  
  // Create timestamp at specific time of day X days ago
  const atTimeOnDay = (days, hour, minute = 0) => {
    const date = new Date(now)
    date.setDate(date.getDate() - days)
    date.setHours(hour, minute, 0, 0)
    return date.toISOString()
  }
  
  // Generate realistic feeding pattern (every 2-3 hours)
  const generateFeedings = (startDay, endDay) => {
    const feedings = []
    let id = Date.now() + Math.random() * 100000
    
    for (let day = startDay; day <= endDay; day++) {
      // 6-8 feedings per day at realistic times (7am-11pm)
      const feedTimes = [7, 10, 13, 16, 19, 21, 23, 1] // hours of day (including late night)
      const numFeeds = 6 + Math.floor(Math.random() * 3)
      
      for (let i = 0; i < numFeeds; i++) {
        const hour = feedTimes[i % feedTimes.length] // Use modulo to prevent out of bounds
        const minute = Math.floor(Math.random() * 30)
        const feedType = Math.random() > 0.6 ? 'breast' : 'bottle'
        const feeding = {
          id: id++,
          type: 'feed',
          feedType,
          timestamp: atTimeOnDay(day, hour, minute)
        }
        
        if (feedType === 'breast') {
          feeding.side = ['left', 'right', 'both'][Math.floor(Math.random() * 3)]
          if (Math.random() > 0.7) {
            feeding.notes = ['Good latch', 'Fussy at first', 'Fell asleep while feeding', 'Very hungry'][Math.floor(Math.random() * 4)]
          }
        } else {
          feeding.amount = 3 + Math.floor(Math.random() * 3) + (Math.random() > 0.5 ? 0.5 : 0)
          if (Math.random() > 0.8) {
            feeding.notes = ['Formula', 'Breast milk bottle', 'Finished entire bottle', 'Left 1oz'][Math.floor(Math.random() * 4)]
          }
        }
        
        feedings.push(feeding)
      }
    }
    return feedings
  }
  
  // Generate realistic nap pattern (3-4 naps per day)
  const generateNaps = (startDay, endDay) => {
    const naps = []
    let id = Date.now() + Math.random() * 100000
    
    for (let day = startDay; day <= endDay; day++) {
      // Realistic nap times: morning, midday, afternoon, early evening
      const napTimes = [
        { start: 9, duration: 30 + Math.floor(Math.random() * 60) },   // Morning nap
        { start: 13, duration: 60 + Math.floor(Math.random() * 90) },  // Afternoon nap (longest)
        { start: 16, duration: 30 + Math.floor(Math.random() * 45) },  // Late afternoon
        { start: 19, duration: 20 + Math.floor(Math.random() * 40) }   // Early evening catnap
      ]
      
      const numNaps = 3 + Math.floor(Math.random() * 2)
      
      for (let i = 0; i < numNaps; i++) {
        const napTime = napTimes[i % napTimes.length] // Use modulo to prevent out of bounds
        const minute = Math.floor(Math.random() * 30)
        const startTime = atTimeOnDay(day, napTime.start, minute)
        const endDate = new Date(startTime)
        endDate.setMinutes(endDate.getMinutes() + napTime.duration)
        
        naps.push({
          id: id++,
          type: 'nap',
          duration: napTime.duration,
          startTime,
          endTime: endDate.toISOString(),
          timestamp: startTime,
          notes: Math.random() > 0.7 ? ['Slept well', 'Woke up crying', 'Peaceful nap', 'Needed rocking'][Math.floor(Math.random() * 4)] : undefined
        })
      }
    }
    return naps
  }
  
  // Generate realistic diaper changes (8-12 per day)
  const generateDiapers = (startDay, endDay) => {
    const diapers = []
    let id = Date.now() + Math.random() * 100000
    
    for (let day = startDay; day <= endDay; day++) {
      const numDiapers = 8 + Math.floor(Math.random() * 5)
      
      for (let i = 0; i < numDiapers; i++) {
        // Spread throughout waking hours (6am-11pm)
        const hour = 6 + Math.floor(Math.random() * 17)
        const minute = Math.floor(Math.random() * 60)
        const types = ['pee', 'pee', 'pee', 'poop', 'both'] // More pee than poop
        
        diapers.push({
          id: id++,
          type: 'diaper',
          diaperType: types[Math.floor(Math.random() * types.length)],
          timestamp: atTimeOnDay(day, hour, minute),
          notes: Math.random() > 0.9 ? ['Diaper rash', 'Applied cream', 'Very wet', 'Blowout!'][Math.floor(Math.random() * 4)] : undefined
        })
      }
    }
    return diapers
  }
  
  // Generate medications and vitamins
  const generateMedications = (startDay, endDay) => {
    const meds = []
    let id = Date.now() + Math.random() * 100000
    
    for (let day = startDay; day <= endDay; day++) {
      // Daily vitamin D (usually given in morning)
      meds.push({
        id: id++,
        type: 'medication',
        medicationName: 'Vitamin D',
        dosage: '400 IU (1 drop)',
        timestamp: atTimeOnDay(day, 9, Math.floor(Math.random() * 60)),
        notes: 'Daily supplement'
      })
      
      // Occasional medications
      if (Math.random() > 0.85) {
        const hour = 8 + Math.floor(Math.random() * 14) // Between 8am-10pm
        meds.push({
          id: id++,
          type: 'medication',
          medicationName: ['Tylenol', 'Gas drops', 'Gripe water'][Math.floor(Math.random() * 3)],
          dosage: ['2.5ml', '0.5ml', '5ml'][Math.floor(Math.random() * 3)],
          timestamp: atTimeOnDay(day, hour, Math.floor(Math.random() * 60)),
          notes: ['For teething', 'Fussy/gassy', 'Before bed', 'After feeding'][Math.floor(Math.random() * 4)]
        })
      }
    }
    return meds
  }
  
  // Generate other activities
  const generateOtherActivities = (startDay, endDay) => {
    const activities = []
    let id = Date.now() + Math.random() * 100000
    
    for (let day = startDay; day <= endDay; day++) {
      // Daily bath (evening between 6-8pm)
      if (Math.random() > 0.3) {
        const bathHour = 18 + Math.floor(Math.random() * 2)
        activities.push({
          id: id++,
          type: 'other',
          activityType: 'bath',
          timestamp: atTimeOnDay(day, bathHour, Math.floor(Math.random() * 60)),
          notes: ['Evening bath', 'Loved splashing', 'Quick bath', 'Bath with lavender'][Math.floor(Math.random() * 4)]
        })
      }
      
      // Tummy time (2-3 times per day during waking hours)
      const tummyTimes = 2 + Math.floor(Math.random() * 2)
      for (let i = 0; i < tummyTimes; i++) {
        const tummyHour = 10 + i * 4 // 10am, 2pm, 6pm
        activities.push({
          id: id++,
          type: 'other',
          activityType: 'tummytime',
          timestamp: atTimeOnDay(day, tummyHour, Math.floor(Math.random() * 60)),
          notes: [`${5 + Math.floor(Math.random() * 10)} minutes`, 'Did great!', 'Got frustrated', 'Lifted head'][Math.floor(Math.random() * 4)]
        })
      }
      
      // Occasional activities during daytime
      if (Math.random() > 0.7) {
        const activityTypes = ['playtime', 'walk', 'reading', 'milestone']
        const activityType = activityTypes[Math.floor(Math.random() * activityTypes.length)]
        const notes = {
          playtime: ['Played with rattle', 'Enjoyed mobile', 'Sensory play', 'Floor time'],
          walk: ['Stroller walk', 'Fresh air', '30 min walk', 'Park visit'],
          reading: ['Read 3 books', 'Storytime', 'Loved the pictures', 'Fell asleep during story'],
          milestone: ['Smiled at me!', 'Held head up', 'Tracked toy', 'Cooed and babbled', 'Rolled over!']
        }
        
        const activityHour = 9 + Math.floor(Math.random() * 10) // Between 9am-7pm
        activities.push({
          id: id++,
          type: 'other',
          activityType,
          timestamp: atTimeOnDay(day, activityHour, Math.floor(Math.random() * 60)),
          notes: notes[activityType][Math.floor(Math.random() * notes[activityType].length)]
        })
      }
      
      // Weekly weight check (usually at pediatrician around 2pm)
      if (day % 7 === 0) {
        const baseWeight = 10 + (endDay - day) * 0.15 // Growing baby
        activities.push({
          id: id++,
          type: 'other',
          activityType: 'weight',
          timestamp: atTimeOnDay(day, 14, Math.floor(Math.random() * 30)),
          notes: `${Math.floor(baseWeight)} lbs ${Math.floor((baseWeight % 1) * 16)} oz`
        })
      }
    }
    return activities
  }
  
  // Generate 30 days of rich historical data
  const daysOfHistory = 30
  
  activities.push(...generateFeedings(0, daysOfHistory))
  activities.push(...generateNaps(0, daysOfHistory))
  activities.push(...generateDiapers(0, daysOfHistory))
  activities.push(...generateMedications(0, daysOfHistory))
  activities.push(...generateOtherActivities(0, daysOfHistory))
  
  return activities.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
}

export const generateSampleSchedules = () => {
  return [
    {
      id: 1,
      type: 'nanny',
      title: 'Morning Nanny',
      person: 'Sarah Johnson',
      days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
      startTime: '08:00',
      endTime: '13:00',
      hourlyRate: '22',
      notes: 'CPR certified. Prefers organic snacks. Excellent with newborns. Contact: (555) 123-4567'
    },
    {
      id: 2,
      type: 'nanny',
      title: 'Evening Care',
      person: 'Maria Garcia',
      days: ['Monday', 'Wednesday', 'Friday'],
      startTime: '17:00',
      endTime: '20:00',
      hourlyRate: '20',
      notes: 'Great with bedtime routines. Bilingual (English/Spanish). 10 years experience.'
    },
    {
      id: 3,
      type: 'nanny',
      title: 'Weekend Helper',
      person: 'Emily Chen',
      days: ['Saturday', 'Sunday'],
      startTime: '10:00',
      endTime: '16:00',
      hourlyRate: '25',
      notes: 'Early childhood education degree. Loves outdoor activities. Very creative.'
    },
    {
      id: 4,
      type: 'work',
      title: 'Work Schedule',
      person: 'Mom',
      days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
      startTime: '09:00',
      endTime: '17:00',
      notes: 'Remote on Wednesdays. Flexible lunch break for pumping.'
    },
    {
      id: 5,
      type: 'work',
      title: 'Work Schedule',
      person: 'Dad',
      days: ['Monday', 'Tuesday', 'Thursday', 'Friday'],
      startTime: '08:30',
      endTime: '17:30',
      notes: 'Off on Wednesdays. Can help with morning routine.'
    },
    {
      id: 6,
      type: 'activity',
      title: 'Baby Music Class',
      days: ['Tuesday', 'Thursday'],
      startTime: '10:00',
      endTime: '10:45',
      notes: 'Bring favorite toy. $20 per class. At Community Center.'
    },
    {
      id: 7,
      type: 'activity',
      title: 'Mommy & Me Yoga',
      days: ['Monday', 'Wednesday'],
      startTime: '11:00',
      endTime: '12:00',
      notes: 'Bring yoga mat and water. Great for bonding!'
    },
    {
      id: 8,
      type: 'activity',
      title: 'Pediatrician Checkup',
      days: ['Friday'],
      startTime: '14:00',
      endTime: '15:00',
      notes: 'Monthly wellness visit. Dr. Anderson. Bring insurance card.'
    },
    {
      id: 9,
      type: 'activity',
      title: 'Library Story Time',
      days: ['Saturday'],
      startTime: '10:30',
      endTime: '11:15',
      notes: 'Free event. Great for socialization. Arrive early for good spot.'
    },
    {
      id: 10,
      type: 'activity',
      title: 'Swimming Lessons',
      days: ['Saturday'],
      startTime: '15:00',
      endTime: '15:30',
      notes: 'Infant swim class. Bring swim diaper and towel. $30 per session.'
    }
  ]
}
