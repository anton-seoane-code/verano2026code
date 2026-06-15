import curses
import random
import time

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    sh, sw = stdscr.getmaxyx()
    game_h, game_w = sh - 2, sw - 2

    snake = [(game_h // 2, game_w // 2)]
    direction = (0, 1)

    food = (random.randint(0, game_h - 1), random.randint(0, game_w - 1))
    score = 0

    while True:
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == curses.KEY_UP and direction != (1, 0):
            direction = (-1, 0)
        elif key == curses.KEY_DOWN and direction != (-1, 0):
            direction = (1, 0)
        elif key == curses.KEY_LEFT and direction != (0, 1):
            direction = (0, -1)
        elif key == curses.KEY_RIGHT and direction != (0, -1):
            direction = (0, 1)

        head = snake[0]
        new_head = (head[0] + direction[0], head[1] + direction[1])

        if (new_head[0] < 0 or new_head[0] >= game_h or
            new_head[1] < 0 or new_head[1] >= game_w or
            new_head in snake):
            break

        snake.insert(0, new_head)

        if new_head == food:
            score += 1
            while True:
                food = (random.randint(0, game_h - 1), random.randint(0, game_w - 1))
                if food not in snake:
                    break
        else:
            snake.pop()

        stdscr.clear()
        stdscr.addstr(0, 0, f"Score: {score}")
        for y in range(game_h):
            for x in range(game_w):
                if y == 0 or y == game_h - 1 or x == 0 or x == game_w - 1:
                    stdscr.addch(y + 1, x, '#')
        for sy, sx in snake:
            stdscr.addch(sy + 1, sx, 'o')
        stdscr.addch(food[0] + 1, food[1], '*')

    stdscr.clear()
    stdscr.addstr(sh // 2, sw // 2 - 5, f"Game Over! Score: {score}")
    stdscr.addstr(sh // 2 + 1, sw // 2 - 10, "Press any key to exit...")
    stdscr.nodelay(0)
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
