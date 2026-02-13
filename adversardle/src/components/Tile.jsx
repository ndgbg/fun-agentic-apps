import { memo } from 'react';

const STATE_CLASSES = {
  0: 'tile--absent',
  1: 'tile--present',
  2: 'tile--correct',
};

function Tile({ letter = '', state = null, position = 0, isRevealing = false, isBouncing = false }) {
  const hasLetter = letter !== '';
  const revealed = state !== null;

  const className = [
    'tile',
    hasLetter && !revealed ? 'tile--filled' : '',
    revealed ? STATE_CLASSES[state] : '',
    isRevealing ? 'tile--revealing' : '',
    isBouncing ? 'tile--bounce' : '',
  ].filter(Boolean).join(' ');

  const animationDelay = isRevealing ? `${position * 300}ms` : undefined;
  const bounceDelay = isBouncing ? `${position * 100}ms` : undefined;

  return (
    <div
      className={className}
      style={{
        animationDelay: animationDelay || bounceDelay,
      }}
    >
      <div className="tile-inner">
        <div className="tile-front">{letter}</div>
        <div className="tile-back">{letter}</div>
      </div>
    </div>
  );
}

export default memo(Tile);
