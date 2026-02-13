import Row from './Row';

export default function Board({ guesses, patterns, currentGuess, gameStatus, shakeRow, isRevealing }) {
  // Always show at least 6 rows, but grow dynamically
  const minRows = 6;
  const totalRows = Math.max(minRows, guesses.length + (gameStatus === 'playing' ? 1 : 0));

  const rows = [];

  for (let i = 0; i < totalRows; i++) {
    if (i < guesses.length) {
      // Completed guess row
      const isLastGuess = i === guesses.length - 1;
      rows.push(
        <Row
          key={i}
          guess={guesses[i]}
          pattern={patterns[i]}
          isRevealing={isLastGuess && isRevealing}
          isWinRow={isLastGuess && gameStatus === 'won'}
        />
      );
    } else if (i === guesses.length && gameStatus === 'playing') {
      // Current input row
      rows.push(
        <Row
          key={i}
          guess={currentGuess}
          isCurrentRow
          isShaking={shakeRow}
        />
      );
    } else {
      // Empty row
      rows.push(<Row key={i} />);
    }
  }

  return <div className="board">{rows}</div>;
}
