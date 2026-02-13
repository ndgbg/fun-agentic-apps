import { useState } from 'react';
import { useGame } from './hooks/useGame';
import { useTheme } from './hooks/useTheme';
import Header from './components/Header';
import Board from './components/Board';
import Keyboard from './components/Keyboard';
import CandidateCounter from './components/CandidateCounter';
import Toast from './components/Toast';
import HelpModal from './components/HelpModal';
import StatsModal from './components/StatsModal';
import SettingsModal from './components/SettingsModal';
import './App.css';

export default function App() {
  const { settings } = useTheme();

  const {
    gameMode,
    guesses,
    patterns,
    currentGuess,
    gameStatus,
    candidateCount,
    revealedWord,
    keyboardStatus,
    shakeRow,
    toastMessage,
    isRevealing,
    dayNumber,
    onKeyPress,
    startFreePlay,
    newGame,
    totalWords,
  } = useGame(settings.hardMode);

  const [helpOpen, setHelpOpen] = useState(() => {
    return !localStorage.getItem('adversardle-seen-help');
  });
  const [statsOpen, setStatsOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  return (
    <div className="app">
      <Header
        onHelp={() => setHelpOpen(true)}
        onStats={() => setStatsOpen(true)}
        onSettings={() => setSettingsOpen(true)}
      />

      <div className="game-mode-indicator">
        {gameMode === 'daily' ? `Daily #${dayNumber}` : 'Free Play'}
        {settings.hardMode && <span className="hard-badge">HARD</span>}
      </div>

      <CandidateCounter
        count={candidateCount}
        total={totalWords}
        gameStatus={gameStatus}
      />

      <main className="game-area">
        <Board
          guesses={guesses}
          patterns={patterns}
          currentGuess={currentGuess}
          gameStatus={gameStatus}
          shakeRow={shakeRow}
          isRevealing={isRevealing}
        />
      </main>

      {gameStatus === 'won' && (
        <div className="game-over-bar">
          <button className="play-again-btn" onClick={startFreePlay}>
            Play Again
          </button>
          <button className="play-again-btn play-again-btn--secondary" onClick={() => setStatsOpen(true)}>
            View Stats
          </button>
        </div>
      )}

      <Keyboard onKeyPress={onKeyPress} keyboardStatus={keyboardStatus} />

      <Toast message={toastMessage} />

      <HelpModal isOpen={helpOpen} onClose={() => {
        setHelpOpen(false);
        localStorage.setItem('adversardle-seen-help', '1');
      }} />
      <StatsModal
        isOpen={statsOpen}
        onClose={() => setStatsOpen(false)}
        guesses={guesses}
        patterns={patterns}
        gameStatus={gameStatus}
        gameMode={gameMode}
        dayNumber={dayNumber}
      />
      <SettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        onNewGame={newGame}
        onFreePlay={startFreePlay}
        gameStatus={gameStatus}
      />
    </div>
  );
}
