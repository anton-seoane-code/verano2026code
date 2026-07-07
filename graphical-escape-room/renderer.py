import pygame
import pygame.freetype
from room import ITEMS, PUZZLES

W, H = 800, 640
ROOM_H = 470
INV_Y = 475
STATUS_Y = 550

COLORS = {
    "bg": (26, 26, 26),
    "frame": (37, 37, 37),
    "text": (224, 224, 224),
    "accent": (79, 195, 247),
    "success": (102, 187, 106),
    "warning": (255, 167, 38),
    "hover": (60, 60, 60),
    "overlay": (0, 0, 0, 180),
}

class Renderer:
    def __init__(self, game):
        pygame.init()
        pygame.freetype.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Escape Room — Aetheria")
        self.clock = pygame.time.Clock()
        self.game = game
        self.font = pygame.freetype.SysFont("segoeui", 16)
        self.font_bold = pygame.freetype.SysFont("segoeui", 16)
        self.font_bold.strong = True
        self.font_title = pygame.freetype.SysFont("segoeui", 22)
        self.font_title.strong = True
        self.font_small = pygame.freetype.SysFont("segoeui", 13)
        self.font_input = pygame.freetype.SysFont("consolas", 28)

        self.dialog = None
        self.dialog_buttons = []
        self.dialog_input = ""
        self.dialog_input_active = False
        self.hovered_obj = None
        self.status_text = "Click on objects to interact."

        self.refresh()

    def refresh(self):
        pass

    def draw_room(self):
        room = self.game.get_current_room()
        bg = self._hex_color(room.bg_color)
        self.screen.fill(bg, (0, 0, W, ROOM_H))

        floor_y = ROOM_H - 100
        pygame.draw.line(self.screen, (17, 17, 17), (0, floor_y), (W, floor_y), 3)

        for obj in room.objects:
            self._draw_obj(obj)

    def _draw_obj(self, obj):
        taken, solved = self.game.get_object_state(obj)
        color = self._hex_color(obj.color)
        outline = (136, 136, 136)
        if taken or solved:
            outline = COLORS["success"]
        if self.hovered_obj and self.hovered_obj.id == obj.id:
            outline = COLORS["accent"]

        x1, y1, x2, y2 = obj.x, obj.y, obj.x + obj.w, obj.y + obj.h
        rect = (x1, y1, obj.w, obj.h)

        if obj.shape == "oval":
            pygame.draw.ellipse(self.screen, color, rect)
            pygame.draw.ellipse(self.screen, outline, rect, 2)
        else:
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, outline, rect, 2)

        lines = self._wrap_text(obj.name, 100)
        if lines:
            for i, line in enumerate(lines):
                tw, th = self.font.get_rect(line).size
                tx = x1 + (obj.w - tw) // 2
                ty = y1 + (obj.h - th * len(lines)) // 2 + i * th
                self.font.render_to(self.screen, (tx, ty), line, (255, 255, 255))

    def draw_inventory(self):
        pygame.draw.rect(self.screen, COLORS["frame"], (0, INV_Y, W, 75))
        self.font_bold.render_to(self.screen, (12, INV_Y + 6), "Inventory:", COLORS["text"])

        if not self.game.inventory:
            self.font.render_to(self.screen, (100, INV_Y + 8), "(empty)", (136, 136, 136))
        else:
            x = 100
            for item_id in self.game.inventory:
                info = ITEMS.get(item_id, {"name": item_id})
                tw, th = self.font.get_rect(info["name"]).size
                btn_rect = (x, INV_Y + 4, tw + 20, th + 10)
                pygame.draw.rect(self.screen, (55, 71, 79), btn_rect, border_radius=4)
                pygame.draw.rect(self.screen, (84, 110, 122), btn_rect, 1, border_radius=4)
                self.font.render_to(self.screen, (x + 10, INV_Y + 6), info["name"], (255, 255, 255))
                x += tw + 30

    def draw_status(self):
        pygame.draw.rect(self.screen, COLORS["bg"], (0, STATUS_Y, W, H - STATUS_Y))
        lines = self._wrap_text(self.status_text, 760)
        y = STATUS_Y + 10
        for line in lines:
            self.font.render_to(self.screen, (20, y), line, COLORS["text"])
            y += 22

    def draw_room_label(self):
        room = self.game.get_current_room()
        self.font_title.render_to(self.screen, (W // 2 - 80, 8), f"── {room.name} ──", COLORS["accent"])

    def _draw_dialog(self):
        if not self.dialog:
            return
        overlay = pygame.Surface((W, H))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        pw, ph = 460, 320
        px, py = (W - pw) // 2, (H - ph) // 2
        pygame.draw.rect(self.screen, COLORS["bg"], (px, py, pw, ph), border_radius=8)
        pygame.draw.rect(self.screen, (80, 80, 80), (px, py, pw, ph), 2, border_radius=8)

        self.font_title.render_to(self.screen, (px + 20, py + 15), self.dialog["title"], COLORS["accent"])

        desc_y = py + 50
        desc_lines = self._wrap_text(self.dialog["desc"], pw - 40)
        for line in desc_lines:
            self.font.render_to(self.screen, (px + 20, desc_y), line, COLORS["text"])
            desc_y += 22

        if self.dialog_input_active:
            input_rect = (px + 20, desc_y + 5, pw - 40, 40)
            pygame.draw.rect(self.screen, (30, 30, 30), input_rect, border_radius=4)
            pygame.draw.rect(self.screen, COLORS["accent"], input_rect, 2, border_radius=4)
            display_text = self.dialog_input + ("|" if pygame.time.get_ticks() % 1000 < 500 else "")
            self.font_input.render_to(self.screen, (px + 28, desc_y + 8), display_text, COLORS["text"])

        self.dialog_buttons = []
        bx = px + 20
        by = py + ph - 55
        for label, color, hover_color, cb in self.dialog["buttons"]:
            tw, th = self.font_bold.get_rect(label).size
            bw = tw + 24
            bh = th + 12
            mouse = pygame.mouse.get_pos()
            btn_rect = (bx, by, bw, bh)
            is_hover = (bx <= mouse[0] <= bx + bw and by <= mouse[1] <= by + bh)
            btn_color = hover_color if is_hover else color
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=4)
            self.font_bold.render_to(self.screen, (bx + 12, by + 6), label, (255, 255, 255))
            self.dialog_buttons.append((btn_rect, cb))
            bx += bw + 10

    def _wrap_text(self, text, max_width):
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            test = cur + " " + w if cur else w
            tw, _ = self.font.get_rect(test).size
            if tw <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines or [""]

    def _hex_color(self, h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def _get_obj_at(self, pos):
        x, y = pos
        room = self.game.get_current_room()
        for obj in room.objects:
            if obj.x <= x <= obj.x + obj.w and obj.y <= y <= obj.y + obj.h:
                return obj
        return None

    def _get_inv_item_at(self, pos):
        x, y = pos
        if y < INV_Y or y > INV_Y + 75:
            return None
        ix = 100
        for item_id in self.game.inventory:
            info = ITEMS.get(item_id, {"name": item_id})
            tw, th = self.font.get_rect(info["name"]).size
            bw = tw + 20
            if ix <= x <= ix + bw and INV_Y + 4 <= y <= INV_Y + 4 + th + 10:
                return item_id
            ix += bw + 10
        return None

    def handle_click(self, pos):
        if self.dialog:
            for rect, cb in self.dialog_buttons:
                rx, ry, rw, rh = rect
                if rx <= pos[0] <= rx + rw and ry <= pos[1] <= ry + rh:
                    cb()
                    return
            if self.dialog.get("click_outside_close"):
                self.close_dialog()
            return

        obj = self._get_obj_at(pos)
        if obj:
            self._open_obj_dialog(obj)
            return

        item_id = self._get_inv_item_at(pos)
        if item_id:
            self._open_item_dialog(item_id)

    def handle_keydown(self, event):
        if self.dialog_input_active:
            if event.key == pygame.K_RETURN:
                self._submit_code()
            elif event.key == pygame.K_BACKSPACE:
                self.dialog_input = self.dialog_input[:-1]
            elif event.unicode.isprintable() and len(self.dialog_input) < 10:
                if event.unicode.isdigit() or event.unicode.isalpha():
                    self.dialog_input += event.unicode
        elif event.key == pygame.K_ESCAPE and self.dialog:
            self.close_dialog()

    def handle_hover(self, pos):
        self.hovered_obj = self._get_obj_at(pos)
        if self.hovered_obj:
            self.status_text = self.hovered_obj.hint or self.hovered_obj.desc
        else:
            self.status_text = "Click on objects to interact."

    def close_dialog(self):
        self.dialog = None
        self.dialog_buttons = []
        self.dialog_input = ""
        self.dialog_input_active = False

    def _open_item_dialog(self, item_id):
        info = ITEMS.get(item_id, {"name": item_id, "desc": ""})
        self.dialog = {
            "title": info["name"],
            "desc": info.get("desc", ""),
            "buttons": [("Close", (55, 71, 79), (84, 110, 122), self.close_dialog)],
            "click_outside_close": True,
        }
        self.dialog_buttons = []
        self.dialog_input_active = False

    def _open_obj_dialog(self, obj):
        taken, solved = self.game.get_object_state(obj)
        desc = self.game.get_description(obj)
        buttons = []
        cb_close = self.close_dialog

        is_exit = obj.requires and obj.id in ("door", "door_lab", "exit_door")

        if is_exit:
            if self.game.can_exit():
                buttons.append(("Open Door", COLORS["success"], (67, 160, 71), self._do_exit))
            else:
                buttons.append((obj.locked_msg, (55, 71, 79), (55, 71, 79), lambda: None))
        elif obj.puzzle_id and not solved:
            self.dialog_input_active = True
            self.dialog_input = ""
            buttons.append(("Submit", COLORS["accent"], (41, 182, 246), self._submit_code))
        elif obj.take and not taken:
            buttons.append(("Take", COLORS["success"], (67, 160, 71), lambda: self._do_take(obj)))
        elif obj.requires and not solved:
            if self.game.has_item(obj.requires):
                item_name = ITEMS.get(obj.requires, {}).get("name", obj.requires)
                buttons.append((f"Use {item_name}", COLORS["warning"], (251, 140, 0), lambda: self._do_use(obj)))
            else:
                needed = ITEMS.get(obj.requires, {}).get("name", obj.requires)
                buttons.append((f"Need: {needed}", (55, 71, 79), (55, 71, 79), lambda: None))
        elif obj.id == "bookshelf" and not self.game.bookshelf_pulled:
            buttons.append(("Pull the book", (120, 144, 156), (84, 110, 122), lambda: self._do_special(obj)))

        buttons.append(("Close", (55, 71, 79), (84, 110, 122), cb_close))

        self.dialog = {
            "title": obj.name,
            "desc": desc,
            "buttons": buttons,
            "click_outside_close": True,
            "obj": obj,
        }

    def _do_take(self, obj):
        if self.game.take_item(obj):
            self.status_text = f"Took {ITEMS.get(obj.take, {}).get('name', obj.take)}."
            self.close_dialog()

    def _do_use(self, obj):
        if self.game.use_item(obj.requires, obj):
            self.status_text = f"Used {ITEMS.get(obj.requires, {}).get('name', obj.requires)} on {obj.name}."
            self.close_dialog()

    def _do_special(self, obj):
        success, msg = self.game.handle_special(obj.id)
        if success:
            self.status_text = msg
            self.close_dialog()

    def _submit_code(self):
        obj = self.dialog.get("obj") if self.dialog else None
        if not obj or not obj.puzzle_id:
            self.close_dialog()
            return
        if self.game.check_puzzle(obj, self.dialog_input):
            puzzle = PUZZLES[obj.puzzle_id]
            reward_name = ITEMS.get(puzzle["reward"], {}).get("name", puzzle["reward"])
            self.status_text = f"Solved! {puzzle['solved_msg']}"
            self.close_dialog()
        else:
            self.dialog_input = ""
            self.status_text = "Wrong code. Try again."

    def _do_exit(self):
        if self.game.exit_room():
            self.close_dialog()
            if self.game.victory:
                self._show_victory()
            else:
                self.status_text = f"Entered {self.game.get_current_room().name}."

    def _show_victory(self):
        self.dialog = None
        self.screen.fill(COLORS["bg"])
        self.font_title.render_to(self.screen, (W // 2 - 120, 100), "ESCAPED!", COLORS["success"])
        lines = [
            "You have escaped the Aetheria Escape Room!",
            "",
            "The Study  →  The Laboratory  →  The Vault  →  FREEDOM",
            "",
            "All puzzles solved. All rooms conquered.",
        ]
        y = 160
        for line in lines:
            self.font.render_to(self.screen, (W // 2 - 180, y), line, COLORS["text"])
            y += 25

        close_rect = (W // 2 - 50, y + 30, 100, 36)
        pygame.draw.rect(self.screen, COLORS["accent"], close_rect, border_radius=4)
        self.font_bold.render_to(self.screen, (W // 2 - 30, y + 38), "Quit", (0, 0, 0))
        pygame.display.flip()

        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    waiting = False
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    cx, cy = ev.pos
                    rx, ry, rw, rh = close_rect
                    if rx <= cx <= rx + rw and ry <= cy <= ry + rh:
                        waiting = False

    def render(self):
        self.draw_room_label()
        self.draw_room()
        self.draw_inventory()
        self.draw_status()
        if self.dialog:
            self._draw_dialog()
        pygame.display.flip()
        self.clock.tick(30)

def run(game):
    r = Renderer(game)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                r.handle_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                r.handle_hover(event.pos)
            elif event.type == pygame.KEYDOWN:
                r.handle_keydown(event)

        r.render()
    pygame.quit()
