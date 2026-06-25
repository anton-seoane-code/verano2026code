import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk

DATA_FILE = os.path.join(os.path.dirname(__file__), "scores.json")

def load_scores():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"tic_tac_toe": [], "hangman": [], "rps": []}

def save_scores(scores):
    with open(DATA_FILE, "w") as f:
        json.dump(scores, f, indent=2)

def save_score(game, winner, difficulty=None, guesses=None, player_score=None, ai_score=None):
    scores = load_scores()
    entry = {"winner": winner, "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
    if difficulty:
        entry["difficulty"] = difficulty
    if guesses is not None:
        entry["guesses"] = guesses
    if player_score is not None:
        entry["player_score"] = player_score
    if ai_score is not None:
        entry["ai_score"] = ai_score
    if game in scores:
        scores[game].append(entry)
    save_scores(scores)

def show_scoreboard(parent):
    win = tk.Toplevel(parent)
    win.title("Scoreboard")
    win.geometry("750x420")
    win.resizable(False, False)
    win.transient(parent)
    win.grab_set()

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    configs = [
        ("tic_tac_toe", "Tic-Tac-Toe", ("winner", "date", "difficulty")),
        ("hangman", "Hangman", ("winner", "date", "guesses")),
        ("rps", "Rock-Paper-Scissors", ("winner", "date", "score")),
    ]

    for key, label, columns in configs:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=label)

        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        headings = {"winner": "Winner", "date": "Date", "difficulty": "Difficulty",
                     "guesses": "Wrong Guesses", "score": "Score"}
        widths = {"winner": 100, "date": 160, "difficulty": 120, "guesses": 120, "score": 150}

        for col in columns:
            tree.heading(col, text=headings.get(col, col))
            tree.column(col, width=widths.get(col, 100))

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        scores = load_scores().get(key, [])
        for entry in reversed(scores):
            if key == "tic_tac_toe":
                vals = (entry["winner"], entry["date"], entry.get("difficulty", "-"))
            elif key == "hangman":
                vals = (entry["winner"], entry["date"], str(entry.get("guesses", "-")))
            else:
                ps = entry.get("player_score", 0)
                ai = entry.get("ai_score", 0)
                vals = (entry["winner"], entry["date"], f"{ps} - {ai}")
            tree.insert("", "end", values=vals)
