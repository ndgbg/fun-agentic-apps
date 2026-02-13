import { SOLUTIONS } from '../data/solutions';
import { VALID_GUESSES } from '../data/validGuesses';

/** Set of all valid 5-letter words (solutions + additional guesses). */
const validSet = new Set([...SOLUTIONS, ...VALID_GUESSES]);

/** Check if a word is a valid 5-letter guess. */
export function isValidGuess(word) {
  return validSet.has(word.toLowerCase());
}

/** Check if hard mode constraints are satisfied. */
export function checkHardMode(guess, previousGuesses, previousPatterns) {
  for (let i = 0; i < previousGuesses.length; i++) {
    const prevGuess = previousGuesses[i];
    const prevPattern = previousPatterns[i];

    for (let j = 0; j < 5; j++) {
      const letter = prevGuess[j];

      if (prevPattern[j] === 2) {
        // Green: must use same letter in same position
        if (guess[j] !== letter) {
          return { valid: false, message: `${j + 1}${ordinalSuffix(j + 1)} letter must be '${letter.toUpperCase()}'` };
        }
      } else if (prevPattern[j] === 1) {
        // Yellow: must use letter somewhere (but not same position)
        if (!guess.includes(letter)) {
          return { valid: false, message: `Guess must contain '${letter.toUpperCase()}'` };
        }
      }
    }
  }

  return { valid: true };
}

function ordinalSuffix(n) {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return s[(v - 20) % 10] || s[v] || s[0];
}

/** Build keyboard letter status map from all guesses and patterns. */
export function buildKeyboardStatus(guesses, patterns) {
  const status = {};

  for (let i = 0; i < guesses.length; i++) {
    const guess = guesses[i];
    const pattern = patterns[i];

    for (let j = 0; j < 5; j++) {
      const letter = guess[j];
      const current = status[letter] || 'unused';
      const result = pattern[j] === 2 ? 'correct' : pattern[j] === 1 ? 'present' : 'absent';

      // Priority: correct > present > absent > unused
      if (result === 'correct') {
        status[letter] = 'correct';
      } else if (result === 'present' && current !== 'correct') {
        status[letter] = 'present';
      } else if (result === 'absent' && current === 'unused') {
        status[letter] = 'absent';
      }
    }
  }

  return status;
}
