import sys
import random

def print_board(board):
    print("  0   1   2")
    for i, row in enumerate(board):
        print(i, " | ".join(row))
        if i < 2:
            print("  ---+---+---")

def check_winner(board, player):
    for i in range(3):
        if all(board[i][j] == player for j in range(3)):
            return True
        if all(board[j][i] == player for j in range(3)):
            return True
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2 - i] == player for i in range(3)):
        return True
    return False

def is_draw(board):
    return all(board[i][j] != " " for i in range(3) for j in range(3))

def get_empty_cells(board):
    return [(i, j) for i in range(3) for j in range(3) if board[i][j] == " "]

def minimax(board, depth, is_maximizing, alpha, beta):
    if check_winner(board, "O"):
        return 10 - depth
    if check_winner(board, "X"):
        return depth - 10
    if is_draw(board):
        return 0

    if is_maximizing:
        best = -float("inf")
        for i, j in get_empty_cells(board):
            board[i][j] = "O"
            val = minimax(board, depth + 1, False, alpha, beta)
            board[i][j] = " "
            best = max(best, val)
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return best
    else:
        best = float("inf")
        for i, j in get_empty_cells(board):
            board[i][j] = "X"
            val = minimax(board, depth + 1, True, alpha, beta)
            board[i][j] = " "
            best = min(best, val)
            beta = min(beta, val)
            if beta <= alpha:
                break
        return best

def ai_move(board, difficulty):
    empty = get_empty_cells(board)
    if difficulty == "easy":
        return random.choice(empty)

    if difficulty == "medium":
        if random.random() < 0.4:
            return random.choice(empty)

    best_val = -float("inf")
    best_move = empty[0]
    for i, j in empty:
        board[i][j] = "O"
        val = minimax(board, 0, False, -float("inf"), float("inf"))
        board[i][j] = " "
        if val > best_val:
            best_val = val
            best_move = (i, j)
    return best_move

def player_vs_player():
    board = [[" "] * 3 for _ in range(3)]
    players = ["X", "O"]
    turn = 0
    while True:
        print_board(board)
        player = players[turn % 2]
        print(f"Player {player}'s turn")
        try:
            row = int(input("Row (0-2): "))
            col = int(input("Col (0-2): "))
        except ValueError:
            print("Invalid input. Enter numbers 0-2.")
            continue
        if row not in range(3) or col not in range(3) or board[row][col] != " ":
            print("Invalid move. Try again.")
            continue
        board[row][col] = player
        if check_winner(board, player):
            print_board(board)
            print(f"Player {player} wins!")
            return
        if is_draw(board):
            print_board(board)
            print("Draw!")
            return
        turn += 1

def player_vs_ai():
    board = [[" "] * 3 for _ in range(3)]
    print("Difficulty: easy / medium / hard")
    diff = input("Choose: ").strip().lower()
    if diff not in ("easy", "medium", "hard"):
        diff = "hard"
    print("You are X, AI is O")

    while True:
        print_board(board)
        print("Your turn (X)")
        try:
            row = int(input("Row (0-2): "))
            col = int(input("Col (0-2): "))
        except ValueError:
            print("Invalid input. Enter numbers 0-2.")
            continue
        if row not in range(3) or col not in range(3) or board[row][col] != " ":
            print("Invalid move. Try again.")
            continue
        board[row][col] = "X"
        if check_winner(board, "X"):
            print_board(board)
            print("You win!")
            return
        if is_draw(board):
            print_board(board)
            print("Draw!")
            return

        print("AI thinking...")
        i, j = ai_move(board, diff)
        board[i][j] = "O"
        if check_winner(board, "O"):
            print_board(board)
            print("AI wins!")
            return
        if is_draw(board):
            print_board(board)
            print("Draw!")
            return

def main():
    print("=== TIC-TAC-TOE ===")
    print("1. Player vs Player")
    print("2. Player vs AI")
    choice = input("Choose mode (1/2): ").strip()
    if choice == "1":
        player_vs_player()
    else:
        player_vs_ai()

if __name__ == "__main__":
    main()
