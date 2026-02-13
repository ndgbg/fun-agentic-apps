import { useMemo } from 'react';
import { loadStats } from '../utils/storage';
import { generateShareText, copyToClipboard } from '../utils/sharing';
import { useTheme } from '../hooks/useTheme';

export default function StatsModal({ isOpen, onClose, guesses, patterns, gameStatus, gameMode, dayNumber }) {
  const { settings } = useTheme();
  const stats = useMemo(() => isOpen ? loadStats() : null, [isOpen]);

  if (!isOpen || !stats) return null;

  const winPct = stats.gamesPlayed > 0
    ? Math.round((stats.gamesWon / stats.gamesPlayed) * 100)
    : 0;

  // Build distribution data
  const distEntries = Object.entries(stats.guessDistribution)
    .map(([k, v]) => [Number(k), v])
    .sort((a, b) => a[0] - b[0]);
  const maxDist = Math.max(1, ...distEntries.map(([, v]) => v));

  const canShare = gameStatus === 'won';

  const handleShare = async () => {
    const text = generateShareText(guesses, patterns, gameMode === 'daily', settings);
    const copied = await copyToClipboard(text);
    if (copied) {
      // Brief feedback — the toast in App handles this
      alert('Copied to clipboard!');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Statistics</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">
          <div className="stats-grid">
            <div className="stat">
              <div className="stat-value">{stats.gamesPlayed}</div>
              <div className="stat-label">Played</div>
            </div>
            <div className="stat">
              <div className="stat-value">{winPct}</div>
              <div className="stat-label">Win %</div>
            </div>
            <div className="stat">
              <div className="stat-value">{stats.currentStreak}</div>
              <div className="stat-label">Current Streak</div>
            </div>
            <div className="stat">
              <div className="stat-value">{stats.maxStreak}</div>
              <div className="stat-label">Max Streak</div>
            </div>
          </div>

          {distEntries.length > 0 && (
            <>
              <h3>Guess Distribution</h3>
              <div className="distribution">
                {distEntries.map(([numGuesses, count]) => (
                  <div key={numGuesses} className="dist-row">
                    <span className="dist-label">{numGuesses}</span>
                    <div className="dist-bar-container">
                      <div
                        className="dist-bar"
                        style={{ width: `${Math.max(8, (count / maxDist) * 100)}%` }}
                      >
                        {count}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {canShare && (
            <button className="share-btn" onClick={handleShare}>
              Share Result
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: 6 }}>
                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
                <polyline points="16 6 12 2 8 6"/>
                <line x1="12" y1="2" x2="12" y2="15"/>
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
