import sys
from openai import OpenAI

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, TEMPERATURE, MAX_TOKENS

client = None

def get_client():
    global client
    if client is None:
        if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY.startswith('sk-your'):
            print("\n  ERROR: No valid DeepSeek API key found.")
            print("  Create a .env file in ai-dungeon-master/ with:")
            print("    DEEPSEEK_API_KEY=sk-your-actual-key\n")
            sys.exit(1)
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return client

def stream_story(messages):
    cl = get_client()
    response = cl.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        stream=True,
    )
    parts = []
    for chunk in response:
        delta = chunk.choices[0].delta if chunk.choices else None
        if delta and delta.content:
            token = delta.content
            parts.append(token)
            print(token, end='', flush=True)
    print()
    return ''.join(parts)
