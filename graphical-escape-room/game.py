from room import ROOMS, ITEMS, PUZZLES

class Game:
    def __init__(self):
        self.inventory = []
        self.current_room_id = "study"
        self.puzzles_solved = {}
        self.taken_objects = set()
        self.used_on = {}
        self.revealed_objects = set()
        self.victory = False
        self.bookshelf_pulled = False

    def get_current_room(self):
        return ROOMS[self.current_room_id]

    def get_object_state(self, obj):
        taken = obj.id in self.taken_objects
        puzzle_solved = obj.puzzle_id and self.puzzles_solved.get(obj.puzzle_id)
        return taken, puzzle_solved

    def get_description(self, obj):
        taken, puzzle_solved = self.get_object_state(obj)
        item_used = obj.id in self.used_on.values()

        if puzzle_solved and obj.puzzle_id in PUZZLES:
            return PUZZLES[obj.puzzle_id]["solved_msg"]
        if taken and obj.after_take_desc:
            return obj.after_take_desc
        if item_used:
            if obj.after_use_desc:
                return obj.after_use_desc
            if obj.puzzle_id:
                puzzle = PUZZLES[obj.puzzle_id]
                if self.puzzles_solved.get(obj.puzzle_id):
                    return puzzle["solved_msg"]
        return obj.desc

    def has_item(self, item_id):
        return item_id in self.inventory

    def take_item(self, obj):
        if obj.take and not obj.id in self.taken_objects:
            self.inventory.append(obj.take)
            self.taken_objects.add(obj.id)
            return True
        return False

    def use_item(self, item_id, obj):
        if item_id == obj.requires and item_id in self.inventory:
            self.inventory.remove(item_id)
            self.used_on[item_id] = obj.id

            combine_to = {
                ("empty_flask", "tap"): "filled_flask",
                ("filled_flask", "shelf"): "saline_flask",
                ("saline_flask", "hotplate"): "crystal",
                ("crystal", "microscope"): None,
                ("uv_light", "certificate"): None,
            }
            key = (item_id, obj.id)
            if key in combine_to:
                result = combine_to[key]
                if result:
                    self.inventory.append(result)
                return True
        return False

    def check_puzzle(self, obj, code):
        puzzle = PUZZLES.get(obj.puzzle_id)
        if not puzzle:
            return False
        if code == puzzle["answer"]:
            self.puzzles_solved[obj.puzzle_id] = True
            reward = puzzle["reward"]
            if reward and reward not in self.inventory:
                self.inventory.append(reward)
            return True
        return False

    def can_exit(self):
        room = self.get_current_room()
        if not room.exit_item:
            return True
        return room.exit_item in self.inventory

    def exit_room(self):
        if not self.can_exit():
            return False
        room = self.get_current_room()
        if room.exit_to == "__victory__":
            self.victory = True
            return True
        if room.exit_to in ROOMS:
            self.current_room_id = room.exit_to
            return True
        return False

    def handle_special(self, obj_id):
        if obj_id == "bookshelf" and not self.bookshelf_pulled:
            self.bookshelf_pulled = True
            if "uv_light" not in self.inventory:
                self.inventory.append("uv_light")
            return True, "You pull the book. A hidden compartment opens, revealing a UV light!"
        return False, ""
