"""Hangman Challenge - a feature-rich console word game using Python's standard library."""
import random
import string

MAX_WRONG = 6
SCORES = {"easy": 10, "medium": 20, "hard": 30}
WORDS = {
    "easy": {"Animals": ["tiger", "zebra", "panda", "horse"], "Tech": ["mouse", "robot", "phone", "pixel"], "Nature": ["river", "plant", "cloud", "earth"]},
    "medium": {"Animals": ["dolphin", "penguin", "elephant", "giraffe"], "Tech": ["keyboard", "software", "database", "internet"], "Nature": ["mountain", "rainfall", "sunlight", "waterfall"]},
    "hard": {"Animals": ["chimpanzee", "crocodile", "porcupine", "rattlesnake"], "Tech": ["programming", "encryption", "javascript", "algorithm"], "Nature": ["environment", "biodiversity", "thunderstorm", "greenhouse"]},
}
ART = [
"  +---+\n  |   |\n      |\n      |\n      |\n      |\n=========",
"  +---+\n  |   |\n  O   |\n      |\n      |\n      |\n=========",
"  +---+\n  |   |\n  O   |\n  |   |\n      |\n      |\n=========",
"  +---+\n  |   |\n  O   |\n /|   |\n      |\n      |\n=========",
"  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n      |\n=========",
"  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n      |\n=========",
"  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n      |\n=========",
]

def choose_difficulty(input_func=input, print_func=print):
    options = {"1": "easy", "2": "medium", "3": "hard"}
    while True:
        print_func("\nChoose difficulty: 1) Easy  2) Medium  3) Hard")
        choice = input_func("Choice: ").strip()
        if choice in options:
            return options[choice]
        print_func("Please enter 1, 2, or 3.")

def show_status(word, correct, wrong, print_func=print):
    print_func(ART[len(wrong)])
    print_func("Word: " + " ".join(c if c in correct else "_" for c in word))
    print_func("Wrong guesses: " + (", ".join(sorted(wrong)) or "None"))
    print_func(f"Chances left: {MAX_WRONG - len(wrong)}")

def play_round(difficulty, input_func=input, print_func=print, chosen_word=None):
    if difficulty not in WORDS:
        raise ValueError("Difficulty must be easy, medium, or hard.")
    category = random.choice(list(WORDS[difficulty]))
    word = (chosen_word or random.choice(WORDS[difficulty][category])).lower()
    if not word.isascii() or not word.isalpha():
        raise ValueError("Secret words must contain English letters only.")
    correct, wrong, hint_used = set(), set(), False
    print_func("\n" + "=" * 36 + "\n       HANGMAN CHALLENGE\n" + "=" * 36)
    print_func(f"Level: {difficulty.title()} | Category: {category}")
    print_func("Guess one letter at a time; type 'hint' once for help.")
    while len(wrong) < MAX_WRONG:
        show_status(word, correct, wrong, print_func)
        guess = input_func("Your guess: ").strip().lower()
        if guess == "hint":
            if hint_used:
                print_func("Hint already used this round.")
                continue
            hidden = sorted(set(word) - correct)
            if not hidden:
                break
            letter = random.choice(hidden)
            correct.add(letter)
            hint_used = True
            print_func(f"Hint: revealed '{letter}'. Using a hint costs 5 points.")
        elif len(guess) != 1 or guess not in string.ascii_lowercase:
            print_func("Enter one English letter (A-Z), or type 'hint'.")
            continue
        elif guess in correct or guess in wrong:
            print_func("You already tried that letter.")
            continue
        elif guess in word:
            correct.add(guess)
            print_func("Good guess!")
        else:
            wrong.add(guess)
            print_func("Not in the word. Keep trying!")
        if set(word) <= correct:
            score = SCORES[difficulty] + (MAX_WRONG - len(wrong)) * 2
            if hint_used:
                score = max(1, score - 5)
            print_func(f"\nYOU WIN! The word was '{word}'.")
            print_func(f"Score earned: {score}")
            return True, score
    show_status(word, correct, wrong, print_func)
    print_func(f"\nGAME OVER! The word was '{word}'.")
    return False, 0

def main():
    games = wins = points = 0
    print("\nWELCOME TO HANGMAN CHALLENGE")
    while True:
        level = choose_difficulty()
        won, score = play_round(level)
        games += 1
        wins += int(won)
        points += score
        print("\nSESSION STATS")
        print(f"Games played: {games} | Wins: {wins} | Win rate: {wins / games:.0%}")
        print(f"Total points: {points}")
        while True:
            again = input("Play again? (y/n): ").strip().lower()
            if again in {"y", "yes"}:
                break
            if again in {"n", "no"}:
                print("Thanks for playing. See you next time!")
                return
            print("Please enter y or n.")

if __name__ == "__main__":
    main()
