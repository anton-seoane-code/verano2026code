import tkinter as tk
from tkinter import messagebox
import random
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from scoreboard import save_score, show_scoreboard


class RPSApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Rock-Paper-Scissors")
        self.root.resizable(False, False)
        self._center(450, 500)

        self.player_score = 0
        self.ai_score = 0
        self.round = 1
        self.game_over = False
        self.max_score = 2

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
        game_menu.add_command(label="New Game", command=self._new_game)
        game_menu.add_separator()
        game_menu.add_command(label="Scoreboard", command=lambda: show_scoreboard(self.root))
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.quit)

    def _create_widgets(self):
        self.title_label = tk.Label(self.root, text="Rock-Paper-Scissors", font=("Arial", 18, "bold"))
        self.title_label.pack(pady=(15, 5))

        self.score_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.score_label.pack()

        self.round_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.round_label.pack()

        self.choice_frame = tk.Frame(self.root)
        self.choice_frame.pack(pady=20)

        choices = [("Rock 🪨", "r"), ("Paper 📄", "p"), ("Scissors ✂️", "s")]
        for text, val in choices:
            btn = tk.Button(self.choice_frame, text=text, font=("Arial", 14),
                            width=14, height=2,
                            command=lambda v=val: self._play(v))
            btn.pack(pady=5)

        self.result_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.result_label.pack(pady=10)

    def _new_game(self):
        self.player_score = 0
        self.ai_score = 0
        self.round = 1
        self.game_over = False
        self._update_display()
        self.result_label.config(text="Choose your move!")
        self._enable_buttons(True)

    def _enable_buttons(self, enabled):
        state = "normal" if enabled else "disabled"
        for child in self.choice_frame.winfo_children():
            child.config(state=state)

    def _update_display(self):
        self.score_label.config(text=f"You {self.player_score}  -  {self.ai_score} AI")
        self.round_label.config(text=f"Round {self.round} (Best of 3)")

    def _play(self, player_choice):
        if self.game_over:
            return

        ai_choice = random.choice(["r", "p", "s"])
        names = {"r": "Rock", "p": "Paper", "s": "Scissors"}
        beats = {"r": "s", "s": "p", "p": "r"}

        result_str = f"You chose {names[player_choice]} | AI chose {names[ai_choice]}"

        if player_choice == ai_choice:
            result_str += "\nDraw!"
            result = 0
        elif beats[player_choice] == ai_choice:
            result_str += "\nYou win this round!"
            result = 1
            self.player_score += 1
        else:
            result_str += "\nAI wins this round!"
            result = -1
            self.ai_score += 1

        self.result_label.config(text=result_str)
        self.round += 1
        self._update_display()

        if self.player_score >= self.max_score or self.ai_score >= self.max_score:
            self.game_over = True
            self._enable_buttons(False)
            if self.player_score > self.ai_score:
                winner = "Player"
                msg = "You win the game!"
            else:
                winner = "AI"
                msg = "AI wins the game!"
            self.result_label.config(text=f"{result_str}\n\n{msg}")
            save_score("rps", winner, player_score=self.player_score, ai_score=self.ai_score)
            messagebox.showinfo("Game Over", msg, parent=self.root)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    RPSApp().run()
