import Tile from './Tile';

export default function Row({ guess = '', pattern = null, isCurrentRow = false, isRevealing = false, isShaking = false, isWinRow = false }) {
  const letters = guess.padEnd(5, ' ').split('').slice(0, 5);

  return (
    <div className={`row ${isShaking ? 'row--shake' : ''}`}>
      {letters.map((letter, i) => (
        <Tile
          key={i}
          letter={letter === ' ' ? '' : letter.toUpperCase()}
          state={pattern ? pattern[i] : null}
          position={i}
          isRevealing={isRevealing}
          isBouncing={isWinRow && !isRevealing}
        />
      ))}
    </div>
  );
}
