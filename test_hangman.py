"""Automated tests: run python -m unittest -v."""
import unittest
from unittest.mock import patch
from hangman import play_round

class HangmanTests(unittest.TestCase):
    def run_game(self, answers, word="cat", level="easy"):
        answers = iter(answers)
        output = []
        def fake_input(_=""):
            return next(answers, "z")
        with patch("hangman.random.choice", side_effect=lambda items: items[0]):
            result = play_round(level, input_func=fake_input, print_func=output.append, chosen_word=word)
        return result, "\n".join(output)

    def test_win(self):
        result, output = self.run_game(["c", "a", "t"])
        self.assertTrue(result[0])
        self.assertGreater(result[1], 0)
        self.assertIn("YOU WIN!", output)

    def test_invalid_input(self):
        result, output = self.run_game(["12", "c", "a", "t"])
        self.assertTrue(result[0])
        self.assertIn("Enter one English letter", output)

    def test_duplicate_guess(self):
        result, output = self.run_game(["c", "c", "a", "t"])
        self.assertTrue(result[0])
        self.assertIn("already tried", output)

    def test_six_misses(self):
        result, output = self.run_game(["x", "y", "z", "b", "d", "e"])
        self.assertFalse(result[0])
        self.assertEqual(result[1], 0)
        self.assertIn("GAME OVER!", output)

    def test_hint(self):
        result, output = self.run_game(["hint", "c", "t"])
        self.assertTrue(result[0])
        self.assertIn("Hint:", output)

    def test_non_english_word_rejected(self):
        with self.assertRaises(ValueError):
            self.run_game([], word="café")

    def test_invalid_level_rejected(self):
        with self.assertRaises(ValueError):
            self.run_game([], level="expert")

if __name__ == "__main__":
    unittest.main()
