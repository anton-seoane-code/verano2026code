from dataclasses import dataclass, field

@dataclass
class GameObject:
    id: str
    name: str
    x: int
    y: int
    w: int
    h: int
    color: str
    desc: str
    shape: str = "rect"
    take: str = ""
    puzzle_id: str = ""
    requires: str = ""
    hint: str = ""
    after_take_desc: str = ""
    after_use_desc: str = ""
    locked_msg: str = ""
    hidden: bool = False

@dataclass
class Room:
    id: str
    name: str
    bg_color: str
    objects: list = field(default_factory=list)
    exit_to: str = ""
    exit_item: str = ""
    exit_locked: str = "The door is locked."

ROOMS = {
    "study": Room(
        id="study",
        name="The Study",
        bg_color="#3e2723",
        objects=[
            GameObject(
                id="desk", name="Desk",
                x=80, y=280, w=200, h=140,
                color="#5d4037", shape="rect",
                desc="An old oak desk. A handwritten note lies on top.",
                take="note",
                after_take_desc="The desk is clear now.",
                hint="The note might contain something useful.",
            ),
            GameObject(
                id="painting", name="Painting",
                x=300, y=60, w=180, h=140,
                color="#c62828", shape="rect",
                desc="A portrait of a stern-looking man. The brass nameplate reads: 'Lord Ashwick, 1847'.",
                hint="The date '1847' is engraved on the nameplate.",
            ),
            GameObject(
                id="safe", name="Wall Safe",
                x=550, y=90, w=90, h=80,
                color="#616161", shape="rect",
                desc="A heavy steel safe with a 4-digit combination dial.",
                puzzle_id="safe_study",
                hint="You need to find a 4-digit code.",
            ),
            GameObject(
                id="door", name="Door",
                x=660, y=180, w=70, h=200,
                color="#4e342e", shape="rect",
                desc="A heavy oak door with a keyhole.",
                requires="brass_key",
                locked_msg="The door is locked. You need a brass key.",
            ),
        ],
        exit_to="lab",
        exit_item="brass_key",
        exit_locked="The door is locked. You need a brass key.",
    ),
    "lab": Room(
        id="lab",
        name="The Laboratory",
        bg_color="#263238",
        objects=[
            GameObject(
                id="cabinet", name="Cabinet",
                x=40, y=200, w=140, h=200,
                color="#37474f", shape="rect",
                desc="A metal supply cabinet. A glass flask sits on the shelf.",
                take="empty_flask",
                after_take_desc="The cabinet is empty.",
                hint="There's a flask inside.",
            ),
            GameObject(
                id="tap", name="Water Tap",
                x=220, y=260, w=60, h=80,
                color="#90a4ae", shape="rect",
                desc="A metal faucet over a small sink. It drips slowly.",
                requires="empty_flask",
                after_use_desc="You filled the flask with water.",
                hint="You could fill something here.",
            ),
            GameObject(
                id="shelf", name="Shelf",
                x=320, y=100, w=130, h=150,
                color="#4e342e", shape="rect",
                desc="A wooden shelf with jars and bottles. A salt packet catches your eye.",
                requires="filled_flask",
                after_use_desc="You added salt to the water. Now you have a saline solution.",
                hint="Salt might be useful for a chemical reaction.",
            ),
            GameObject(
                id="hotplate", name="Heating Plate",
                x=500, y=270, w=100, h=60,
                color="#bf360c", shape="rect",
                desc="An electric heating plate. It's warm to the touch.",
                requires="saline_flask",
                after_use_desc="You heat the saline solution. Crystals begin to form!",
                hint="Heating the solution might produce something.",
            ),
            GameObject(
                id="microscope", name="Microscope",
                x=350, y=260, w=120, h=110,
                color="#455a64", shape="rect",
                desc="An old brass microscope. There's a slide plate.",
                requires="crystal",
                after_use_desc="You place the crystal on the slide. Through the lens, you see numbers etched inside: CODE 582",
                hint="Examine something under the microscope.",
            ),
            GameObject(
                id="drawer", name="Locked Drawer",
                x=420, y=300, w=80, h=60,
                color="#6d4c41", shape="rect",
                desc="A small drawer with a 3-digit combination lock.",
                puzzle_id="drawer_lab",
                hint="You need a 3-digit code.",
            ),
            GameObject(
                id="door_lab", name="Door",
                x=660, y=180, w=70, h=200,
                color="#37474f", shape="rect",
                desc="A reinforced steel door with a card reader.",
                requires="keycard",
                locked_msg="The door needs a keycard to open.",
            ),
        ],
        exit_to="vault",
        exit_item="keycard",
        exit_locked="The door needs a keycard to open.",
    ),
    "vault": Room(
        id="vault",
        name="The Vault",
        bg_color="#1a1a1a",
        objects=[
            GameObject(
                id="bookshelf", name="Bookshelf",
                x=40, y=80, w=140, h=280,
                color="#3e2723", shape="rect",
                desc="A tall bookshelf. One book titled 'The Founding of Aetheria' sticks out slightly.",
                hint="Try pulling the book that sticks out.",
            ),
            GameObject(
                id="certificate", name="Certificate",
                x=280, y=40, w=160, h=100,
                color="#d4a574", shape="rect",
                desc="A framed founding charter dated 1847. The ink is faded but the seal is intact.",
                requires="uv_light",
                after_use_desc="Under UV light, hidden text appears: 'The vault opens for the worthy. CODE: 1847'",
                hint="Maybe a special light would reveal more.",
            ),
            GameObject(
                id="safe_vault", name="Wall Safe",
                x=300, y=170, w=120, h=100,
                color="#616161", shape="rect",
                desc="A large wall safe with a 4-digit combination dial.",
                puzzle_id="safe_vault",
                hint="You need a 4-digit code.",
            ),
            GameObject(
                id="exit_door", name="Vault Door",
                x=660, y=120, w=80, h=280,
                color="#424242", shape="rect",
                desc="A massive steel vault door with a heavy locking mechanism.",
                requires="vault_key",
                locked_msg="The vault door is sealed tight. You need the vault key.",
            ),
        ],
        exit_to="__victory__",
        exit_item="vault_key",
        exit_locked="The vault door is sealed tight. You need the vault key.",
    ),
}

ITEMS = {
    "note": {"name": "Note", "desc": "A handwritten note: 'The code is 4392.'"},
    "brass_key": {"name": "Brass Key", "desc": "An old brass key, worn smooth with age."},
    "empty_flask": {"name": "Empty Flask", "desc": "A clean glass flask."},
    "filled_flask": {"name": "Filled Flask", "desc": "A flask filled with clear water."},
    "salt_packet": {"name": "Salt Packet", "desc": "A small paper packet of salt."},
    "saline_flask": {"name": "Saline Flask", "desc": "A flask filled with salt water."},
    "crystal": {"name": "Crystal", "desc": "A small, clear crystal with a faint inner glow."},
    "keycard": {"name": "Keycard", "desc": "A white keycard with a magnetic strip."},
    "uv_light": {"name": "UV Light", "desc": "A small ultraviolet flashlight."},
    "vault_key": {"name": "Vault Key", "desc": "A heavy iron key with an ornate bow."},
}

PUZZLES = {
    "safe_study": {"answer": "4392", "reward": "brass_key", "solved_msg": "The safe clicks open! Inside is a brass key."},
    "drawer_lab": {"answer": "582", "reward": "keycard", "solved_msg": "The drawer slides open. Inside is a keycard."},
    "safe_vault": {"answer": "1847", "reward": "vault_key", "solved_msg": "The safe swings open with a heavy clunk. You grab the vault key."},
}
