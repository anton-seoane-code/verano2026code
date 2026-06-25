import random

CHOICES = {"r": "Rock", "p": "Paper", "s": "Scissors"}
BEATS = {"r": "s", "s": "p", "p": "r"}
LOSES = {"r": "p", "p": "s", "s": "r"}

def get_user_choice():
    while True:
        inp = input("(r)ock, (p)aper, (s)cissors: ").strip().lower()
        if inp in CHOICES:
            return inp
        print("Invalid choice. Enter r, p, or s.")

def determine_round(a, b):
    if a == b:
        return 0
    if BEATS[a] == b:
        return 1
    return -1

def play():
    print("=== ROCK PAPER SCISSORS ===")
    print("Best of 3 wins the game.\n")
    player_score = 0
    ai_score = 0
    draws = 0
    round_num = 1

    while player_score < 2 and ai_score < 2:
        print(f"--- Round {round_num} ---")
        print(f"Score: You {player_score} - {ai_score} AI (Draws: {draws})")
        player = get_user_choice()
        ai = random.choice(list(CHOICES.keys()))
        print(f"You chose {CHOICES[player]}, AI chose {CHOICES[ai]}")

        result = determine_round(player, ai)
        if result == 1:
            print("You win this round!\n")
            player_score += 1
        elif result == -1:
            print("AI wins this round!\n")
            ai_score += 1
        else:
            print("Draw!\n")
            draws += 1
        round_num += 1

    print("=== GAME OVER ===")
    print(f"Final: You {player_score} - {ai_score} AI (Draws: {draws})")
    if player_score > ai_score:
        print("You win the game!")
    else:
        print("AI wins the game!")

if __name__ == "__main__":
    play()
