import json
import os
from collections import deque

from config import CONTEXT_TURNS
from prompts import SYSTEM_PROMPT

SAVE_FILE = os.path.join(os.path.dirname(__file__), 'save.json')

class GameState:
    def __init__(self):
        self.hp = 10
        self.max_hp = 10
        self.inventory = []
        self.location = "Unknown"
        self.game_over = False
        self.history = deque(maxlen=CONTEXT_TURNS)

    def apply_response(self, data):
        self.hp = data['hp']
        self.max_hp = data['max_hp']
        self.inventory = data.get('inventory', [])
        self.location = data.get('location', self.location)
        self.game_over = data.get('game_over', False)

    def add_turn(self, action, response_data):
        self.history.append({'role': 'user', 'content': action})
        story = response_data.get('story', '')
        options = response_data.get('options', [])
        self.history.append({'role': 'assistant', 'content': story, 'options': options})

    def context_messages(self):
        messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        messages.extend(self.history)
        return messages

    def to_dict(self):
        return {
            'hp': self.hp,
            'max_hp': self.max_hp,
            'inventory': self.inventory,
            'location': self.location,
            'game_over': self.game_over,
            'history': list(self.history),
        }

    @classmethod
    def from_dict(cls, d):
        state = cls()
        state.hp = d['hp']
        state.max_hp = d['max_hp']
        state.inventory = d['inventory']
        state.location = d['location']
        state.game_over = d['game_over']
        state.history = deque(d.get('history', []), maxlen=CONTEXT_TURNS)
        return state

    def save(self):
        with open(SAVE_FILE, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls):
        if not os.path.exists(SAVE_FILE):
            return None
        with open(SAVE_FILE) as f:
            return cls.from_dict(json.load(f))

    @classmethod
    def delete_save(cls):
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
