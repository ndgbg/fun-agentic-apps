import { getDayNumber } from './dailySeed';

const EMOJI_MAP = {
  0: { normal: '\u2B1C', dark: '\u2B1B', highContrast: '\u2B1C' },  // gray
  1: { normal: '\uD83D\uDFE8', dark: '\uD83D\uDFE8', highContrast: '\uD83D\uDFE6' },  // yellow / blue
  2: { normal: '\uD83D\uDFE9', dark: '\uD83D\uDFE9', highContrast: '\uD83D\uDFE7' },  // green / orange
};

/**
 * Generate a shareable emoji grid from game results.
 */
export function generateShareText(guesses, patterns, isDaily, settings = {}) {
  const { darkMode = false, highContrast = false } = settings;
  const theme = highContrast ? 'highContrast' : darkMode ? 'dark' : 'normal';

  const dayNum = isDaily ? getDayNumber() : null;
  const title = isDaily
    ? `Adversardle #${dayNum}`
    : 'Adversardle (Free Play)';

  const subtitle = `Cornered the AI in ${guesses.length} guess${guesses.length === 1 ? '' : 'es'}!`;

  const grid = patterns
    .map(pattern => pattern.map(c => EMOJI_MAP[c][theme]).join(''))
    .join('\n');

  return `${title}\n${subtitle}\n\n${grid}`;
}

/**
 * Copy text to clipboard, with fallback.
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // Fallback for older browsers
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      return true;
    } catch {
      return false;
    } finally {
      document.body.removeChild(textarea);
    }
  }
}
