import tkinter as tk
from tkinter import messagebox
import random
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from scoreboard import save_score, show_scoreboard


def load_words():
    path = os.path.join(os.path.dirname(__file__), "words.txt")
    try:
        with open(path) as f:
            return [w.strip().lower() for w in f if w.strip()]
    except FileNotFoundError:
        return ["python", "programming", "computer", "algorithm", "database"]


class HangmanApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hangman")
        self.root.resizable(False, False)
        self._center(550, 650)

        self.words = load_words()
        self.word = ""
        self.guessed = set()
        self.wrong = 0
        self.max_wrong = 6
        self.game_over = False

        self._create_menu()
        self._create_widgets()
        self._new_game()

    def _center(self, w, h):
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(ws-w)//2}+{(hs-h)//2}")

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Word", command=self._new_game)
        game_menu.add_separator()
        game_menu.add_command(label="Scoreboard", command=lambda: show_scoreboard(self.root))
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.quit)

    def _create_widgets(self):
        self.canvas = tk.Canvas(self.root, width=300, height=250, bg="white")
        self.canvas.pack(pady=(15, 5))

        self.word_label = tk.Label(self.root, text="", font=("Courier", 28, "bold"))
        self.word_label.pack(pady=10)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.status_label.pack()

        self.letters_frame = tk.Frame(self.root)
        self.letters_frame.pack(pady=15)

        self.letter_buttons = {}
        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for ri, row in enumerate(rows):
            f = tk.Frame(self.letters_frame)
            f.pack()
            for ch in row:
                btn = tk.Button(f, text=ch, font=("Arial", 11, "bold"),
                                width=3, height=1,
                                command=lambda c=ch: self._guess(c))
                btn.pack(side="left", padx=1, pady=1)
                self.letter_buttons[ch] = btn

    def _draw_gallow(self):
        self.canvas.delete("all")
        w, h = 300, 250
        cx, cy = 80, 200

        self.canvas.create_line(50, 230, 150, 230, width=3)
        self.canvas.create_line(100, 230, 100, 30, width=3)
        self.canvas.create_line(100, 30, 200, 30, width=3)
        self.canvas.create_line(200, 30, 200, 60, width=2)

        if self.wrong > 0:
            self.canvas.create_oval(185, 60, 215, 90, width=2)
        if self.wrong > 1:
            self.canvas.create_line(200, 90, 200, 140, width=2)
        if self.wrong > 2:
            self.canvas.create_line(200, 100, 175, 120, width=2)
        if self.wrong > 3:
            self.canvas.create_line(200, 100, 225, 120, width=2)
        if self.wrong > 4:
            self.canvas.create_line(200, 140, 175, 170, width=2)
        if self.wrong > 5:
            self.canvas.create_line(200, 140, 225, 170, width=2)

    def _new_game(self):
        self.word = random.choice(self.words)
        self.guessed = set()
        self.wrong = 0
        self.game_over = False
        self._draw_gallow()
        self._update_display()
        self.status_label.config(text=f"Word has {len(self.word)} letters")
        for btn in self.letter_buttons.values():
            btn.config(state="normal", bg="SystemButtonFace")

    def _update_display(self):
        display = " ".join(c if c in self.guessed else "_" for c in self.word)
        self.word_label.config(text=display)

    def _guess(self, letter):
        if self.game_over:
            return
        if letter in self.guessed:
            return

        self.guessed.add(letter)
        self.letter_buttons[letter].config(state="disabled")

        if letter in self.word:
            self.letter_buttons[letter].config(bg="lightgreen")
            self._update_display()
            if all(c in self.guessed for c in self.word):
                self.game_over = True
                self.status_label.config(text=f"You win! The word was '{self.word}'")
                save_score("hangman", "Player", guesses=self.wrong)
                messagebox.showinfo("Game Over", f"You win!\nThe word was '{self.word}'", parent=self.root)
        else:
            self.wrong += 1
            self.letter_buttons[letter].config(bg="lightcoral")
            self._draw_gallow()
            self.status_label.config(text=f"Wrong! {self.wrong}/{self.max_wrong}")
            if self.wrong >= self.max_wrong:
                self.game_over = True
                self._disable_all()
                self.word_label.config(text=" ".join(self.word))
                self.status_label.config(text=f"You lose! The word was '{self.word}'")
                save_score("hangman", "AI", guesses=self.wrong)
                messagebox.showinfo("Game Over", f"You lose!\nThe word was '{self.word}'", parent=self.root)

    def _disable_all(self):
        for btn in self.letter_buttons.values():
            btn.config(state="disabled")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    HangmanApp().run()
