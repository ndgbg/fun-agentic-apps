import { memo } from 'react';

function CandidateCounter({ count, total, gameStatus }) {
  const percentage = ((count / total) * 100).toFixed(1);
  const isLow = count <= 10;
  const isCornered = count === 1;

  let message;
  if (gameStatus === 'won') {
    message = 'AI cornered! You win!';
  } else if (isCornered) {
    message = 'AI cornered — guess the word!';
  } else if (isLow) {
    message = `AI is nervous... ${count} word${count === 1 ? '' : 's'} left`;
  } else if (count === total) {
    message = `AI is scheming among ${count.toLocaleString()} words...`;
  } else {
    message = `AI hiding among ${count.toLocaleString()} words (${percentage}%)`;
  }

  return (
    <div className={`candidate-counter ${isLow ? 'candidate-counter--low' : ''} ${isCornered || gameStatus === 'won' ? 'candidate-counter--cornered' : ''}`}>
      <div className="candidate-bar">
        <div
          className="candidate-bar-fill"
          style={{ width: `${Math.max(2, (count / total) * 100)}%` }}
        />
      </div>
      <span className="candidate-text">{message}</span>
    </div>
  );
}

export default memo(CandidateCounter);
