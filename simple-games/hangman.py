import random
import sys

STAGES = [
    """
       ------
       |    |
       |
       |
       |
       |
    --------""",
    """
       ------
       |    |
       |    O
       |
       |
       |
    --------""",
    """
       ------
       |    |
       |    O
       |    |
       |
       |
    --------""",
    """
       ------
       |    |
       |    O
       |   /|
       |
       |
    --------""",
    """
       ------
       |    |
       |    O
       |   /|\\\\
       |
       |
    --------""",
    """
       ------
       |    |
       |    O
       |   /|\\\\
       |   /
       |
    --------""",
    """
       ------
       |    |
       |    O
       |   /|\\\\
       |   / \\\\
       |
    --------""",
]

def load_words():
    try:
        with open("words.txt") as f:
            return [w.strip().lower() for w in f if w.strip()]
    except FileNotFoundError:
        return ["python", "programming", "computer", "algorithm", "database"]

def display(word, guessed):
    return " ".join(c if c in guessed else "_" for c in word)

def play():
    words = load_words()
    word = random.choice(words)
    guessed = set()
    wrong = 0
    max_wrong = len(STAGES) - 1

    print("=== HANGMAN ===")
    print(f"The word has {len(word)} letters.\n")

    while wrong < max_wrong:
        print(STAGES[wrong])
        print()
        print(display(word, guessed))
        print()

        guess = input("Guess a letter: ").strip().lower()
        if len(guess) != 1 or not guess.isalpha():
            print("Enter a single letter.")
            continue
        if guess in guessed:
            print("Already guessed that letter.")
            continue

        guessed.add(guess)

        if guess in word:
            print(f"Good! '{guess}' is in the word.\n")
            if all(c in guessed for c in word):
                print(STAGES[wrong])
                print(display(word, guessed))
                print(f"\nYou win! The word was '{word}'.")
                return
        else:
            wrong += 1
            print(f"Wrong! '{guess}' is not in the word.\n")

    print(STAGES[wrong])
    print(display(word, guessed))
    print(f"\nYou lose! The word was '{word}'.")

if __name__ == "__main__":
    play()
