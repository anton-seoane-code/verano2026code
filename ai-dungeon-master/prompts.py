import json
import re

SYSTEM_PROMPT = """\
You are an AI text adventure game engine set in a fantasy world. \
Generate immersive, atmospheric narrative in 2–3 paragraphs per turn. \
Respond ONLY with valid JSON — no markdown, no commentary outside the JSON block.

Your JSON response must have these fields:
{
  "story": "Your 2–3 paragraph narrative here. Describe the scene, the consequences of the player's action, sensory details, and NPC reactions. Keep the player engaged.",
  "hp": 10,
  "max_hp": 10,
  "inventory": ["item1", "item2"],
  "location": "Current location name",
  "options": ["Option 1: brief description of what this action does", "Option 2: brief description"],
  "game_over": false
}

Rules:
- hp must never exceed max_hp. Reduce hp on dangerous actions or combat.
- inventory is a list of item names the player carries. Add/remove items as the story dictates.
- location is a short name for the current area (e.g. "Dark Forest", "Goblin Cave").
- options should provide 2–4 meaningful choices that follow naturally from the story.
- game_over must be true only when the player dies or the story reaches a definitive end.
- Combat: describe the enemy and the result. The player can fight, flee, or negotiate.
- Items: describe useful items the player finds. The player can pick them up.
- Magic: spells and magical effects are possible. Describe them vividly.
- Keep the world consistent. Refer to past events and items the player has encountered.
- Never break character. You are the game engine, not an assistant.
- Total story output across all turns should feel like a coherent adventure."""

RETRY_PROMPT = """Your previous response was not valid JSON. Respond again with ONLY this exact JSON — no other text, no markdown:
{"story": "your narrative here", "hp": 10, "max_hp": 10, "inventory": [], "location": "location", "options": ["option 1", "option 2"], "game_over": false}
Start with '{"story":'."""

DEFAULTS = {
    'story': 'The adventure continues...',
    'hp': 10,
    'max_hp': 10,
    'inventory': [],
    'location': 'Unknown',
    'options': ['Explore your surroundings', 'Look around'],
    'game_over': False,
}

def _find_json_braces(text):
    start = text.find('{')
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        c = text[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None

def _try_parse(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    cleaned = re.sub(r',\s*}', '}', text)
    cleaned = re.sub(r',\s*\]', ']', cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    return None

def _fill_defaults(data):
    required = ['story', 'hp', 'max_hp', 'inventory', 'location', 'options', 'game_over']
    result = {}
    for field in required:
        val = data.get(field)
        if val is not None:
            result[field] = val
        else:
            result[field] = DEFAULTS[field]
    result['hp'] = max(0, min(int(result['hp']), int(result['max_hp'])))
    result['max_hp'] = int(result['max_hp'])
    if not isinstance(result['inventory'], list):
        result['inventory'] = DEFAULTS['inventory']
    if not isinstance(result['options'], list) or not result['options']:
        result['options'] = DEFAULTS['options']
    if not isinstance(result['game_over'], bool):
        result['game_over'] = False
    return result

def parse_story_response(text):
    text = text.strip()
    if not text:
        return _fill_defaults({})

    code = re.search(r'```(?:json)?\s*\n?([\s\S]*?)```', text)
    if code:
        data = _try_parse(code.group(1).strip())
        if data:
            return _fill_defaults(data)

    block = _find_json_braces(text)
    if block:
        data = _try_parse(block)
        if data:
            return _fill_defaults(data)

    data = _try_parse(text)
    if data:
        return _fill_defaults(data)

    return _fill_defaults({'story': text})
