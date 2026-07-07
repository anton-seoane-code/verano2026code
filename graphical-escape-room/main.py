#!/usr/bin/env python3
import tkinter as tk
from game import Game
from renderer import Renderer

def main():
    root = tk.Tk()
    root.geometry("800x640")
    game = Game()
    renderer = Renderer(root, game)
    root.mainloop()

if __name__ == "__main__":
    main()
