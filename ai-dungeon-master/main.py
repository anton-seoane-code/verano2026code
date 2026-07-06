#!/usr/bin/env python3
import os

from game_state import GameState, SAVE_FILE
from ai_client import stream_story
from prompts import parse_story_response

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'
CLEAR = '\033[2J\033[H'

TITLE = f"""\
{CYAN}{BOLD}
  ╔══════════════════════════════════╗
  ║                                  ║
  ║     AI DUNGEON MASTER            ║
  ║     A Text Adventure             ║
  ║     Powered by DeepSeek          ║
  ║                                  ║
  ╚══════════════════════════════════╝{RESET}
"""

def hp_bar(current, maximum, width=20):
    filled = int(width * current / maximum) if maximum > 0 else 0
    bar = '█' * filled + '░' * (width - filled)
    color = GREEN if current > maximum * 0.5 else YELLOW if current > maximum * 0.25 else RED
    return f"HP: {color}{bar}{RESET} {current}/{maximum}"

def show_status(state):
    print(f"\n{BOLD}Location:{RESET} {state.location}")
    print(hp_bar(state.hp, state.max_hp))
    if state.inventory:
        print(f"{BOLD}Inventory:{RESET} " + ", ".join(state.inventory))

def show_options(options):
    print(f"\n{BOLD}What do you do?{RESET}")
    for i, opt in enumerate(options, 1):
        print(f"  {YELLOW}{i}{RESET}. {opt}")

def get_input(options):
    while True:
        try:
            text = input(f"\n{CYAN}> {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if not text:
            continue
        if text.isdigit():
            idx = int(text) - 1
            if 0 <= idx < len(options):
                return options[idx]
        return text

def ask_api(messages):
    try:
        return stream_story(messages)
    except Exception as e:
        print(f"\n{RED}The magical connection falters: {e}{RESET}")
        return None

def new_game():
    state = GameState()
    print(f"{CLEAR}{TITLE}")
    print("The DM is consulting the ancient tomes...\n")
    messages = state.context_messages()
    messages.append({'role': 'user', 'content': "Begin the adventure. Describe where I am and what I see."})
    raw = ask_api(messages)
    if raw is None:
        return None
    data = parse_story_response(raw)
    if data is None:
        print(f"\n{RED}Failed to parse the DM's response. The ancient magic falters...{RESET}")
        return None
    state.apply_response(data)
    state.add_turn("Begin the adventure. Describe where I am and what I see.", data)
    state.save()
    return state

def continue_game():
    return GameState.load()

def game_loop(state):
    while not state.game_over:
        show_status(state)
        options = state.history[-1].get('options', []) if state.history else []
        show_options(options)
        action = get_input(options)
        if action is None:
            print(f"\n{YELLOW}Game saved. Farewell, adventurer.{RESET}")
            state.save()
            return
        print(f"\n{BOLD}You:{RESET} {action}\n")
        messages = state.context_messages()
        messages.append({'role': 'user', 'content': action})
        raw = ask_api(messages)
        if raw is None:
            continue
        data = parse_story_response(raw)
        if data is None:
            print(f"\n{RED}The DM's words are incoherent. Let's try again...{RESET}")
            continue
        state.apply_response(data)
        state.add_turn(action, data)
        state.save()
    show_status(state)
    print(f"\n{RED}{BOLD}╔══════════════════════════╗{RESET}")
    print(f"{RED}{BOLD}║     GAME OVER            ║{RESET}")
    print(f"{RED}{BOLD}╚══════════════════════════╝{RESET}")
    print(f"\nYour adventure has ended. Final score: {state.hp * 10 + len(state.inventory) * 5}")
    GameState.delete_save()

def check_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        print(f"{CLEAR}{TITLE}")
        print(f"{YELLOW}No .env file found.{RESET}")
        print("AI Dungeon Master needs a DeepSeek API key to run.")
        key = input(f"\nPaste your DeepSeek API key: ").strip()
        if not key:
            print(f"\n{RED}No key provided. Exiting.{RESET}")
            return False
        with open(env_path, 'w') as f:
            f.write(f"DEEPSEEK_API_KEY={key}\n")
        print(f"\n{GREEN}Saved to .env. Starting the game...{RESET}\n")
        os.environ['DEEPSEEK_API_KEY'] = key
    return True

def main():
    if not check_env():
        return
    while True:
        print(f"{CLEAR}{TITLE}")
        has_save = os.path.exists(SAVE_FILE)
        print(f"  {BOLD}1.{RESET} New Game")
        if has_save:
            print(f"  {BOLD}2.{RESET} Continue")
        print(f"  {BOLD}q.{RESET} Quit")
        choice = input(f"\n{CYAN}> {RESET}").strip().lower()
        if choice == '1' or (choice == '2' and not has_save) or choice == 'new':
            state = new_game()
            if state:
                game_loop(state)
        elif (choice == '2' or choice == 'continue') and has_save:
            state = continue_game()
            if state:
                game_loop(state)
        elif choice in ('q', 'quit', 'exit'):
            print(f"\n{YELLOW}Until next time, adventurer.{RESET}")
            break

if __name__ == '__main__':
    main()
