import json
import os

CONFIG_FILE = "alien_conquer.cfg"

DEFAULT_CONFIG = {
    "num_players": 2,
    "num_aliens": 20,
    "music_volume": 0.7,
    "sfx_volume": 0.7,
}

class Config:
    def __init__(self):
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    loaded = json.load(f)
                    for k in DEFAULT_CONFIG:
                        if k in loaded:
                            self.data[k] = loaded[k]
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.data, f, indent=2)
        except IOError:
            pass

    def get(self, key):
        return self.data.get(key, DEFAULT_CONFIG[key])

    def set(self, key, value):
        self.data[key] = value
