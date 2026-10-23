# Hangman Arena — Visual Python Game

A graphical Hangman word game built with Python and Tkinter. It is designed to feel like a small arcade game while staying easy to install and run: no third-party packages, API keys, or internet connection required.

## Highlights
- Dark arcade-style interface with a custom-drawn Hangman illustration
- Clickable A–Z keyboard plus physical keyboard controls
- Three difficulty levels: Easy, Medium, Hard
- Six categories: Animals, Technology, Nature, Space, Food, and Sports
- A descriptive clue for every word
- Six lives, clear feedback, and win/loss states
- One hint per round; hints reveal a letter and deduct five points
- Difficulty-based scoring, streaks, total points, wins, and personal best
- Local stats persist between launches
- Automated game-logic tests that do not need to open a window

## Requirements
- Python 3.10+ recommended
- Tkinter, normally included with standard Python on Windows
- No pip installs required

## Launch on Windows
Open this folder in VS Code, choose Terminal → New Terminal, and run:

    py hangman.py

If the py launcher is unavailable, run:

    python hangman.py

This opens the graphical game window. Run hangman.py to play; test_hangman.py is for tests only.

## How to play
1. Select Easy, Medium, or Hard in the dropdown.
2. Read the clue and choose a letter with the on-screen keyboard or your physical keyboard.
3. Each incorrect letter uses one of six lives.
4. Click Hint or press F1 to reveal one hidden letter. A hint reduces your final score by five points.
5. Solve the word to win. Choose New Game or press F2 for another round.
6. Build a win streak and improve your personal best.

## Run tests

    py -m unittest -v

## Project files
- hangman.py — game UI, word bank, scoring, and game logic
- test_hangman.py — automated tests for the game logic
- .gitignore — ignores Python cache and local stats
- hangman_stats.json — created locally when a round ends; not committed

## Privacy
Game statistics are saved in a local JSON file beside the script. The game does not transmit data over the internet.
