/**
 * Daily challenge seed generation.
 * Everyone gets the same game on the same day.
 */

// Epoch: Jan 1, 2024
const EPOCH = new Date(2024, 0, 1).getTime();
const MS_PER_DAY = 86400000;

/** Get the day number since epoch. */
export function getDayNumber(date = new Date()) {
  const now = new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
  return Math.floor((now - EPOCH) / MS_PER_DAY);
}

/**
 * Simple seeded PRNG (mulberry32).
 * Returns a function that produces deterministic floats in [0, 1).
 */
export function seededRandom(seed) {
  let t = seed + 0x6D2B79F5;
  return function () {
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * Get a numeric seed for a given day number.
 * Used for deterministic tie-breaking in the adversarial agent.
 */
export function getDailySeed(dayNumber) {
  // Mix the day number into a decent seed
  let h = dayNumber * 2654435761;
  h = ((h >>> 16) ^ h) * 0x45d9f3b;
  h = ((h >>> 16) ^ h) * 0x45d9f3b;
  h = (h >>> 16) ^ h;
  return h >>> 0;
}
