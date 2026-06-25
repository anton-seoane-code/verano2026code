import tkinter as tk
from tkinter import messagebox
import random
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from scoreboard import save_score, show_scoreboard


class TicTacToeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tic-Tac-Toe")
        self.root.resizable(False, False)
        self._center(400, 450)

        self.board = [[" "] * 3 for _ in range(3)]
        self.current_player = "X"
        self.game_mode = "pvp"
        self.game_over = False

        self._create_menu()
        self._create_widgets()
        self.status_label.config(text="Player X's turn (PvP)")
        self._mode_dialog()

    def _center(self, w, h):
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws - w) // 2
        y = (hs - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Game", menu=game_menu)
        game_menu.add_command(label="New Game", command=self._new_game)

        diff_menu = tk.Menu(game_menu, tearoff=0)
        game_menu.add_cascade(label="Difficulty", menu=diff_menu)
        diff_menu.add_command(label="Player vs Player", command=lambda: self._set_mode("pvp"))
        diff_menu.add_command(label="AI - Easy", command=lambda: self._set_mode("easy"))
        diff_menu.add_command(label="AI - Medium", command=lambda: self._set_mode("medium"))
        diff_menu.add_command(label="AI - Hard", command=lambda: self._set_mode("hard"))

        game_menu.add_separator()
        game_menu.add_command(label="Scoreboard", command=lambda: show_scoreboard(self.root))
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.root.quit)

    def _create_widgets(self):
        self.status_label = tk.Label(self.root, text="", font=("Arial", 14))
        self.status_label.pack(pady=(15, 5))

        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.buttons = [[None] * 3 for _ in range(3)]
        for i in range(3):
            for j in range(3):
                btn = tk.Button(
                    self.frame, text="", font=("Arial", 28, "bold"),
                    width=3, height=1,
                    command=lambda r=i, c=j: self._click(r, c),
                )
                btn.grid(row=i, column=j, padx=3, pady=3)
                self.buttons[i][j] = btn

    def _mode_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Mode")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        w, h = 300, 250
        ws, hs = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        dialog.geometry(f"{w}x{h}+{(ws-w)//2}+{(hs-h)//2}")

        tk.Label(dialog, text="Choose Game Mode", font=("Arial", 14, "bold")).pack(pady=(20, 10))

        modes = [("Player vs Player", "pvp"), ("AI - Easy", "easy"),
                 ("AI - Medium", "medium"), ("AI - Hard", "hard")]
        for text, mode in modes:
            tk.Button(dialog, text=text, font=("Arial", 11), width=20,
                      command=lambda m=mode, d=dialog: self._set_mode_from_dialog(m, d)).pack(pady=4)

    def _set_mode_from_dialog(self, mode, dialog):
        self._set_mode(mode)
        dialog.destroy()

    def _set_mode(self, mode):
        self._new_game()
        self.game_mode = mode
        labels = {"pvp": "Player vs Player", "easy": "AI - Easy",
                  "medium": "AI - Medium", "hard": "AI - Hard"}
        self.status_label.config(text=f"Mode: {labels[mode]} | Player X's turn")

    def _new_game(self):
        self.board = [[" "] * 3 for _ in range(3)]
        self.current_player = "X"
        self.game_over = False
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="", state="normal", bg="SystemButtonFace")
        if self.game_mode in ("easy", "medium", "hard"):
            self.status_label.config(text=f"Mode: AI - {self.game_mode.capitalize()} | Your turn (X)")
        else:
            self.status_label.config(text="Player X's turn (PvP)")

    def _click(self, row, col):
        if self.game_over or self.board[row][col] != " ":
            return
        if self.game_mode != "pvp" and self.current_player != "X":
            return

        self._make_move(row, col, self.current_player)

        if not self.game_over and self.game_mode != "pvp":
            self.root.after(300, self._ai_turn)

    def _make_move(self, row, col, player):
        self.board[row][col] = player
        self.buttons[row][col].config(text=player)
        if player == "X":
            self.buttons[row][col].config(fg="blue")
        else:
            self.buttons[row][col].config(fg="red")

        if self._check_winner(player):
            self.game_over = True
            self._disable_all()
            self.status_label.config(text=f"Player {player} wins!")
            save_score("tic_tac_toe", player, difficulty=self.game_mode if self.game_mode != "pvp" else None)
            messagebox.showinfo("Game Over", f"Player {player} wins!", parent=self.root)
            return

        if self._is_draw():
            self.game_over = True
            self._disable_all()
            self.status_label.config(text="Draw!")
            save_score("tic_tac_toe", "Draw", difficulty=self.game_mode if self.game_mode != "pvp" else None)
            messagebox.showinfo("Game Over", "Draw!", parent=self.root)
            return

        self.current_player = "O" if player == "X" else "X"
        if self.game_mode == "pvp":
            self.status_label.config(text=f"Player {self.current_player}'s turn")
        else:
            self.status_label.config(text="Your turn (X)" if self.current_player == "X" else "AI thinking...")

    def _ai_turn(self):
        if self.game_over or self.current_player != "O":
            return
        move = self._ai_move()
        if move:
            self._make_move(move[0], move[1], "O")

    def _ai_move(self):
        empty = [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == " "]
        if not empty:
            return None

        if self.game_mode == "easy":
            return random.choice(empty)

        if self.game_mode == "medium":
            if random.random() < 0.4:
                return random.choice(empty)

        best_val = -float("inf")
        best_move = empty[0]
        for i, j in empty:
            self.board[i][j] = "O"
            val = self._minimax(0, False, -float("inf"), float("inf"))
            self.board[i][j] = " "
            if val > best_val:
                best_val = val
                best_move = (i, j)
        return best_move

    def _minimax(self, depth, is_maximizing, alpha, beta):
        if self._check_winner("O"):
            return 10 - depth
        if self._check_winner("X"):
            return depth - 10
        if self._is_draw():
            return 0

        if is_maximizing:
            best = -float("inf")
            for i, j in self._get_empty():
                self.board[i][j] = "O"
                val = self._minimax(depth + 1, False, alpha, beta)
                self.board[i][j] = " "
                best = max(best, val)
                alpha = max(alpha, val)
                if beta <= alpha:
                    break
            return best
        else:
            best = float("inf")
            for i, j in self._get_empty():
                self.board[i][j] = "X"
                val = self._minimax(depth + 1, True, alpha, beta)
                self.board[i][j] = " "
                best = min(best, val)
                beta = min(beta, val)
                if beta <= alpha:
                    break
            return best

    def _get_empty(self):
        return [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == " "]

    def _check_winner(self, player):
        for i in range(3):
            if all(self.board[i][j] == player for j in range(3)):
                return True
            if all(self.board[j][i] == player for j in range(3)):
                return True
        if all(self.board[i][i] == player for i in range(3)):
            return True
        if all(self.board[i][2 - i] == player for i in range(3)):
            return True
        return False

    def _is_draw(self):
        return all(self.board[i][j] != " " for i in range(3) for j in range(3))

    def _disable_all(self):
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(state="disabled")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    TicTacToeApp().run()
