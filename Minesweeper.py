import pygame
import random

n_mines = int(input("How many mines?\n >>"))
n_mines = max(40, min(n_mines, 80))  # Ensure the number of mines is between 40 and 80

pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((1280, 640))
font = pygame.font.SysFont("comicsansms", 30)

BOARD_PADDING = 320

board = [
    list("################")
    for _ in range(16)
]

visible_board = [
    list("################")
    for _ in range(16)
]

def create_board(board):
    for y in range(16):
        for x in range(16):
            pygame.draw.rect(screen, (255, 255, 255), (x * 40 + BOARD_PADDING, y * 40, 40, 40), 1)
            if board[y][x] == "*":
                pygame.draw.circle(screen, (255, 0, 0), (x * 40 + 20 + BOARD_PADDING, y * 40 + 20), 10)

mines = []
numbers = []
flags = []

def print_board(board):
    for row in board:
        print(" ".join(row))
    print()

def pos_to_index(x, y):
    return (x - BOARD_PADDING) // 40, y // 40

def number_of_mines(board, x, y):
    count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if 0 <= x + i < 16 and 0 <= y + j < 16:
                if board[y + j][x + i] == "*":
                    count += 1
    return count

def number(board):
    for y in range(16):
        for x in range(16):
            if board[y][x] == "#":
                count = number_of_mines(board, x, y)
                if count > 0:
                    board[y][x] = str(count)
                else:
                    board[y][x] = "0"

def mine(board, p_x, p_y):
    while len(mines) < n_mines:
        x = random.randint(0, 15)
        y = random.randint(0, 15)
        if abs(x - p_x) > 1 or abs(y - p_y) > 1:
            if board[y][x] == "#":
                board[y][x] = "*"
                mines.append((x, y))

    return mines

running = True
First_click = True

while running:
    p_x, p_y = pygame.mouse.get_pos()
    p_x, p_y = pos_to_index(p_x, p_y)

    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if First_click and event.button == 1:
                p_x, p_y = pygame.mouse.get_pos()
                p_x, p_y = pos_to_index(p_x, p_y)
                mine(board, p_x, p_y)
                First_click = False
                number(board)
                print_board(board)
            if event.button == 1:
                if board[p_y][p_x] == "*":
                    print("Game Over")
                    running = False
                else:
                    board[p_y][p_x] = str(number_of_mines(board, p_x, p_y))
            if event.button == 3:
                if board[p_y][p_x] == "#":
                    board[p_y][p_x] = "F"
                    flags.append((p_x, p_y))
                elif board[p_y][p_x] == "F":
                    board[p_y][p_x] = "#"
                    flags.remove((p_x, p_y))

    for flag in flags:
        text = font.render("F", True, (255, 255, 255))
        screen.blit(text, (flag[0] * 40 + BOARD_PADDING + 10, flag[1] * 40))

    create_board(board)
    pygame.display.flip()

    clock.tick(60)

pygame.quit()