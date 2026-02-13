# Adversardle — Adversarial AI Wordle

A Wordle-like word game where the AI actively fights back. Unlike regular Wordle where a word is pre-selected, this AI watches your guesses and strategically shifts the target to maximize difficulty while remaining provably fair.

**You win by "cornering" the AI into exactly one possible word.**

## How It Works

1. The AI starts with all 2,309 candidate words
2. On each guess, it partitions candidates by which color pattern they'd produce (243 possible patterns)
3. It picks the pattern that leaves the **most** candidates — the adversarial choice
4. Candidates are filtered to match the chosen pattern
5. When only 1 candidate remains, the player wins

The AI is adversarial but **provably fair**: every response is consistent with at least one real word.

## Features

- **Daily Challenge** — seeded PRNG so everyone gets the same game; shareable emoji grid
- **Free Play** — unlimited practice games
- **Candidate Counter** — shows how many words the AI could still be hiding
- **Shareable Results** — emoji grid copied to clipboard
- **Dark Mode / High Contrast Mode** — full theme support
- **Hard Mode** — revealed hints must be used in subsequent guesses
- **Animated Tile Flips** — shake on invalid, bounce on win
- **Stats Tracking** — games played, win %, streaks, guess distribution
- **No Guess Limit** — board grows dynamically beyond 6 rows
- **Responsive** — works on desktop and mobile

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Build

```bash
npm run build
npm run preview
```

## Tech Stack

- React 18 + Vite
- Zero additional dependencies — pure client-side logic
- CSS custom properties for theming
- localStorage for persistence

## Why It's Agentic

The AI autonomously reasons about all 243 possible color-pattern responses each turn and picks the one that maximizes remaining candidate words. It's not pattern-matching or random — it's strategic adversarial decision-making in real time.
