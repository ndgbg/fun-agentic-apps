/**
 * AdversarialAgent — the core AI that fights back against the player.
 *
 * Unlike regular Wordle where a word is pre-selected, this agent watches
 * every guess and strategically picks the color pattern that leaves the
 * MOST remaining candidates — maximizing difficulty while staying provably fair.
 *
 * The game ends when the player "corners" the AI into exactly one possible word.
 */

/**
 * Compute the color pattern for a guess against a specific target word.
 * Returns a 5-element array: 2 = green, 1 = yellow, 0 = gray.
 *
 * Two-pass algorithm handles duplicate letters correctly:
 *   Pass 1: Mark exact matches (green)
 *   Pass 2: Mark present-but-wrong-position (yellow), respecting letter counts
 */
export function computePattern(guess, target) {
  const pattern = [0, 0, 0, 0, 0];
  const targetCounts = {};
  const guessArr = guess.split('');
  const targetArr = target.split('');

  // Pass 1: Greens
  for (let i = 0; i < 5; i++) {
    if (guessArr[i] === targetArr[i]) {
      pattern[i] = 2;
    } else {
      targetCounts[targetArr[i]] = (targetCounts[targetArr[i]] || 0) + 1;
    }
  }

  // Pass 2: Yellows
  for (let i = 0; i < 5; i++) {
    if (pattern[i] === 0 && targetCounts[guessArr[i]] > 0) {
      pattern[i] = 1;
      targetCounts[guessArr[i]]--;
    }
  }

  return pattern;
}

/**
 * Encode a 5-element pattern array into a single integer (base-3, 0–242).
 * This allows using patterns as Map keys efficiently.
 */
export function patternToKey(pattern) {
  return pattern[0] * 81 + pattern[1] * 27 + pattern[2] * 9 + pattern[3] * 3 + pattern[4];
}

/**
 * Decode a pattern key back into a 5-element array.
 */
export function keyToPattern(key) {
  const pattern = [];
  let k = key;
  for (let i = 0; i < 5; i++) {
    const pow = Math.pow(3, 4 - i);
    pattern.push(Math.floor(k / pow));
    k = k % pow;
  }
  return pattern;
}

/**
 * The Adversarial Agent.
 *
 * Maintains a candidate pool and, for each guess, picks the response pattern
 * that maximizes the remaining candidate count — i.e., the hardest possible
 * fair response.
 */
export class AdversarialAgent {
  constructor(wordList) {
    this.initialWords = [...wordList];
    this.candidates = [...wordList];
  }

  /** Number of words the AI could still be hiding behind. */
  get candidateCount() {
    return this.candidates.length;
  }

  /** Reset to full candidate pool (for new game). */
  reset() {
    this.candidates = [...this.initialWords];
  }

  /**
   * Process a guess. Partitions candidates by pattern, picks the partition
   * with the most candidates (adversarial strategy), filters candidates,
   * and returns the chosen pattern.
   *
   * If only one candidate remains and the guess matches it, returns all greens.
   *
   * @param {string} guess - The 5-letter guess word
   * @returns {{ pattern: number[], candidates: number, revealedWord: string|null }}
   */
  processGuess(guess) {
    // Partition candidates by the pattern they'd produce
    const partitions = new Map();

    for (const word of this.candidates) {
      const pattern = computePattern(guess, word);
      const key = patternToKey(pattern);

      if (!partitions.has(key)) {
        partitions.set(key, []);
      }
      partitions.get(key).push(word);
    }

    // Pick the partition with the most candidates (adversarial!)
    let bestKey = -1;
    let bestSize = -1;
    let bestWords = [];

    for (const [key, words] of partitions) {
      if (words.length > bestSize) {
        bestSize = words.length;
        bestKey = key;
        bestWords = words;
      }
    }

    // Update candidates to the chosen partition
    this.candidates = bestWords;

    const pattern = keyToPattern(bestKey);
    const isWin = pattern.every(c => c === 2);
    const revealedWord = isWin ? guess : null;

    return {
      pattern,
      candidates: this.candidates.length,
      revealedWord,
    };
  }

  /**
   * Process a guess deterministically using a seed (for daily challenge).
   * When multiple partitions tie for largest size, uses the seed to break ties
   * consistently so all players get the same experience.
   *
   * @param {string} guess - The 5-letter guess word
   * @param {number} seed - Numeric seed for tie-breaking
   * @returns {{ pattern: number[], candidates: number, revealedWord: string|null }}
   */
  processGuessDeterministic(guess, seed) {
    const partitions = new Map();

    for (const word of this.candidates) {
      const pattern = computePattern(guess, word);
      const key = patternToKey(pattern);

      if (!partitions.has(key)) {
        partitions.set(key, []);
      }
      partitions.get(key).push(word);
    }

    // Find max size
    let maxSize = 0;
    for (const words of partitions.values()) {
      if (words.length > maxSize) maxSize = words.length;
    }

    // Collect all partitions with max size (ties)
    const tiedKeys = [];
    for (const [key, words] of partitions) {
      if (words.length === maxSize) {
        tiedKeys.push(key);
      }
    }

    // Break ties deterministically using seed
    tiedKeys.sort((a, b) => a - b);
    const chosenKey = tiedKeys[seed % tiedKeys.length];

    this.candidates = partitions.get(chosenKey);

    const pattern = keyToPattern(chosenKey);
    const isWin = pattern.every(c => c === 2);

    return {
      pattern,
      candidates: this.candidates.length,
      revealedWord: isWin ? guess : null,
    };
  }
}
