import sys
import json
import requests

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, TEMPERATURE, MAX_TOKENS

def stream_story(messages):
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY.startswith('sk-your'):
        print("\n  ERROR: No valid DeepSeek API key found.")
        print("  Create a .env file in ai-dungeon-master/ with:")
        print("    DEEPSEEK_API_KEY=sk-your-actual-key\n")
        sys.exit(1)

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": True,
    }
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    url = DEEPSEEK_BASE_URL.rstrip('/') + '/chat/completions'
    response = requests.post(url, headers=headers, json=payload, stream=True)
    response.raise_for_status()

    parts = []
    for line in response.iter_lines():
        if not line:
            continue
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data_str = line[6:]
            if data_str.strip() == '[DONE]':
                break
            try:
                chunk = json.loads(data_str)
                choices = chunk.get('choices', [])
                if choices:
                    delta = choices[0].get('delta', {})
                    content = delta.get('content')
                    if content:
                        parts.append(content)
                        print(content, end='', flush=True)
            except json.JSONDecodeError:
                pass
    print()
    return ''.join(parts)
