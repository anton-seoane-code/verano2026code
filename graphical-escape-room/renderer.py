import tkinter as tk
from tkinter import simpledialog
from room import ITEMS

CANVAS_W = 780
CANVAS_H = 460

COLORS = {
    "bg": "#1a1a1a",
    "frame": "#252525",
    "text": "#e0e0e0",
    "accent": "#4fc3f7",
    "success": "#66bb6a",
    "warning": "#ffa726",
}

class Renderer:
    def __init__(self, root, game):
        self.root = root
        self.game = game
        self.root.title("Escape Room — Aetheria")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        self.room_label = tk.Label(
            root, text="", font=("Segoe UI", 16, "bold"),
            bg=COLORS["bg"], fg=COLORS["accent"]
        )
        self.room_label.pack(pady=(10, 2))

        self.canvas = tk.Canvas(
            root, width=CANVAS_W, height=CANVAS_H,
            bg="#333", highlightthickness=0
        )
        self.canvas.pack(pady=5)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_hover)

        self.inv_frame = tk.Frame(root, bg=COLORS["frame"], height=50)
        self.inv_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        self.status_label = tk.Label(
            root, text="Click on objects to interact.",
            font=("Segoe UI", 10), bg=COLORS["bg"], fg=COLORS["text"],
            wraplength=760, justify=tk.LEFT
        )
        self.status_label.pack(pady=(0, 10))

        self.refresh()

    def refresh(self):
        room = self.game.get_current_room()
        self.room_label.config(text=f"── {room.name} ──")
        self.draw_room(room)
        self.draw_inventory()

    def draw_room(self, room):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=room.bg_color, outline="")

        self.canvas.create_line(0, 370, CANVAS_W, 370, fill="#111", width=3)

        for obj in room.objects:
            self.draw_object(obj)

    def draw_object(self, obj):
        taken, puzzle_solved = self.game.get_object_state(obj)

        color = obj.color
        outline = "#888"

        if taken or puzzle_solved:
            outline = COLORS["success"]

        obj_type = "oval" if obj.shape == "oval" else "rect"
        x1, y1, x2, y2 = obj.x, obj.y, obj.x + obj.w, obj.y + obj.h

        if obj_type == "oval":
            self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline=outline,
                                    width=2, tags=(f"obj_{obj.id}",))
        else:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=outline,
                                         width=2, tags=(f"obj_{obj.id}",))

        label_bg = "#000000aa" if obj.shape != "oval" else None
        self.canvas.create_text(
            (x1 + x2) // 2, (y1 + y2) // 2,
            text=obj.name, fill="white",
            font=("Segoe UI", 9, "bold"),
            tags=(f"obj_{obj.id}",)
        )

    def on_canvas_hover(self, event):
        x, y = event.x, event.y
        room = self.game.get_current_room()
        found = False
        for obj in room.objects:
            if obj.x <= x <= obj.x + obj.w and obj.y <= y <= obj.y + obj.h:
                self.status_label.config(text=obj.desc)
                found = True
                break
        if not found:
            self.status_label.config(text="Click on objects to interact.")

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        room = self.game.get_current_room()
        for obj in room.objects:
            if obj.x <= x <= obj.x + obj.w and obj.y <= y <= obj.y + obj.h:
                self.show_obj_dialog(obj)
                return

    def draw_inventory(self):
        for w in self.inv_frame.winfo_children():
            w.destroy()

        tk.Label(self.inv_frame, text="Inventory:",
                 font=("Segoe UI", 10, "bold"),
                 bg=COLORS["frame"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=8)

        if not self.game.inventory:
            tk.Label(self.inv_frame, text="(empty)",
                     font=("Segoe UI", 9), bg=COLORS["frame"],
                     fg="#888").pack(side=tk.LEFT, padx=5)
        else:
            for item_id in self.game.inventory:
                info = ITEMS.get(item_id, {"name": item_id, "desc": ""})
                btn = tk.Button(
                    self.inv_frame, text=info["name"],
                    font=("Segoe UI", 9),
                    bg="#37474f", fg="white",
                    activebackground="#546e7a",
                    relief=tk.RAISED, bd=1,
                    command=lambda i=item_id, inf=info: self.show_item_dialog(i, inf)
                )
                btn.pack(side=tk.LEFT, padx=3, pady=5)

    def show_item_dialog(self, item_id, info):
        win = tk.Toplevel(self.root)
        win.title(info["name"])
        win.configure(bg=COLORS["bg"])
        win.geometry("350x150")
        win.resizable(False, False)

        frame = tk.Frame(win, bg=COLORS["bg"], padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text=info["name"],
                 font=("Segoe UI", 14, "bold"),
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(anchor=tk.W)

        tk.Label(frame, text=info.get("desc", ""),
                 font=("Segoe UI", 11),
                 bg=COLORS["bg"], fg=COLORS["text"],
                 wraplength=300, justify=tk.LEFT).pack(anchor=tk.W, pady=(10, 15))

        tk.Button(frame, text="Close",
                  font=("Segoe UI", 10),
                  bg="#37474f", fg="white",
                  activebackground="#546e7a",
                  command=win.destroy).pack()

    def show_obj_dialog(self, obj):
        taken, puzzle_solved = self.game.get_object_state(obj)
        dialog = tk.Toplevel(self.root)
        dialog.title(obj.name)
        dialog.configure(bg=COLORS["bg"])
        dialog.resizable(False, False)

        frame = tk.Frame(dialog, bg=COLORS["bg"], padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text=obj.name,
                 font=("Segoe UI", 14, "bold"),
                 bg=COLORS["bg"], fg=COLORS["accent"]).pack(anchor=tk.W)

        desc = self.game.get_description(obj)
        desc_label = tk.Label(
            frame, text=desc,
            font=("Segoe UI", 11),
            bg=COLORS["bg"], fg=COLORS["text"],
            wraplength=350, justify=tk.LEFT
        )
        desc_label.pack(anchor=tk.W, pady=(10, 12))

        btn_frame = tk.Frame(frame, bg=COLORS["bg"])
        btn_frame.pack(fill=tk.X)

        self._add_dialog_buttons(btn_frame, obj, dialog, desc_label)

        tk.Button(frame, text="Close",
                  font=("Segoe UI", 10),
                  bg="#37474f", fg="white",
                  activebackground="#546e7a",
                  command=dialog.destroy).pack(pady=(8, 0))

    def _add_dialog_buttons(self, frame, obj, dialog, desc_label):
        room = self.game.get_current_room()
        taken, puzzle_solved = self.game.get_object_state(obj)

        is_exit = obj.requires and obj.id in ("door", "door_lab", "exit_door")

        if is_exit:
            if self.game.can_exit():
                self._make_exit_button(frame, dialog)
            else:
                self._make_locked_label(frame, obj)
            return

        if obj.puzzle_id and not puzzle_solved:
            self._make_code_entry(frame, obj, dialog, desc_label)
            return

        if obj.take and not taken:
            self._make_take_button(frame, obj, dialog)
            return

        if obj.requires and not puzzle_solved:
            if self.game.has_item(obj.requires):
                self._make_use_button(frame, obj, dialog)
            else:
                self._make_needed_label(frame, obj)

        if obj.id == "bookshelf" and not self.game.bookshelf_pulled:
            self._make_special_button(frame, obj, dialog, desc_label)

    def _make_take_button(self, frame, obj, dialog):
        def do_take():
            if self.game.take_item(obj):
                dialog.destroy()
                self.refresh()
                self.status_label.config(text=f"Took {ITEMS.get(obj.take, {}).get('name', obj.take)}.")

        tk.Button(frame, text="Take",
                  font=("Segoe UI", 10, "bold"),
                  bg=COLORS["success"], fg="white",
                  activebackground="#43a047",
                  command=do_take).pack(side=tk.LEFT, padx=(0, 8))

    def _make_use_button(self, frame, obj, dialog):
        item_name = ITEMS.get(obj.requires, {}).get("name", obj.requires)

        def do_use():
            if self.game.use_item(obj.requires, obj):
                dialog.destroy()
                self.refresh()
                self.status_label.config(text=f"Used {item_name} on {obj.name}.")

        tk.Button(frame, text=f"Use {item_name}",
                  font=("Segoe UI", 10, "bold"),
                  bg="#ffa726", fg="#222",
                  activebackground="#fb8c00",
                  command=do_use).pack(side=tk.LEFT, padx=(0, 8))

    def _make_special_button(self, frame, obj, dialog, desc_label):
        def do_special():
            success, msg = self.game.handle_special(obj.id)
            if success:
                desc_label.config(text=msg)
                for child in frame.winfo_children():
                    child.destroy()
                tk.Button(frame, text="Take UV Light",
                          font=("Segoe UI", 10, "bold"),
                          bg=COLORS["success"], fg="white",
                          activebackground="#43a047",
                          command=lambda: self._take_uv(dialog)).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(frame, text="Pull the book",
                  font=("Segoe UI", 10),
                  bg="#78909c", fg="white",
                  activebackground="#546e7a",
                  command=do_special).pack(side=tk.LEFT, padx=(0, 8))

    def _take_uv(self, dialog):
        self.game.inventory.append("uv_light")
        dialog.destroy()
        self.refresh()
        self.status_label.config(text="Took UV Light.")

    def _make_code_entry(self, frame, obj, dialog, desc_label):
        tk.Label(frame, text="Enter code:",
                 font=("Segoe UI", 10),
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(side=tk.LEFT, padx=(0, 5))

        entry = tk.Entry(frame, width=10, font=("Segoe UI", 12),
                         justify=tk.CENTER)
        entry.pack(side=tk.LEFT, padx=(0, 5))
        entry.focus_set()

        def do_submit():
            code = entry.get().strip()
            if self.game.check_puzzle(obj, code):
                dialog.destroy()
                self.refresh()
                puzzle = room.PUZZLES[obj.puzzle_id]
                reward_name = ITEMS.get(puzzle["reward"], {}).get("name", puzzle["reward"])
                self.status_label.config(text=f"Solved! {puzzle['solved_msg']}")
            else:
                entry.delete(0, tk.END)
                self.status_label.config(text="Wrong code. Try again.")

        import room as room
        entry.bind("<Return>", lambda e: do_submit())

        tk.Button(frame, text="Submit",
                  font=("Segoe UI", 10, "bold"),
                  bg=COLORS["accent"], fg="#222",
                  activebackground="#29b6f6",
                  command=do_submit).pack(side=tk.LEFT)

    def _make_exit_button(self, frame, dialog):
        def do_exit():
            if self.game.exit_room():
                dialog.destroy()
                if self.game.victory:
                    self.show_victory()
                else:
                    self.refresh()
                    self.status_label.config(text=f"Entered {self.game.get_current_room().name}.")

        tk.Button(frame, text="Open Door",
                  font=("Segoe UI", 12, "bold"),
                  bg=COLORS["success"], fg="white",
                  activebackground="#43a047",
                  command=do_exit).pack()

    def _make_locked_label(self, frame, obj):
        tk.Label(frame, text=obj.locked_msg,
                 font=("Segoe UI", 10, "italic"),
                 bg=COLORS["bg"], fg=COLORS["warning"]).pack()

    def _make_needed_label(self, frame, obj):
        needed = ITEMS.get(obj.requires, {}).get("name", obj.requires)
        tk.Label(frame, text=f"You need: {needed}",
                 font=("Segoe UI", 10),
                 bg=COLORS["bg"], fg=COLORS["warning"]).pack()

    def show_victory(self):
        for w in self.root.winfo_children():
            w.destroy()

        self.root.geometry("500x400")

        tk.Label(self.root,
                 text="🏆  ESCAPED!  🏆",
                 font=("Segoe UI", 28, "bold"),
                 bg=COLORS["bg"], fg=COLORS["success"]).pack(pady=(40, 10))

        tk.Label(self.root,
                 text="You have escaped the Aetheria Escape Room!\n\n"
                       "The Study    →   The Laboratory   →   The Vault   →   FREEDOM\n\n"
                       "All puzzles solved. All rooms conquered.",
                 font=("Segoe UI", 12),
                 bg=COLORS["bg"], fg=COLORS["text"],
                 justify=tk.CENTER).pack(pady=20)

        tk.Button(self.root, text="Play Again",
                  font=("Segoe UI", 12, "bold"),
                  bg=COLORS["accent"], fg="#222",
                  activebackground="#29b6f6",
                  command=lambda: (
                      self.root.destroy(),
                      __import__("main").main()
                  )).pack(pady=10)

        tk.Button(self.root, text="Quit",
                  font=("Segoe UI", 10),
                  bg="#37474f", fg="white",
                  activebackground="#546e7a",
                  command=self.root.destroy).pack()
