export default function HelpModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>How To Play</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="modal-body">
          <p><strong>Adversardle</strong> is Wordle with an AI that fights back.</p>

          <p>Unlike regular Wordle, there is <strong>no pre-selected word</strong>. The AI starts with all possible 5-letter words and strategically picks responses to maximize difficulty.</p>

          <h3>How It Works</h3>
          <ol>
            <li>Guess any valid 5-letter word</li>
            <li>The AI looks at ALL remaining candidate words</li>
            <li>It picks the color pattern that leaves the <strong>most</strong> possibilities</li>
            <li>Your goal: <strong>corner the AI</strong> into exactly one word</li>
          </ol>

          <h3>Color Clues</h3>
          <div className="help-examples">
            <div className="help-row">
              <div className="help-tile help-tile--correct">W</div>
              <span><strong>Green</strong> — correct letter, correct spot</span>
            </div>
            <div className="help-row">
              <div className="help-tile help-tile--present">I</div>
              <span><strong>Yellow</strong> — correct letter, wrong spot</span>
            </div>
            <div className="help-row">
              <div className="help-tile help-tile--absent">X</div>
              <span><strong>Gray</strong> — letter not in the word</span>
            </div>
          </div>

          <h3>The Catch</h3>
          <p>The AI is <strong>adversarial but provably fair</strong>. Every response is consistent with at least one real word. It just picks the hardest-possible consistent response each turn.</p>

          <p>The candidate counter shows how many words the AI could still be hiding. When it hits 1 — you've cornered it!</p>

          <h3>Tips</h3>
          <ul>
            <li>Start with words that have common, distinct letters</li>
            <li>Watch the candidate counter to gauge progress</li>
            <li>There's no guess limit — take your time!</li>
            <li>Typical games take 6-12 guesses</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
