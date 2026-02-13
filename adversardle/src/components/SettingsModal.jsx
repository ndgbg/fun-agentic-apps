import { useTheme } from '../hooks/useTheme';

export default function SettingsModal({ isOpen, onClose, onNewGame, onFreePlay, gameStatus }) {
  const { settings, toggleDarkMode, toggleHighContrast, toggleHardMode } = useTheme();

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Settings</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body settings-body">
          <div className="setting-row">
            <div className="setting-info">
              <span className="setting-label">Hard Mode</span>
              <span className="setting-desc">Revealed hints must be used in subsequent guesses</span>
            </div>
            <button
              className={`toggle ${settings.hardMode ? 'toggle--on' : ''}`}
              onClick={toggleHardMode}
              aria-label="Toggle hard mode"
            >
              <div className="toggle-knob" />
            </button>
          </div>

          <div className="setting-row">
            <div className="setting-info">
              <span className="setting-label">Dark Theme</span>
            </div>
            <button
              className={`toggle ${settings.darkMode ? 'toggle--on' : ''}`}
              onClick={toggleDarkMode}
              aria-label="Toggle dark theme"
            >
              <div className="toggle-knob" />
            </button>
          </div>

          <div className="setting-row">
            <div className="setting-info">
              <span className="setting-label">High Contrast Mode</span>
              <span className="setting-desc">Improved color accessibility</span>
            </div>
            <button
              className={`toggle ${settings.highContrast ? 'toggle--on' : ''}`}
              onClick={toggleHighContrast}
              aria-label="Toggle high contrast"
            >
              <div className="toggle-knob" />
            </button>
          </div>

          <hr className="setting-divider" />

          <div className="setting-actions">
            <button className="action-btn" onClick={() => { onFreePlay(); onClose(); }}>
              New Free Play
            </button>
            {gameStatus === 'won' && (
              <button className="action-btn action-btn--secondary" onClick={() => { onNewGame(); onClose(); }}>
                Play Again
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
