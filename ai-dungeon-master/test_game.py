"""Quick smoke tests for game state and response parsing — no API calls."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from game_state import GameState, SAVE_FILE
from prompts import parse_story_response, SYSTEM_PROMPT

assert len(SYSTEM_PROMPT) > 100, "System prompt too short"

sample_response = json.dumps({
    "story": "You stand in a dark forest. Moonlight filters through the canopy.",
    "hp": 8,
    "max_hp": 10,
    "inventory": ["torch", "sword"],
    "location": "Dark Forest",
    "options": ["Follow the path north", "Investigate the glowing mushrooms"],
    "game_over": False,
})

parsed = parse_story_response(sample_response)
assert parsed is not None, "Should parse valid JSON"
assert parsed['hp'] == 8
assert parsed['location'] == 'Dark Forest'
assert len(parsed['options']) == 2

parsed_with_markdown = parse_story_response(f"```json\n{sample_response}\n```")
assert parsed_with_markdown is not None, "Should parse JSON from markdown block"

state = GameState()
state.apply_response(parsed)
state.add_turn("look around", parsed)

assert state.hp == 8
assert state.location == 'Dark Forest'
assert "torch" in state.inventory
assert len(state.history) == 2
assert state.history[-1]['role'] == 'assistant'
assert 'options' in state.history[-1]
assert len(state.history[-1]['options']) == 2

saved = state.to_dict()
restored = GameState.from_dict(saved)
assert restored.hp == 8
assert restored.location == 'Dark Forest'
assert len(restored.history) == 2

state.save()
loaded = GameState.load()
assert loaded is not None
assert loaded.hp == 8
GameState.delete_save()
assert not os.path.exists(SAVE_FILE)

print("All tests passed!")
