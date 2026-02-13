import { useState, useCallback, useRef, useEffect } from 'react';
import { SOLUTIONS } from '../data/solutions';
import { AdversarialAgent } from '../agents/AdversarialAgent';
import { isValidGuess, checkHardMode, buildKeyboardStatus } from '../utils/gameLogic';
import { updateStatsAfterGame, loadDailyState, saveDailyState, clearDailyState } from '../utils/storage';
import { getDayNumber, getDailySeed } from '../utils/dailySeed';

/**
 * Central game state hook.
 * Manages guesses, patterns, game status, and communication with the AdversarialAgent.
 */
export function useGame(hardMode = false) {
  const agentRef = useRef(new AdversarialAgent(SOLUTIONS));

  const [gameMode, setGameMode] = useState('daily'); // 'daily' | 'free'
  const [guesses, setGuesses] = useState([]);
  const [patterns, setPatterns] = useState([]);
  const [currentGuess, setCurrentGuess] = useState('');
  const [gameStatus, setGameStatus] = useState('playing'); // 'playing' | 'won' | 'lost'
  const [candidateCount, setCandidateCount] = useState(SOLUTIONS.length);
  const [revealedWord, setRevealedWord] = useState(null);
  const [shakeRow, setShakeRow] = useState(false);
  const [toastMessage, setToastMessage] = useState(null);
  const [isRevealing, setIsRevealing] = useState(false);

  const dayNumber = getDayNumber();
  const dailySeed = getDailySeed(dayNumber);

  // Load daily state on mount
  useEffect(() => {
    if (gameMode === 'daily') {
      const saved = loadDailyState(dayNumber);
      if (saved) {
        // Replay guesses to restore agent state
        const agent = new AdversarialAgent(SOLUTIONS);
        const replayPatterns = [];
        for (const guess of saved.guesses) {
          const result = agent.processGuessDeterministic(guess, dailySeed);
          replayPatterns.push(result.pattern);
        }
        agentRef.current = agent;
        setGuesses(saved.guesses);
        setPatterns(replayPatterns);
        setCandidateCount(agent.candidateCount);
        if (saved.gameStatus === 'won') {
          setGameStatus('won');
          setRevealedWord(saved.revealedWord);
        }
      }
    }
  }, [gameMode, dayNumber, dailySeed]);

  const showToast = useCallback((msg, duration = 1500) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), duration);
  }, []);

  const triggerShake = useCallback(() => {
    setShakeRow(true);
    setTimeout(() => setShakeRow(false), 600);
  }, []);

  const submitGuess = useCallback(() => {
    if (gameStatus !== 'playing') return;
    if (currentGuess.length !== 5) {
      showToast('Not enough letters');
      triggerShake();
      return;
    }

    const guess = currentGuess.toLowerCase();

    if (!isValidGuess(guess)) {
      showToast('Not in word list');
      triggerShake();
      return;
    }

    // Hard mode check
    if (hardMode && guesses.length > 0) {
      const check = checkHardMode(guess, guesses, patterns);
      if (!check.valid) {
        showToast(check.message);
        triggerShake();
        return;
      }
    }

    setIsRevealing(true);

    // Process through the adversarial agent
    const result = gameMode === 'daily'
      ? agentRef.current.processGuessDeterministic(guess, dailySeed)
      : agentRef.current.processGuess(guess);

    const newGuesses = [...guesses, guess];
    const newPatterns = [...patterns, result.pattern];

    setGuesses(newGuesses);
    setPatterns(newPatterns);
    setCandidateCount(result.candidates);
    setCurrentGuess('');

    // Delay game-end logic until tile flip animation completes
    setTimeout(() => {
      setIsRevealing(false);

      if (result.revealedWord) {
        setGameStatus('won');
        setRevealedWord(result.revealedWord);
        const stats = updateStatsAfterGame(true, newGuesses.length);
        showToast(`Cornered the AI in ${newGuesses.length} guesses!`, 3000);
      }

      // Save daily state
      if (gameMode === 'daily') {
        saveDailyState({
          dayNumber,
          guesses: newGuesses,
          gameStatus: result.revealedWord ? 'won' : 'playing',
          revealedWord: result.revealedWord,
        });
      }
    }, 5 * 300 + 200); // 5 tiles * 300ms delay + buffer
  }, [currentGuess, guesses, patterns, gameStatus, hardMode, gameMode, dailySeed, dayNumber, showToast, triggerShake]);

  const onKeyPress = useCallback((key) => {
    if (gameStatus !== 'playing' || isRevealing) return;

    if (key === 'Enter') {
      submitGuess();
    } else if (key === 'Backspace') {
      setCurrentGuess(prev => prev.slice(0, -1));
    } else if (/^[a-zA-Z]$/.test(key) && currentGuess.length < 5) {
      setCurrentGuess(prev => prev + key.toLowerCase());
    }
  }, [gameStatus, isRevealing, currentGuess, submitGuess]);

  // Physical keyboard handler
  useEffect(() => {
    const handler = (e) => {
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      if (e.key === 'Enter' || e.key === 'Backspace' || /^[a-zA-Z]$/.test(e.key)) {
        e.preventDefault();
        onKeyPress(e.key);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onKeyPress]);

  const keyboardStatus = buildKeyboardStatus(guesses, patterns);

  const startFreePlay = useCallback(() => {
    agentRef.current = new AdversarialAgent(SOLUTIONS);
    setGameMode('free');
    setGuesses([]);
    setPatterns([]);
    setCurrentGuess('');
    setGameStatus('playing');
    setCandidateCount(SOLUTIONS.length);
    setRevealedWord(null);
  }, []);

  const startDaily = useCallback(() => {
    agentRef.current = new AdversarialAgent(SOLUTIONS);
    setGameMode('daily');
    setGuesses([]);
    setPatterns([]);
    setCurrentGuess('');
    setGameStatus('playing');
    setCandidateCount(SOLUTIONS.length);
    setRevealedWord(null);
    clearDailyState();
    // Trigger reload of daily state
    const saved = loadDailyState(dayNumber);
    if (saved) {
      const agent = new AdversarialAgent(SOLUTIONS);
      for (const guess of saved.guesses) {
        agent.processGuessDeterministic(guess, dailySeed);
      }
      agentRef.current = agent;
      setGuesses(saved.guesses);
      setPatterns(saved.guesses.map((g, i) => {
        // Recompute — simpler to just reset
      }));
    }
  }, [dayNumber, dailySeed]);

  const newGame = useCallback(() => {
    agentRef.current = new AdversarialAgent(SOLUTIONS);
    setGuesses([]);
    setPatterns([]);
    setCurrentGuess('');
    setGameStatus('playing');
    setCandidateCount(SOLUTIONS.length);
    setRevealedWord(null);
    if (gameMode === 'free') {
      // Just reset for free play
    }
  }, [gameMode]);

  return {
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
    startDaily,
    newGame,
    totalWords: SOLUTIONS.length,
  };
}
