# CodeAlpha Hangman Game

A terminal-based Hangman Challenge built with Python for the CodeAlpha Python Programming internship.

## Features
- Easy, Medium, and Hard levels
- Animals, Technology, and Nature word categories
- ASCII hangman drawing and six incorrect guesses
- One optional hint per round; using it reduces the score
- Input validation and repeated-guess protection
- Difficulty-based scoring, session statistics, win rate, and replay
- Standard library only; no API keys or extra packages

## Run
Python 3.10+ recommended. No dependencies required.

```bash
python hangman.py
```
On Windows, `py hangman.py` also works.

## Tests
```bash
python -m unittest -v
```

## How to play
Choose a level with 1, 2, or 3. Enter one English letter per guess. Six wrong guesses end the round. Type `hint` once to reveal a letter; this reduces the score. Solve the word to win points, then choose whether to play again.

## Files
- `hangman.py`: game logic and terminal interface
- `test_hangman.py`: automated regression tests
- `.gitignore`: excludes Python cache and local environment files
