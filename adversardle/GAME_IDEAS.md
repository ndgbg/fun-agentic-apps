# Adversardle Spin-off Game Ideas

Brainstormed ideas for new games using the same **adversarial partition** algorithm at the core of Adversardle.

## The Core Mechanic (Quick Recap)

Adversardle works by:
1. Maintaining a pool of candidate answers
2. For each guess, partitioning candidates by what feedback pattern they'd produce
3. Picking the partition with the **most** candidates (hardest for the player)
4. Player wins by cornering the AI into exactly 1 candidate

The same pattern — *adversarial partition over a candidate space* — applies to any deduction game where feedback is discrete.

---

## Game Ideas

### 1. Evil Hangman

**The twist:** Classic Hangman, but the AI has no fixed word. When you guess a letter, it partitions words by *where that letter appears* (or doesn't), then picks the partition that leaves the most candidates.

**How it plays:**
- AI reveals word length upfront (e.g., 6 letters, __ __ __ __ __ __)
- Player guesses one letter at a time
- AI partitions words by which positions contain that letter (e.g., "E at positions 1 and 4", "E at position 2 only", "no E")
- AI picks the partition that keeps the most words alive
- Player has 6–8 wrong guesses before losing

**Why it's interesting:**
- Completely different UX from Adversardle (letter-by-letter vs. full-word guesses)
- Much harder than regular Hangman — common letters like E/A/S/T often get revealed nowhere
- Uses the same word list, zero new data needed
- "Wrong guess" mechanic adds real stakes absent from Adversardle

**Difficulty lever:** Vary allowed wrong guesses (6 = hard, 10 = easy).

---

### 2. Adversarial Mastermind

**The twist:** Classic Mastermind code-breaking game, but the AI has no fixed code. It picks its peg feedback adversarially.

**How it plays:**
- Player guesses a sequence of 4 colors (from 6 possible colors)
- Normal Mastermind feedback: X black pegs (right color, right position) + Y white pegs (right color, wrong position)
- AI partitions all 1,296 possible codes by (X, Y) pairs, picks the response that leaves the most codes alive
- Player wins by cornering AI into 1 remaining code

**Why it's interesting:**
- No word list — pure combinatorics (6^4 = 1,296 codes)
- Feedback is numeric pairs, not color tiles — different feel
- Mastermind is already beloved; "adversarial" twist is a natural evolution
- Smaller search space than Adversardle (1,296 vs. 2,309) but harder feedback to parse

**Visual:** Color-coded pegs in a grid, classic Mastermind aesthetic.

---

### 3. Adversarial Jotto

**The twist:** Jotto is Wordle's ancestor — you guess words and are told how many letters your guess *shares* with the target (not which positions). Adversarial Jotto picks the count adversarially.

**How it plays:**
- Player guesses a 5-letter word
- AI responds with a single number: how many letters the guess shares with the hidden word (0–5, position-irrelevant)
- AI picks the number that leaves the most candidates
- Player wins by cornering AI into 1 word

**Why it's interesting:**
- Much harder than Adversardle — you get *less* information per guess (just a number, not a colored pattern)
- Forces purer logical deduction
- Minimal UI — just a guess and a digit, like a puzzle in a newspaper
- Great for players who find Adversardle too easy

**Compared to Adversardle:** Same word list, same algorithm, but instead of 243 possible patterns (3^5) there are only 6 possible responses (0–5). Each response covers far more candidates, so narrowing is slower and harder.

---

### 4. Adversarial 20 Questions

**The twist:** The AI "thinks" of something from a large category (animals, countries, famous people). You ask yes/no questions. The AI answers adversarially — always giving the answer that leaves the most matching items.

**How it plays:**
- Pick a category: Animals (500+ entries), Countries (195), Historical Figures, Movies, etc.
- Each item has a set of binary attributes (mammal? lives in water? has four legs? endangered? etc.)
- Ask yes/no questions by selecting attributes
- AI answers whichever of yes/no keeps more items alive
- You have 20 questions to narrow down to 1 item

**Why it's interesting:**
- Completely different domain from word games — broader appeal
- Tests strategic thinking: what questions eliminate the most candidates?
- Social fun: "I asked if it was a mammal and the AI said no — it's cheating!" (it's not, it's adversarial)
- Can be powered entirely client-side with a pre-built attribute matrix

**Data needed:** A JSON dataset of items + boolean attributes per item. This can be hand-curated or generated.

---

### 5. Adversarial Numbers (Numble)

**The twist:** Guess a 4-digit number. Instead of Wordle's green/yellow/gray, each digit gets: ✓ (correct), ↑ (too high), ↓ (too low). AI picks feedback adversarially.

**How it plays:**
- Player guesses a 4-digit number (0000–9999, or 1000–9999)
- Feedback per digit: correct / too high / too low
- AI partitions all 9,000 numbers by feedback pattern, picks the hardest
- Player wins by cornering AI into 1 number

**Why it's interesting:**
- No domain knowledge required — pure logic
- Different feedback type: ordered (not binary presence/absence)
- Accessible to non-word-game fans
- Fun variant: 3-digit numbers for kids, 6-digit for masochists

**Search space:** 9,000 candidates vs. 2,309 for Adversardle — harder to corner.

---

### 6. Adversardle: Phrases (5-Word Edition)

**The twist:** Same Adversardle mechanic but guess common **phrases or idioms** where each "tile" is a word, not a letter.

**How it plays:**
- Phrases are 3–5 words long
- Each word gets green/yellow/gray feedback (right word right position / right word wrong position / word not in phrase)
- AI picks feedback adversarially across a list of ~500 common phrases

**Why it's interesting:**
- Harder to enumerate all possibilities mentally — the search space *feels* infinite
- Cultural knowledge matters more than pure logic
- Fresh experience even for Adversardle veterans
- "BREAK THE ICE" — is "break" in the right position? AI says no.

---

### 7. Adversardle: Emoji

**The twist:** Guess a sequence of 4 emojis from a curated set of ~50. Same green/yellow/gray feedback.

**How it plays:**
- A grid of ~50 emoji to choose from
- Guess a sequence of 4
- Feedback: right emoji right position (green), right emoji wrong position (yellow), not in sequence (gray)
- AI picks feedback adversarially across all valid 4-emoji sequences

**Why it's interesting:**
- Immediately shareable — emoji feedback grids are perfect for social media
- No language dependency — globally playable
- The visual/colorful UI differentiates it clearly from Adversardle
- Small curated emoji set keeps the search space manageable

---

### 8. Cooperative Adversardle (2 Players vs. AI)

**The twist:** Two players collaborate to corner the AI. They alternate guesses but share information.

**How it plays:**
- Two players take turns guessing (player A, player B, player A, ...)
- Both see all previous guesses and patterns
- They must corner the AI in 10 total guesses (5 each)
- Can play async (share a link/state) or same-screen

**Why it's interesting:**
- Social game — best enjoyed with a friend or partner
- Communication meta-game: "I'm going to guess CRANE to test vowels, you follow up on consonants"
- Same core engine, zero new algorithm needed
- Could add a chat/emoji reaction strip between guesses

---

## Difficulty Variants (Across All Ideas)

Any of the above could include these modes:

| Mode | Mechanic |
|------|----------|
| **Classic** | AI picks the hardest valid response |
| **Sadist** | AI picks hardest response AND has 2x the normal candidate pool |
| **Fair** | AI has a fixed hidden answer (regular game mode) |
| **Race** | Timed — corner the AI in under 60 seconds |
| **Daily** | Seeded for consistency across all players |

---

## Recommendation

The two strongest candidates for a next build:

1. **Evil Hangman** — Different UX, same algorithm, immediately understandable, no new data
2. **Adversarial Mastermind** — Zero word dependency, elegant numeric feedback, clean visual design

Both can be built as pure client-side React apps with no external dependencies, matching Adversardle's architecture exactly.
