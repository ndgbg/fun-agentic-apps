const STATS_KEY = 'adversardle-stats';
const SETTINGS_KEY = 'adversardle-settings';
const DAILY_STATE_KEY = 'adversardle-daily';

const DEFAULT_STATS = {
  gamesPlayed: 0,
  gamesWon: 0,
  currentStreak: 0,
  maxStreak: 0,
  guessDistribution: {},
};

const DEFAULT_SETTINGS = {
  hardMode: false,
  darkMode: window.matchMedia('(prefers-color-scheme: dark)').matches,
  highContrast: false,
};

function safeGet(key, fallback) {
  try {
    const stored = localStorage.getItem(key);
    return stored ? JSON.parse(stored) : fallback;
  } catch {
    return fallback;
  }
}

function safeSet(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // localStorage full or unavailable — silently ignore
  }
}

export function loadStats() {
  return { ...DEFAULT_STATS, ...safeGet(STATS_KEY, DEFAULT_STATS) };
}

export function saveStats(stats) {
  safeSet(STATS_KEY, stats);
}

export function updateStatsAfterGame(won, numGuesses) {
  const stats = loadStats();
  stats.gamesPlayed++;

  if (won) {
    stats.gamesWon++;
    stats.currentStreak++;
    stats.maxStreak = Math.max(stats.maxStreak, stats.currentStreak);
    const key = String(numGuesses);
    stats.guessDistribution[key] = (stats.guessDistribution[key] || 0) + 1;
  } else {
    stats.currentStreak = 0;
  }

  saveStats(stats);
  return stats;
}

export function loadSettings() {
  return { ...DEFAULT_SETTINGS, ...safeGet(SETTINGS_KEY, DEFAULT_SETTINGS) };
}

export function saveSettings(settings) {
  safeSet(SETTINGS_KEY, settings);
}

export function loadDailyState(dayNumber) {
  const state = safeGet(DAILY_STATE_KEY, null);
  if (state && state.dayNumber === dayNumber) {
    return state;
  }
  return null;
}

export function saveDailyState(state) {
  safeSet(DAILY_STATE_KEY, state);
}

export function clearDailyState() {
  try {
    localStorage.removeItem(DAILY_STATE_KEY);
  } catch {
    // ignore
  }
}
