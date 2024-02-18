import random
import sys

import pygame

pygame.init()


def random_color():
    return random.randint(100, 245), random.randint(100, 245), random.randint(100, 245)


SCREEN_WIDTH = 960
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
GAME_WIDTH = 800

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

BALL_RADIUS = 10
BALL_COLOR = WHITE
BALL_SPEED = [5, 5]

PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_COLOR = random_color()
PADDLE_SPEED = 20

BRICK_WIDTH = 80
BRICK_HEIGHT = 30
BRICK_GAP = 1
NUM_ROWS = 5
NUM_COLS = 10

COUNTDOWN_TIME = 3  # seconds

LIVES = 5

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Breakout")

font_large = pygame.font.Font(None, 70)
font_small = pygame.font.Font(None, 36)

brick_break = pygame.mixer.Sound("../resources/sounds/bottle_break.wav")
brick_break.set_volume(0.1)

mouse = True


def draw_paddle(paddle_x):
    pygame.draw.rect(screen, PADDLE_COLOR, (paddle_x, SCREEN_HEIGHT - PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT))


def draw_ball(ball_x, ball_y):
    pygame.draw.circle(screen, BALL_COLOR, (ball_x, ball_y), BALL_RADIUS)


def draw_bricks(bricks):
    for brick in bricks:
        pygame.draw.rect(screen, brick[1], brick[0])


def create_bricks():
    bricks = []
    for row in range(NUM_ROWS):
        colors = [random_color() for _ in range(NUM_COLS)]
        for col, color in enumerate(colors):
            brick_x = col * (BRICK_WIDTH + BRICK_GAP)
            brick_y = row * (BRICK_HEIGHT + BRICK_GAP)
            brick_rect = pygame.Rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT)
            bricks.append((brick_rect, color))
    return bricks


def draw_countdown(count):
    text = font_large.render(str(count), True, WHITE)
    text_rect = text.get_rect(center=(GAME_WIDTH + 80, SCREEN_HEIGHT // 2))
    pygame.draw.rect(screen, (0, 0, 0), text_rect)
    screen.blit(text, text_rect)
    pygame.display.flip()


def draw_lives(lives):
    pygame.draw.rect(screen, PADDLE_COLOR, (GAME_WIDTH + 10, 0, 2, SCREEN_HEIGHT))
    x = GAME_WIDTH + 50
    for _ in range(lives):
        pygame.draw.circle(screen, WHITE, (x, 10), BALL_RADIUS * 0.67)
        x += BALL_RADIUS + 10


def game():
    clock = pygame.time.Clock()
    paddle_x = (SCREEN_WIDTH - PADDLE_WIDTH) // 2
    ball_x, ball_y = GAME_WIDTH // 2, SCREEN_HEIGHT // 2
    ball_dx, ball_dy = BALL_SPEED

    bricks = create_bricks()

    countdown = COUNTDOWN_TIME
    lives = LIVES
    game_over = False

    while not game_over:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    main_menu()

        mouse_x, _ = pygame.mouse.get_pos()
        if not mouse:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and paddle_x > 0:
                paddle_x -= PADDLE_SPEED
            elif keys[pygame.K_RIGHT] and paddle_x < GAME_WIDTH - PADDLE_WIDTH:
                paddle_x += PADDLE_SPEED
        else:
            if mouse_x > paddle_x + PADDLE_WIDTH + PADDLE_SPEED + 1:
                paddle_x += PADDLE_SPEED
            elif mouse_x < paddle_x - PADDLE_SPEED - 1:
                paddle_x -= PADDLE_SPEED
            paddle_x = min(paddle_x, GAME_WIDTH - PADDLE_WIDTH + 10)
            if PADDLE_WIDTH // 4 > paddle_x > mouse_x:
                paddle_x = 0
            if GAME_WIDTH - PADDLE_WIDTH // 4 < paddle_x < mouse_x:
                paddle_x = GAME_WIDTH - PADDLE_WIDTH

        ball_x += ball_dx
        ball_y += ball_dy

        if ball_x <= BALL_RADIUS or ball_x >= SCREEN_WIDTH - BALL_RADIUS:
            ball_dx *= -1
        if ball_y <= BALL_RADIUS:
            ball_dy *= -1

        if ball_y + BALL_RADIUS >= SCREEN_HEIGHT - PADDLE_HEIGHT - 1 and paddle_x <= ball_x <= paddle_x + PADDLE_WIDTH:
            ball_dy *= -1

        if ball_x >= GAME_WIDTH - BALL_RADIUS:
            ball_dx *= -1

        if ball_y >= SCREEN_HEIGHT:
            lives -= 1
            ball_x = random.randint(10, GAME_WIDTH - 10)
            ball_y = SCREEN_HEIGHT // 2
            ball_dx = BALL_SPEED
            ball_dy = BALL_SPEED
            countdown = COUNTDOWN_TIME

        for brick in bricks:
            if brick[0].colliderect(
                    pygame.Rect(ball_x - BALL_RADIUS, ball_y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)):
                bricks.remove(brick)
                brick_break.play()
                ball_dy *= -1

        draw_paddle(paddle_x)
        draw_ball(int(ball_x), int(ball_y))
        draw_bricks(bricks)
        draw_lives(lives)

        # refresh
        pygame.display.flip()
        clock.tick(60)

        while countdown > 0:
            draw_countdown(countdown)
            pygame.time.delay(1000)
            countdown -= 1

        if lives == 0 or not bricks:
            game_over = True

    screen.fill(BLACK)
    if not bricks:
        game_over_text = font_large.render("Game Win", True, GREEN)
        screen.blit(game_over_text, (GAME_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
    else:
        game_over_text = font_large.render("Game Over", True, RED)
        screen.blit(game_over_text, (GAME_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(2000)
    quit_game()


def quit_game():
    pygame.quit()
    sys.exit()


def options():
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()
                    game()
                if event.key == pygame.K_m:
                    main_menu()
        pygame.display.update()


def main_menu():
    clock = pygame.time.Clock()
    ball_x = random.randint(10, GAME_WIDTH - 10)
    ball_y = random.randint(10, 100)
    ball_dx, ball_dy = BALL_SPEED
    buttons = []
    button_width = 200
    button_height = 50
    button_left = SCREEN_WIDTH // 2 - button_width // 2
    button_top = 200
    button_play = pygame.Rect(button_left, button_top, button_width, button_height)
    button_options = pygame.Rect(button_left, button_top + 100, button_width, button_height)
    button_exit = pygame.Rect(button_left, button_top + 200, button_width, button_height)
    buttons.append((button_play, (0, 0, 155)))
    buttons.append((button_options, (0, 155, 0)))
    buttons.append((button_exit, (155, 0, 0)))

    while True:
        screen.fill(BLACK)
        text_play = font_small.render("Play", True, (255, 255, 255))
        text_options = font_small.render("Options", True, (255, 255, 255))
        text_exit = font_small.render("Exit", True, (255, 255, 255))
        mx, my = pygame.mouse.get_pos()
        ball_x += ball_dx
        ball_y += ball_dy

        if ball_x > SCREEN_WIDTH or ball_x < 0:
            ball_dx *= -1
        if ball_y > SCREEN_HEIGHT or ball_y < 0:
            ball_dy *= -1

        for button in buttons:
            if button[0].colliderect(
                    pygame.Rect(ball_x - BALL_RADIUS, ball_y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)):
                button = (button[0], random_color())
                dx = ball_x - (button[0].x + button[0].width // 2)
                dy = ball_y - (button[0].y + button[0].height // 2)

                if abs(dx) > abs(dy):
                    if dx > 0:
                        ball_x = button[0].right + BALL_RADIUS
                    else:
                        ball_x = button[0].left - BALL_RADIUS
                    ball_dx *= -1
                else:
                    if dy > 0:
                        ball_y = button[0].bottom + BALL_RADIUS
                    else:
                        ball_y = button[0].top - BALL_RADIUS
                        ball_dy *= -1
            pygame.draw.rect(screen, button[1], button[0])

        screen.blit(text_play,
                    text_play.get_rect(center=(button_left + button_width // 2, button_top + button_height // 2)))
        screen.blit(text_options, text_options.get_rect(
            center=(button_left + button_width // 2, button_top + 100 + button_height // 2)))
        screen.blit(text_exit,
                    text_exit.get_rect(center=(button_left + button_width // 2, button_top + 200 + button_height // 2)))
        draw_ball(int(ball_x), int(ball_y))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_play.collidepoint(mx, my):
                    game()
                if button_options.collidepoint(mx, my):
                    options()
                if button_exit.collidepoint(mx, my):
                    quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()
                if event.key == pygame.K_g:
                    game()
                if event.key == pygame.K_o:
                    options()
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main_menu()
