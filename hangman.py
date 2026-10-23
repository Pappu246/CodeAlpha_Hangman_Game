"""Hangman Arena: a graphical word game built with Python's Tkinter."""
from __future__ import annotations

import json
import random
import string
import tkinter as tk
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import ttk

MAX_WRONG = 6
LEVELS = {
    "Easy": {"base": 10, "label": "WARM-UP"},
    "Medium": {"base": 20, "label": "CHALLENGE"},
    "Hard": {"base": 35, "label": "EXPERT"},
}
WORDS = {
    "Easy": {
        "Animals": [("tiger", "A big cat with dark stripes"), ("panda", "A black-and-white bear"), ("zebra", "An animal with black and white stripes"), ("horse", "An animal people can ride")],
        "Technology": [("mouse", "A device used to control a pointer"), ("robot", "A machine that can perform tasks"), ("phone", "A device used to call people"), ("pixel", "The tiny unit of a digital image")],
        "Nature": [("river", "A natural stream of flowing water"), ("cloud", "Tiny water droplets floating in the sky"), ("plant", "A living thing that often grows in soil"), ("earth", "The planet we live on")],
        "Space": [("comet", "An icy object that travels around the Sun"), ("orbit", "The path an object follows around another"), ("lunar", "Related to the Moon"), ("venus", "The second planet from the Sun")],
        "Food": [("pizza", "A baked dish with toppings"), ("mango", "A sweet tropical fruit"), ("bread", "A staple food made from flour"), ("pasta", "An Italian food made from dough")],
        "Sports": [("chess", "A strategy game played on 64 squares"), ("tennis", "A racket sport played over a net"), ("rugby", "A team sport played with an oval ball"), ("skate", "To glide on wheels or blades")],
    },
    "Medium": {
        "Animals": [("dolphin", "A highly intelligent marine mammal"), ("penguin", "A flightless bird that swims well"), ("giraffe", "A very tall mammal with a long neck"), ("octopus", "A sea animal with eight arms")],
        "Technology": [("keyboard", "A device used to type on a computer"), ("software", "Programs that run on a computer"), ("network", "Connected computers and devices"), ("browser", "An app used to open websites")],
        "Nature": [("rainfall", "Water falling from clouds"), ("mountain", "A very high natural landform"), ("sunlight", "Light that comes from the Sun"), ("desert", "A very dry region with little rain")],
        "Space": [("asteroid", "A rocky object that orbits the Sun"), ("galaxy", "A huge system of stars and gas"), ("eclipse", "When one celestial body blocks another"), ("cosmos", "The universe considered as a whole")],
        "Food": [("sandwich", "Food placed between slices of bread"), ("pancake", "A flat cake cooked in a pan"), ("noodles", "Long thin strips of dough"), ("biscuit", "A small baked snack")],
        "Sports": [("football", "A team sport played by kicking a ball"), ("cricket", "A bat-and-ball sport with wickets"), ("badminton", "A racket sport played with a shuttlecock"), ("cycling", "Riding a two-wheeled vehicle")],
    },
    "Hard": {
        "Animals": [("chimpanzee", "A great ape known for its intelligence"), ("crocodile", "A large reptile that lives near water"), ("porcupine", "A mammal covered in sharp quills"), ("rhinoceros", "A large mammal with one or two horns")],
        "Technology": [("algorithm", "A step-by-step procedure for solving a problem"), ("encryption", "The process of encoding information securely"), ("processor", "The computer component that executes instructions"), ("programming", "Writing instructions that a computer can execute")],
        "Nature": [("biodiversity", "The variety of living things in an ecosystem"), ("thunderstorm", "A storm with lightning and thunder"), ("greenhouse", "A structure used to grow plants in warmth"), ("earthquake", "Sudden shaking of the ground")],
        "Space": [("astronaut", "A person trained to travel into space"), ("constellation", "A recognized pattern of stars"), ("supernova", "A powerful explosion of a star"), ("telescope", "An instrument used to observe distant objects")],
        "Food": [("croissant", "A buttery crescent-shaped pastry"), ("blueberry", "A small round blue-purple fruit"), ("quesadilla", "A tortilla dish filled with melted cheese"), ("spaghetti", "Long thin strands of Italian pasta")],
        "Sports": [("gymnastics", "A sport involving balance, strength and tumbling"), ("basketball", "A sport played by shooting a ball through a hoop"), ("volleyball", "A team sport played by hitting a ball over a net"), ("marathon", "A long-distance running race")],
    },
}

C = {
    "bg": "#0B1120", "panel": "#121C2F", "surface": "#18253A",
    "key": "#22324A", "line": "#2C3B52", "text": "#F2F6FC",
    "muted": "#9AABC2", "teal": "#65E6D2", "teal_dark": "#163F45",
    "green": "#43D9A3", "red": "#FF718B", "gold": "#FFD166", "blue": "#82AFFF",
}
FONT = "Segoe UI"
STATS_FILE = Path(__file__).resolve().with_name("hangman_stats.json")


@dataclass
class GameState:
    word: str
    clue: str
    category: str
    difficulty: str
    correct: set[str] = field(default_factory=set)
    wrong: set[str] = field(default_factory=set)
    hint_used: bool = False
    hint_letter: str | None = None
    status: str = "playing"
    score: int = 0

    @property
    def lives_left(self) -> int:
        return MAX_WRONG - len(self.wrong)


def create_game(difficulty: str, rng=None) -> GameState:
    """Choose a word and clue for a new round."""
    if difficulty not in WORDS:
        raise ValueError("Choose Easy, Medium, or Hard.")
    chooser = rng or random
    category = chooser.choice(list(WORDS[difficulty]))
    word, clue = chooser.choice(WORDS[difficulty][category])
    return GameState(word.lower(), clue, category, difficulty)


def calculate_score(game: GameState) -> int:
    if game.status != "won":
        return 0
    score = LEVELS[game.difficulty]["base"] + len(game.word) * 2 + game.lives_left * 3
    return max(5, score - (5 if game.hint_used else 0))


def apply_guess(game: GameState, letter: str) -> str:
    """Validate and apply one letter; return a result code for the GUI."""
    letter = letter.strip().lower()
    if game.status != "playing":
        return "finished"
    if len(letter) != 1 or letter not in string.ascii_lowercase:
        return "invalid"
    if letter in game.correct or letter in game.wrong:
        return "duplicate"
    if letter in game.word:
        game.correct.add(letter)
        if set(game.word) <= game.correct:
            game.status = "won"
            game.score = calculate_score(game)
            return "won"
        return "correct"
    game.wrong.add(letter)
    if len(game.wrong) >= MAX_WRONG:
        game.status = "lost"
        return "lost"
    return "wrong"


def use_hint(game: GameState, rng=None) -> str | None:
    """Reveal one unrevealed letter. A hint is available once per round."""
    if game.status != "playing" or game.hint_used:
        return None
    hidden = sorted(set(game.word) - game.correct)
    if not hidden:
        return None
    letter = (rng or random).choice(hidden)
    game.correct.add(letter)
    game.hint_used = True
    game.hint_letter = letter
    if set(game.word) <= game.correct:
        game.status = "won"
        game.score = calculate_score(game)
    return letter


class HangmanArena:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Hangman Arena | Word Challenge")
        root.geometry("1160x790")
        root.minsize(980, 700)
        root.configure(bg=C["bg"])
        root.option_add("*Font", (FONT, 10))
        self.difficulty = tk.StringVar(value="Medium")
        self.game = create_game("Medium")
        self.stats = self.load_stats()
        self.round_recorded = False
        self.buttons: dict[str, tk.Button] = {}
        self.tiles: list[tk.Label] = []
        self.build_ui()
        self.update_ui("A new word is ready. Pick a letter!")
        root.bind("<KeyPress>", self.on_key)
        self.canvas.bind("<Configure>", lambda _event: self.draw_scene())

    @staticmethod
    def load_stats() -> dict[str, int]:
        stats = {"games": 0, "wins": 0, "losses": 0, "points": 0, "best": 0, "streak": 0, "best_streak": 0}
        try:
            saved = json.loads(STATS_FILE.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                for key in stats:
                    value = saved.get(key)
                    if isinstance(value, int) and not isinstance(value, bool):
                        stats[key] = max(0, value)
        except (OSError, json.JSONDecodeError, TypeError):
            pass
        return stats

    def save_stats(self):
        try:
            temp = STATS_FILE.with_suffix(".tmp")
            temp.write_text(json.dumps(self.stats, indent=2), encoding="utf-8")
            temp.replace(STATS_FILE)
        except OSError:
            self.set_status("Stats could not be saved, but the game can continue.", "gold")

    def panel(self, parent):
        return tk.Frame(parent, bg=C["panel"], highlightbackground=C["line"], highlightthickness=1)

    def build_ui(self):
        header = tk.Frame(self.root, bg=C["bg"])
        header.pack(fill="x", padx=24, pady=(16, 12))
        brand = tk.Frame(header, bg=C["bg"])
        brand.pack(side="left", fill="x", expand=True)
        tk.Label(brand, text="WORD GAME  /  001", bg=C["bg"], fg=C["teal"],
                 font=(FONT, 9, "bold")).pack(anchor="w")
        tk.Label(brand, text="HANGMAN  ARENA", bg=C["bg"], fg=C["text"],
                 font=(FONT, 25, "bold")).pack(anchor="w")
        tk.Label(brand, text="Guess smart. Keep your lives. Beat your best score.",
                 bg=C["bg"], fg=C["muted"], font=(FONT, 10)).pack(anchor="w")
        self.header_stats = tk.Label(header, text="", bg=C["panel"], fg=C["gold"],
                                     font=(FONT, 10, "bold"), padx=14, pady=12,
                                     highlightbackground=C["line"], highlightthickness=1)
        self.header_stats.pack(side="right", padx=(10, 0))

        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=(0, 10))
        body.columnconfigure(0, weight=11, uniform="columns")
        body.columnconfigure(1, weight=12, uniform="columns")
        body.rowconfigure(0, weight=1)
        left, right = self.panel(body), self.panel(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.build_left(left)
        self.build_right(right)

        footer = tk.Frame(self.root, bg=C["bg"])
        footer.pack(fill="x", padx=24, pady=(0, 13))
        tk.Label(footer, text="SHORTCUTS", bg=C["bg"], fg=C["muted"], font=(FONT, 8, "bold")).pack(side="left")
        tk.Label(footer, text="A–Z  guess letter     F1  hint     F2  new game",
                 bg=C["bg"], fg=C["muted"], font=(FONT, 9)).pack(side="left", padx=14)
        tk.Label(footer, text="OFFLINE  •  NO EXTRA PACKAGES",
                 bg=C["bg"], fg=C["teal"], font=(FONT, 8, "bold")).pack(side="right")

    def build_left(self, parent):
        top = tk.Frame(parent, bg=C["panel"])
        top.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(top, text="THE GALLOWS", bg=C["panel"], fg=C["text"],
                 font=(FONT, 11, "bold")).pack(side="left")
        self.lives_label = tk.Label(top, text="", bg=C["panel"], fg=C["green"],
                                    font=(FONT, 10, "bold"))
        self.lives_label.pack(side="right")
        self.canvas = tk.Canvas(parent, bg=C["surface"], highlightthickness=0, height=290)
        self.canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        stats = tk.Frame(parent, bg=C["panel"])
        stats.pack(fill="x", padx=14, pady=(0, 13))
        for i in range(3):
            stats.columnconfigure(i, weight=1)
        self.games_value = self.stat_card(stats, 0, "ROUNDS", "0")
        self.wins_value = self.stat_card(stats, 1, "WINS", "0")
        self.best_value = self.stat_card(stats, 2, "BEST SCORE", "0")

    def stat_card(self, parent, column, title, value):
        box = tk.Frame(parent, bg=C["surface"], padx=8, pady=5)
        box.grid(row=0, column=column, sticky="ew", padx=3)
        tk.Label(box, text=title, bg=C["surface"], fg=C["muted"], font=(FONT, 8, "bold")).pack()
        label = tk.Label(box, text=value, bg=C["surface"], fg=C["text"], font=(FONT, 15, "bold"))
        label.pack()
        return label

    def build_right(self, parent):
        top = tk.Frame(parent, bg=C["panel"])
        top.pack(fill="x", padx=16, pady=(13, 6))
        tk.Label(top, text="WORD PUZZLE", bg=C["panel"], fg=C["text"],
                 font=(FONT, 11, "bold")).pack(side="left")
        self.level_box = ttk.Combobox(top, textvariable=self.difficulty, values=list(LEVELS),
                                      state="readonly", width=10, font=(FONT, 10))
        self.level_box.pack(side="right")
        self.level_box.bind("<<ComboboxSelected>>", self.on_level_change)

        row = tk.Frame(parent, bg=C["panel"])
        row.pack(fill="x", padx=16)
        self.category_label = tk.Label(row, text="", bg=C["teal_dark"], fg=C["teal"],
                                       font=(FONT, 8, "bold"), padx=9, pady=5)
        self.category_label.pack(side="left")
        self.level_label = tk.Label(row, text="", bg=C["panel"], fg=C["muted"], font=(FONT, 8, "bold"))
        self.level_label.pack(side="right")

        self.word_frame = tk.Frame(parent, bg=C["panel"], height=65)
        self.word_frame.pack(fill="x", padx=12, pady=(10, 5))
        self.word_frame.pack_propagate(False)

        clue = tk.Frame(parent, bg=C["surface"], padx=11, pady=7)
        clue.pack(fill="x", padx=16, pady=(0, 7))
        tk.Label(clue, text="CLUE", bg=C["surface"], fg=C["gold"],
                 font=(FONT, 8, "bold")).pack(anchor="w")
        self.clue_label = tk.Label(clue, text="", bg=C["surface"], fg=C["text"],
                                   font=(FONT, 9), justify="left", wraplength=400)
        self.clue_label.pack(anchor="w", fill="x", pady=(2, 0))

        keyboard = tk.Frame(parent, bg=C["panel"])
        keyboard.pack(fill="x", padx=13, pady=(0, 7))
        for col in range(7):
            keyboard.columnconfigure(col, weight=1)
        for index, letter in enumerate(string.ascii_uppercase):
            r, col = divmod(index, 7)
            button = tk.Button(keyboard, text=letter, command=lambda ch=letter.lower(): self.guess(ch),
                               font=(FONT, 10, "bold"), bg=C["key"], fg=C["text"],
                               activebackground=C["teal"], activeforeground=C["bg"],
                               disabledforeground=C["muted"], relief="flat", bd=0, cursor="hand2",
                               takefocus=False, padx=0, pady=6)
            button.grid(row=r, column=col, sticky="ew", padx=2, pady=2)
            button.bind("<Enter>", lambda _e, b=button: self.hover(b, True))
            button.bind("<Leave>", lambda _e, b=button: self.hover(b, False))
            self.buttons[letter.lower()] = button

        self.status_label = tk.Label(parent, text="", bg=C["teal_dark"], fg=C["teal"],
                                     font=(FONT, 9, "bold"), padx=9, pady=7, anchor="w", wraplength=420)
        self.status_label.pack(fill="x", padx=16, pady=(0, 7))
        controls = tk.Frame(parent, bg=C["panel"])
        controls.pack(fill="x", padx=14, pady=(0, 12))
        self.hint_button = tk.Button(controls, text="✦  Hint  [F1]", command=self.hint,
                                    font=(FONT, 9, "bold"), bg=C["teal_dark"], fg=C["teal"],
                                    activebackground=C["teal"], activeforeground=C["bg"],
                                    relief="flat", cursor="hand2", padx=8, pady=8)
        self.hint_button.pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Button(controls, text="↻  New Game  [F2]", command=self.new_game,
                  font=(FONT, 9, "bold"), bg=C["teal"], fg=C["bg"],
                  activebackground="#A6FFF0", relief="flat", cursor="hand2",
                  padx=8, pady=8).pack(side="left", fill="x", expand=True, padx=4)
        tk.Button(controls, text="?  How to Play", command=self.show_help,
                  font=(FONT, 9, "bold"), bg=C["key"], fg=C["text"],
                  activebackground=C["line"], relief="flat", cursor="hand2",
                  padx=8, pady=8).pack(side="left", fill="x", expand=True, padx=(4, 0))

    @staticmethod
    def hover(button, entered):
        try:
            if str(button["state"]) != "disabled":
                button.configure(bg=C["line"] if entered else C["key"])
        except tk.TclError:
            pass

    def draw_scene(self):
        if not hasattr(self, "canvas"):
            return
        canvas = self.canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 320)
        height = max(canvas.winfo_height(), 240)
        for x in range(15, width, 34):
            for y in range(14, height, 31):
                canvas.create_oval(x, y, x + 2, y + 2, fill="#293A50", outline="")
        canvas.create_text(16, 16, text="ARENA VIEW  /  LIVE", anchor="nw",
                           fill=C["muted"], font=(FONT, 8, "bold"))
        base_y = height - 27
        pole_x = int(width * .26)
        beam_y = int(height * .16)
        rope_x = int(width * .70)
        wood = "#8295AF"
        canvas.create_line(pole_x - 32, base_y, pole_x + 96, base_y, fill=wood, width=5, capstyle="round")
        canvas.create_line(pole_x, base_y, pole_x, beam_y, fill=wood, width=5, capstyle="round")
        canvas.create_line(pole_x, beam_y, rope_x, beam_y, fill=wood, width=5, capstyle="round")
        canvas.create_line(rope_x, beam_y, rope_x, beam_y + 30, fill=C["gold"], width=3)
        canvas.create_line(pole_x + 3, beam_y + 48, pole_x + 32, beam_y, fill="#50647F", width=3)
        canvas.create_oval(pole_x - 5, beam_y - 5, pole_x + 5, beam_y + 5, fill=C["teal"], outline="")
        errors = len(self.game.wrong)
        head_y = beam_y + 56
        ink = C["red"] if errors >= 5 else C["teal"]
        if errors >= 1:
            radius = 19
            canvas.create_oval(rope_x-radius, head_y-radius, rope_x+radius, head_y+radius, outline=ink, width=4)
            canvas.create_oval(rope_x-7, head_y-4, rope_x-3, head_y, fill=ink, outline="")
            canvas.create_oval(rope_x+3, head_y-4, rope_x+7, head_y, fill=ink, outline="")
            if self.game.status == "lost":
                canvas.create_line(rope_x-6, head_y+9, rope_x+6, head_y+5, fill=ink, width=2)
            else:
                canvas.create_arc(rope_x-7, head_y+1, rope_x+7, head_y+11, start=200, extent=140, style="arc", outline=ink, width=2)
        body_top, body_bottom = head_y + 20, head_y + 78
        if errors >= 2:
            canvas.create_line(rope_x, body_top, rope_x, body_bottom, fill=ink, width=4, capstyle="round")
        if errors >= 3:
            canvas.create_line(rope_x, body_top+10, rope_x-26, body_top+34, fill=ink, width=4, capstyle="round")
        if errors >= 4:
            canvas.create_line(rope_x, body_top+10, rope_x+26, body_top+34, fill=ink, width=4, capstyle="round")
        if errors >= 5:
            canvas.create_line(rope_x, body_bottom, rope_x-22, body_bottom+30, fill=ink, width=4, capstyle="round")
        if errors >= 6:
            canvas.create_line(rope_x, body_bottom, rope_x+22, body_bottom+30, fill=ink, width=4, capstyle="round")
        canvas.create_text(width-14, height-12, text=f"{errors}/{MAX_WRONG} MISSES",
                           anchor="se", fill=C["muted"], font=(FONT, 8, "bold"))
        if self.game.status == "won":
            canvas.create_text(width/2, height*.75, text="ROUND CLEARED  ✦", fill=C["green"], font=(FONT, 15, "bold"))
        elif self.game.status == "lost":
            canvas.create_text(width/2, height*.75, text="TRY AGAIN  ↻", fill=C["red"], font=(FONT, 15, "bold"))

    def render_word(self):
        for tile in self.tiles:
            tile.destroy()
        self.tiles.clear()
        for letter in self.game.word:
            visible = letter in self.game.correct or self.game.status == "lost"
            text = letter.upper() if visible else "•"
            if letter in self.game.correct:
                bg = C["teal_dark"] if letter == self.game.hint_letter else C["key"]
                fg = C["teal"] if letter == self.game.hint_letter else C["text"]
            elif self.game.status == "lost":
                bg, fg = "#43283A", C["red"]
            else:
                bg, fg = C["surface"], C["muted"]
            tile = tk.Label(self.word_frame, text=text, width=2, bg=bg, fg=fg,
                            font=(FONT, 14, "bold"), padx=1, pady=6,
                            highlightbackground=C["line"], highlightthickness=1)
            tile.pack(side="left", expand=True, padx=2, pady=4)
            self.tiles.append(tile)

    def update_keyboard(self):
        for letter, button in self.buttons.items():
            if letter in self.game.correct:
                bg = C["teal_dark"] if letter == self.game.hint_letter else "#1C4B43"
                fg = C["teal"] if letter == self.game.hint_letter else C["green"]
                button.configure(state="disabled", bg=bg, fg=fg, disabledforeground=fg)
            elif letter in self.game.wrong:
                button.configure(state="disabled", bg="#4B2637", fg=C["red"], disabledforeground=C["red"])
            elif self.game.status != "playing":
                button.configure(state="disabled", bg=C["key"], fg=C["muted"], disabledforeground=C["muted"])
            else:
                button.configure(state="normal", bg=C["key"], fg=C["text"], disabledforeground=C["muted"])

    def set_status(self, message, tone="normal"):
        themes = {
            "normal": (C["teal_dark"], C["teal"]),
            "good": ("#153C35", C["green"]),
            "bad": ("#452536", C["red"]),
            "gold": ("#423922", C["gold"]),
        }
        bg, fg = themes.get(tone, themes["normal"])
        self.status_label.configure(text=message, bg=bg, fg=fg)

    def update_ui(self, message=None, tone="normal"):
        self.category_label.configure(text=f"  {self.game.category.upper()}  ")
        self.level_label.configure(text=f"{self.game.difficulty.upper()}  •  {LEVELS[self.game.difficulty]['label']}")
        self.clue_label.configure(text=self.game.clue)
        self.render_word()
        self.update_keyboard()
        self.lives_label.configure(
            text=" ".join("♥" if i < self.game.lives_left else "·" for i in range(MAX_WRONG)),
            fg=C["green"] if self.game.lives_left > 2 else C["red"])
        self.games_value.configure(text=str(self.stats["games"]))
        self.wins_value.configure(text=str(self.stats["wins"]))
        self.best_value.configure(text=str(self.stats["best"]))
        self.header_stats.configure(text=f"✦  SCORE  {self.stats['points']}   •   BEST STREAK  {self.stats['best_streak']}")
        self.hint_button.configure(state="normal" if self.game.status == "playing" and not self.game.hint_used else "disabled")
        self.draw_scene()
        if message is not None:
            self.set_status(message, tone)

    def guess(self, letter):
        outcome = apply_guess(self.game, letter)
        messages = {
            "invalid": ("Use one letter from A to Z.", "gold"),
            "duplicate": ("That letter has already been used. Try a different one.", "gold"),
            "correct": (f"Nice! {letter.upper()} is in the word.", "good"),
            "wrong": (f"No {letter.upper()} this time. Stay focused!", "bad"),
            "finished": ("This round is over. Start a new game to play again.", "gold"),
            "won": (f"Brilliant! You solved {self.game.word.upper()}  •  +{self.game.score} points", "good"),
            "lost": (f"Out of lives! The word was {self.game.word.upper()}. Try another round?", "bad"),
        }
        if outcome in {"won", "lost"}:
            self.record_round()
        message, tone = messages[outcome]
        self.update_ui(message, tone)

    def hint(self):
        letter = use_hint(self.game)
        if letter is None:
            self.update_ui("No hint left this round, or the round has ended.", "gold")
            return
        if self.game.status == "won":
            self.record_round()
            message, tone = f"The hint revealed {letter.upper()} and completed the word! Score: {self.game.score}", "good"
        else:
            message, tone = f"Hint used: {letter.upper()} is revealed. Your final score loses 5 points.", "gold"
        self.update_ui(message, tone)

    def record_round(self):
        if self.round_recorded:
            return
        self.round_recorded = True
        self.stats["games"] += 1
        if self.game.status == "won":
            self.stats["wins"] += 1
            self.stats["points"] += self.game.score
            self.stats["best"] = max(self.stats["best"], self.game.score)
            self.stats["streak"] += 1
            self.stats["best_streak"] = max(self.stats["best_streak"], self.stats["streak"])
        else:
            self.stats["losses"] += 1
            self.stats["streak"] = 0
        self.save_stats()

    def new_game(self):
        self.game = create_game(self.difficulty.get())
        self.round_recorded = False
        self.update_ui("Fresh word loaded. Choose a letter and chase a new high score!")

    def on_level_change(self, _event=None):
        self.new_game()

    def on_key(self, event):
        key = event.keysym.lower()
        # Reserve F1/F2 for actions so every A-Z key remains available for guessing.
        if len(key) == 1 and key in string.ascii_lowercase:
            self.guess(key)
        elif event.keysym == "F1":
            self.hint()
        elif event.keysym == "F2":
            self.new_game()

    def show_help(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("How to Play | Hangman Arena")
        dialog.configure(bg=C["bg"])
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        panel = tk.Frame(dialog, bg=C["panel"], padx=22, pady=20)
        panel.pack(fill="both", expand=True, padx=12, pady=12)
        tk.Label(panel, text="HOW TO PLAY", bg=C["panel"], fg=C["teal"],
                 font=(FONT, 17, "bold")).pack(anchor="w")
        tips = [
            ("01  Choose a level", "Easy is a warm-up; Medium is a challenge; Hard earns the most points."),
            ("02  Guess letters", "Click A–Z or type on your keyboard. Every incorrect letter costs one life."),
            ("03  Use your clue", "Read the clue below the word. Use one hint to reveal a letter."),
            ("04  Chase points", "More lives remaining earns bonus points. Using a hint costs five points."),
            ("05  Keep your streak", "Win consecutive rounds to build a streak. Best score and stats save locally."),
        ]
        for title, body in tips:
            block = tk.Frame(panel, bg=C["surface"], padx=11, pady=8)
            block.pack(fill="x", pady=4)
            tk.Label(block, text=title, bg=C["surface"], fg=C["gold"],
                     font=(FONT, 10, "bold")).pack(anchor="w")
            tk.Label(block, text=body, bg=C["surface"], fg=C["text"], font=(FONT, 9),
                     wraplength=400, justify="left").pack(anchor="w", pady=(3, 0))
        tk.Button(panel, text="LET'S PLAY", command=dialog.destroy, bg=C["teal"], fg=C["bg"],
                  activebackground="#A6FFF0", relief="flat", padx=18, pady=8,
                  font=(FONT, 10, "bold"), cursor="hand2").pack(anchor="e", pady=(8, 0))


def main():
    root = tk.Tk()
    HangmanArena(root)
    root.mainloop()


if __name__ == "__main__":
    main()
