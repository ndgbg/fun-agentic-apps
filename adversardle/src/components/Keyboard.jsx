import { memo, useCallback } from 'react';

const ROWS = [
  ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
  ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
  ['Enter', 'z', 'x', 'c', 'v', 'b', 'n', 'm', 'Backspace'],
];

function Keyboard({ onKeyPress, keyboardStatus }) {
  const handleClick = useCallback((key) => {
    onKeyPress(key);
  }, [onKeyPress]);

  return (
    <div className="keyboard">
      {ROWS.map((row, rowIdx) => (
        <div key={rowIdx} className="keyboard-row">
          {row.map(key => {
            const status = keyboardStatus[key] || 'unused';
            const isSpecial = key === 'Enter' || key === 'Backspace';
            const displayKey = key === 'Backspace' ? '⌫' : key === 'Enter' ? 'ENTER' : key.toUpperCase();

            return (
              <button
                key={key}
                className={`key ${isSpecial ? 'key--wide' : ''} key--${status}`}
                onClick={() => handleClick(key)}
                aria-label={key}
              >
                {displayKey}
              </button>
            );
          })}
        </div>
      ))}
    </div>
  );
}

export default memo(Keyboard);
