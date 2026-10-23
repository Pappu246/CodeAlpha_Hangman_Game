"""Unit tests for Hangman Arena. Run with: py -m unittest -v."""
import random
import unittest
from hangman import GameState, MAX_WRONG, WORDS, apply_guess, calculate_score, create_game, use_hint


class GameLogicTests(unittest.TestCase):
    def test_create_game_for_each_difficulty(self):
        for level in ("Easy", "Medium", "Hard"):
            game = create_game(level, random.Random(4))
            self.assertIn(game.category, WORDS[level])
            self.assertTrue(game.word.isascii() and game.word.isalpha())
            self.assertEqual(game.status, "playing")

    def test_reject_invalid_difficulty(self):
        with self.assertRaises(ValueError):
            create_game("Impossible")

    def test_correct_guess_and_win(self):
        game = GameState("cat", "A pet", "Animals", "Easy")
        self.assertEqual(apply_guess(game, "C"), "correct")
        self.assertEqual(apply_guess(game, "a"), "correct")
        self.assertEqual(apply_guess(game, "t"), "won")
        self.assertGreater(game.score, 0)
        self.assertEqual(calculate_score(game), game.score)

    def test_wrong_guess_loses_one_life(self):
        game = GameState("cat", "A pet", "Animals", "Easy")
        self.assertEqual(apply_guess(game, "z"), "wrong")
        self.assertEqual(game.lives_left, MAX_WRONG - 1)

    def test_six_wrong_guesses_end_the_round(self):
        game = GameState("cat", "A pet", "Animals", "Easy")
        for letter in "zxyuvw":
            result = apply_guess(game, letter)
        self.assertEqual(result, "lost")
        self.assertEqual(game.lives_left, 0)
        self.assertEqual(game.score, 0)

    def test_duplicate_and_invalid_guesses(self):
        game = GameState("cat", "A pet", "Animals", "Easy")
        self.assertEqual(apply_guess(game, "?"), "invalid")
        apply_guess(game, "z")
        self.assertEqual(apply_guess(game, "z"), "duplicate")

    def test_hint_reveals_one_letter_and_reduces_score(self):
        game = GameState("cat", "A pet", "Animals", "Easy")
        revealed = use_hint(game, random.Random(2))
        self.assertIn(revealed, game.word)
        self.assertTrue(game.hint_used)
        self.assertIsNone(use_hint(game, random.Random(3)))
        for letter in set(game.word):
            apply_guess(game, letter)
        self.assertEqual(game.status, "won")
        full_score = 10 + len(game.word) * 2 + MAX_WRONG * 3
        self.assertLess(game.score, full_score)

    def test_cannot_guess_after_round_ends(self):
        game = GameState("cat", "A pet", "Animals", "Easy")
        for letter in "cat":
            apply_guess(game, letter)
        self.assertEqual(apply_guess(game, "z"), "finished")

    def test_all_words_have_clues_and_valid_letters(self):
        for levels in WORDS.values():
            for entries in levels.values():
                for word, clue in entries:
                    self.assertTrue(word.isascii() and word.isalpha(), word)
                    self.assertTrue(clue.strip(), word)


if __name__ == "__main__":
    unittest.main()
