import pygame
import math
import random
import time

pygame.init()

tela = pygame.display.set_mode((1250, 650))
paint = pygame.Surface((1250, 650), pygame.SRCALPHA)
pygame.display.set_caption("Pong")
font = pygame.font.SysFont("comicsansms", 25)
font_morte = pygame.font.SysFont("comicsansms", 50)

tela.fill((0, 0, 0))
running = True

class Ball:
    def __init__(self, x=300, y=300, dx=1, dy=1):
        self.y = y
        self.x = x
        self.dx = dx
        self.dy = dy
        self.radius = 5

        self.v = 5
        self.theta = 45

        self.Vx = self.v * math.cos(math.radians(self.theta))
        self.Vy = self.v * math.sin(math.radians(self.theta))

class Player(pygame.Rect):
    def __init__(self, x):
        super().__init__(x, 300, 10, 100)

colors = [(230, 0, 0), (0, 200, 0), (0, 0, 210), (255, 255, 0), (0, 255, 255)]

class Obstacles(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 60)
        self.color = (255, 255, 255)
        self.left_hitbox = pygame.Rect(x-1, y, 1, 60)
        self.right_hitbox = pygame.Rect(x+21, y, 1, 60)
        self.upper_hitbox = pygame.Rect(x, y-1, 20, 1)
        self.bottom_hitbox = pygame.Rect(x, y+61, 20, 1)
        

clock = pygame.time.Clock()
ball = Ball()
player = Player(x = 100)

obstacles = []

LEVELS = {

    1: [
        "....##....",
        "...####...",
        "...####...",
        "....##....",
        "..........",
        "..........",
    ],

    2: [
        "..######..",
        "..######..",
        "..........",
        "..######..",
        "..........",
        "..........",
    ],

    3: [
        ".#.#.#.#..",
        "#.#.#.#...",
        ".#.#.#.#..",
        "#.#.#.#...",
        "..........",
        "..........",
    ],

    4: [
        "..##..##..",
        "..##..##..",
        "..##..##..",
        "..##..##..",
        "..........",
        "..........",
    ],

    5: [
        "..######..",
        ".########.",
        ".###..###.",
        ".###..###.",
        ".########.",
        "..######..",
    ],


    # =========================
    # MÉDIO — LEVELS 6 A 10
    # =========================

    6: [
        "##########",
        "..........",
        ".########.",
        "..........",
        "..######..",
        "..........",
    ],

    7: [
        "##########",
        "#........#",
        "#..####..#",
        "#..####..#",
        "#........#",
        "##########",
    ],

    8: [
        "###.......",
        ".###......",
        "..###.....",
        "...###....",
        "....###...",
        ".....#####",
    ],

    9: [
        "#.#.#.#.#.",
        ".#.#.#.#.#",
        "#.#.#.#.#.",
        ".#.#.#.#.#",
        "#.#.#.#.#.",
        ".#.#.#.#.#",
    ],

    10: [
        "##########",
        "##......##",
        "##.####.##",
        "##.####.##",
        "##......##",
        "##########",
    ],


    # =========================
    # DIFÍCIL — LEVELS 11 A 15
    # =========================

    11: [
        "##########",
        ".########.",
        "..######..",
        "...####...",
        "..######..",
        ".########.",
    ],

    12: [
        "###.###.##",
        "###.###.##",
        ".###.###.#",
        ".###.###.#",
        "###.###.##",
        "###.###.##",
    ],

    13: [
        "##########",
        "####..####",
        "###.##.###",
        "##.####.##",
        "#.######.#",
        "##########",
    ],

    14: [
        "##########",
        "#..####..#",
        "##.#..#.##",
        "#.######.#",
        "##..##..##",
        "##########",
    ],

    15: [
        "##########",
        "##########",
        "##########",
        "##########",
        "##########",
        "##########",
    ],
}

def Level(number):
    obstacles.clear()

    if number > 15:
        return None

    layout = LEVELS[number]

    start_x = 380
    start_y = 70

    spacing_x = 75
    spacing_y = 80

    for row, line in enumerate(layout):
        for column, block in enumerate(line):

            if block == "#":
                x = start_x + column * spacing_x
                y = start_y + row * spacing_y

                obstacle = Obstacles(x, y)
                obstacles.append(obstacle)

def reset_level(level):

    powerups.clear()
    balls.clear()

    player.height = 100
    player.centery = 325

    new_ball = Ball()

    new_ball.v = 5 + 0.2 * (level - 1)

    new_ball.Vx = new_ball.v * math.cos(math.radians(new_ball.theta))
    new_ball.Vy = new_ball.v * math.sin(math.radians(new_ball.theta))

    balls.append(new_ball)

    time.sleep(0.5)

class Powerups:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = color

class SlowBoost(Powerups):

    def apply(self, player, balls):
        for ball in balls:
            ball.v *= 0.5
            ball.Vx = ball.v * math.cos(math.radians(ball.theta))
            ball.Vy = ball.v * math.sin(math.radians(ball.theta))

class Moreballs(Powerups):

    def apply(self, player, balls):

        original_balls = balls[:]

        for ball in original_balls:
            for i in range(2):

                new_ball = Ball(
                    x=ball.x,
                    y=ball.y,
                    dx=random.choice([-1, 1]),
                    dy=random.choice([-1, 1])
                )

                new_ball.v = ball.v

                new_ball.Vx = new_ball.v * math.cos(
                    math.radians(new_ball.theta)
                )

                new_ball.Vy = new_ball.v * math.sin(
                    math.radians(new_ball.theta)
                )

                balls.append(new_ball)

# class ExtraLife(Powerups): Later, im lazy
#     def __init__(self):
#         pass

class PlayerSizeIncrease(Powerups):
    def apply(self, player, balls):
        player.height += 30

class BallsizeIncrease(Powerups):

    def apply(self, player, balls):

        for ball in balls:
            ball.radius = 8

def create_powerup(x, y):
    powerup_type = random.choice([SlowBoost, Moreballs, PlayerSizeIncrease, BallsizeIncrease])
    if powerup_type == SlowBoost:
        return SlowBoost(x, y, (0, 0, 255))
    elif powerup_type == Moreballs:
        return Moreballs(x, y, (0, 255, 0))
    elif powerup_type == PlayerSizeIncrease:
        return PlayerSizeIncrease(x, y, (255, 0, 0))
    elif powerup_type == BallsizeIncrease:
        return BallsizeIncrease(x, y, (255, 255, 0))
frames = 0
seconds = 0
score = 0
level = 0
balls = [ball]
powerups = []

while running:                                                 
    tela.fill((0, 0, 0))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    level_text = font.render(f"Level: {level}", True, (255, 255, 255))

    tela.blit(score_text, (10, 10))
    tela.blit(level_text, (200, 10))
    
    pygame.draw.rect(tela, (255, 255, 255), player)

    player.y = pygame.mouse.get_pos()[1] - player.height // 2

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for obstacle in obstacles:
        pygame.draw.rect(tela, obstacle.color, obstacle)
        pygame.draw.rect(tela, (0, 0, 0), obstacle.inflate(-8, -8))
        
    for ball in balls:
        ball_hitbox = pygame.Rect(ball.x - ball.radius, ball.y - ball.radius, 2 * ball.radius, 2 * ball.radius)
        pygame.draw.circle(tela, (255, 255, 255), (ball.x, ball.y), ball.radius)
        pygame.Rect(ball.x, ball.y, 9, 9)

        if ball.v < 5:
            ball.v = 5
            ball.Vx = ball.v * math.cos(math.radians(ball.theta))
            ball.Vy = ball.v * math.sin(math.radians(ball.theta))


        if (ball.y < 10 and ball.dy == -1) or (ball.y > 640 and ball.dy == 1):

            ball.dy *= -1

            ball.theta = random.randint(30, 60)

            ball.Vx = ball.v * math.cos(math.radians(ball.theta))
            ball.Vy = ball.v * math.sin(math.radians(ball.theta))


        if (ball.x > 1240 and ball.dx == 1):

            ball.dx *= -1

            ball.theta = random.randint(30, 60)

            ball.Vx = ball.v * math.cos(math.radians(ball.theta))
            ball.Vy = ball.v * math.sin(math.radians(ball.theta))

        if ball.x < 10:
            balls.remove(ball)
            if not balls:
                running = False

        steps = max(1, math.ceil(max(abs(ball.Vx), abs(ball.Vy))))

        for _ in range(steps):

            ball.x += (ball.Vx * ball.dx) / steps
            ball.y += (ball.Vy * ball.dy) / steps

            ball_hitbox = pygame.Rect(0, 0, 10, 10)
            ball_hitbox.center = (round(ball.x), round(ball.y))

            for obstacle in obstacles:
                if obstacle.left_hitbox.colliderect(ball_hitbox) or obstacle.right_hitbox.colliderect(ball_hitbox):

                    obstacles.remove(obstacle)

                    ball.dx *= -1
                    
                    score += 10

                    if random.randint(1, 5) == 1:
                        powerup = create_powerup(obstacle.x + obstacle.width // 2 - 10, obstacle.y + obstacle.height // 2 - 10)
                        powerups.append(powerup)

                elif obstacle.upper_hitbox.colliderect(ball_hitbox) or obstacle.bottom_hitbox.colliderect(ball_hitbox):

                    obstacles.remove(obstacle)

                    ball.dy *= -1

                    score += 10

                    if random.randint(1, 5) == 1:
                        powerup = create_powerup(obstacle.x + obstacle.width // 2 - 10, obstacle.y + obstacle.height // 2 - 10)
                        powerups.append(powerup)

            if ball_hitbox.colliderect(player) and ball.dx == -1:
                ball.dx = 1

                offset = ball.y - player.centery
                relative = offset / (player.height / 2)
                relative = max(-1, min(1, relative))

                min_theta = 10
                max_theta = 75
                
                ball.theta = min_theta + abs(relative) * (max_theta - min_theta)

                if relative < 0:
                    ball.dy = -1
                else:
                    ball.dy = 1

                ball.Vx = ball.v * math.cos(math.radians(ball.theta))
                ball.Vy = ball.v * math.sin(math.radians(ball.theta))

                break

        if frames % 120 == 0:
            ball.v *= 1.02
            print(ball.v)

            ball.Vx = ball.v * math.cos(math.radians(ball.theta))
            ball.Vy = ball.v * math.sin(math.radians(ball.theta))

    for powerup in powerups:

        pygame.draw.rect(tela, powerup.color, powerup.rect)

        powerup.rect.x -= 3

        if powerup.rect.colliderect(player):
            powerup.apply(player, balls)
            print(f"Powerup {powerup.__class__.__name__} applied!")
            powerups.remove(powerup)

        elif powerup.rect.x < -50:
            powerups.remove(powerup)


    if not obstacles:
        if level > 15:
            ball.v = 0
            bit_error = font_morte.render("5 BIT ERROR", True, (255, 0, 0))
            kill_text = font_morte.render("PARABENS, QUEBROU O JOGO", True, (255, 255, 255))
            tela.blit(kill_text, (250, 300))
            tela.blit(bit_error, (450, 200))
            for ball in balls:
                balls.remove(ball)
        else:
            level += 1
            Level(level)
            reset_level(level)

    pygame.display.flip()
    frames += 1

    if frames % 60 == 0:
        seconds += 1

    clock.tick(60)

pygame.quit()