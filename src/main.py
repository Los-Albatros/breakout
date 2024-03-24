import asyncio
import random
import sys

import pygame

from options import load_pref, save_pref

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

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Breakout")

font_large = pygame.font.Font(None, 70)
font_small = pygame.font.Font(None, 36)

brick_break = pygame.mixer.Sound("../resources/sounds/bottle_break.wav")
brick_break.set_volume(0.1)


def draw_paddle(paddle):
    pygame.draw.rect(screen, PADDLE_COLOR, paddle)


def draw_ball(ball_x, ball_y):
    pygame.draw.circle(screen, BALL_COLOR, (ball_x, ball_y), BALL_RADIUS)


def draw_bricks(bricks):
    for brick in bricks:
        pygame.draw.rect(screen, brick[1], brick[0])


def load_map(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        bricks = []
        for line in lines:
            x, y, r, g, b = map(int, line.strip().split(','))
            brick_rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
            bricks.append((brick_rect, (r, g, b)))
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


def bounce(shape, ball_x, ball_y, ball_dx, ball_dy):
    if shape.colliderect(pygame.Rect(ball_x - BALL_RADIUS, ball_y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)):
        ball_dy *= -1
        collision_point_y = ball_y - ball_dy
        collision_point_x = ball_x - ball_dx
        if ball_dy > 0 and collision_point_y <= shape.top or ball_dy < 0 and collision_point_y >= shape.bottom:
            ball_dy *= -1
        if ball_dx > 0 and collision_point_x <= shape.left or ball_dx < 0 and collision_point_x >= shape.right:
            ball_dx *= -1
        return True, ball_dx, ball_dy
    return False, ball_dx, ball_dy


async def game(level=1, lives=5):
    clock = pygame.time.Clock()
    paddle = pygame.Rect((SCREEN_WIDTH - PADDLE_WIDTH) // 2, SCREEN_HEIGHT - PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball_x, ball_y = GAME_WIDTH // 2, SCREEN_HEIGHT // 2
    ball_dx, ball_dy = BALL_SPEED

    if level == 2:
        ball_x, ball_y = GAME_WIDTH // 2, 75

    bricks = load_map("../resources/maps/" + str(level) + ".bo")

    countdown = COUNTDOWN_TIME
    game_over = False

    switch_input = "Mouse"
    volume = 0

    params = load_pref()
    if params:
        volume = params['volume']
        switch_input = params['input']

    brick_break.set_volume(int(volume) / 200)

    while not game_over:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                await quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    await main_menu()

        mouse_x, _ = pygame.mouse.get_pos()
        if switch_input == "Keyboard":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and paddle.x > 0:
                paddle.x -= PADDLE_SPEED
            elif keys[pygame.K_RIGHT] and paddle.x < GAME_WIDTH - PADDLE_WIDTH:
                paddle.x += PADDLE_SPEED
        else:
            if mouse_x > paddle.x + PADDLE_WIDTH + PADDLE_SPEED + 1:
                paddle.x += PADDLE_SPEED
            elif mouse_x < paddle.x - PADDLE_SPEED - 1:
                paddle.x -= PADDLE_SPEED
            paddle.x = min(paddle.x, GAME_WIDTH - PADDLE_WIDTH + 10)
            if PADDLE_WIDTH // 4 > paddle.x > mouse_x:
                paddle.x = 0
            if GAME_WIDTH - PADDLE_WIDTH // 4 < paddle.x < mouse_x:
                paddle.x = GAME_WIDTH - PADDLE_WIDTH

        ball_x += ball_dx
        ball_y += ball_dy

        if ball_x <= BALL_RADIUS or ball_x >= SCREEN_WIDTH - BALL_RADIUS:
            ball_dx *= -1
        if ball_y <= BALL_RADIUS:
            ball_dy *= -1

        is_bounce, ball_dx, ball_dy = bounce(paddle, ball_x, ball_y, ball_dx, ball_dy)

        if ball_x >= GAME_WIDTH - BALL_RADIUS:
            ball_dx *= -1

        if ball_y >= SCREEN_HEIGHT:
            lives -= 1
            ball_x = random.randint(10, GAME_WIDTH - 10)
            ball_y = SCREEN_HEIGHT // 2
            ball_dx, ball_dy = BALL_SPEED
            ball_dx *= random.choice([-1, 1])
            if lives == 0 or len(bricks) == 0:
                game_over = True
            else:
                countdown = COUNTDOWN_TIME

        for brick in bricks:
            is_bounce, ball_dx, ball_dy = bounce(brick[0], ball_x, ball_y, ball_dx, ball_dy)
            if is_bounce:
                bricks.remove(brick)
                brick_break.play()

        draw_paddle(paddle)
        draw_ball(int(ball_x), int(ball_y))
        draw_bricks(bricks)
        draw_lives(lives)

        # refresh
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

        while countdown > 0:
            draw_countdown(countdown)
            pygame.time.delay(1000)
            countdown -= 1

        if len(bricks) == 0:
            countdown = COUNTDOWN_TIME
            game_over = True

    screen.fill(BLACK)
    if len(bricks) == 0:
        level = level + 1
        if level < 3:
            await game(level, lives)
        else:
            game_over_text = font_large.render("Game Win", True, GREEN)
            screen.blit(game_over_text, (GAME_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
    else:
        game_over_text = font_large.render("Game Over", True, RED)
        screen.blit(game_over_text, (GAME_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(2000)
    await main_menu()


async def quit_game():
    pygame.quit()
    sys.exit()


async def options():
    volume = 50
    switch_input = "Keyboard"

    params = load_pref()
    if params:
        volume = params['volume']
        switch_input = params['input']

    while True:
        screen.fill(BLACK)
        mx, my = pygame.mouse.get_pos()
        text_options = font_large.render("Options", True, (255, 255, 255))
        screen.blit(text_options, text_options.get_rect(center=(SCREEN_WIDTH // 4, 50)))

        button_width = 200
        button_height = 50
        button_left = SCREEN_WIDTH // 2 - button_width // 2
        button_top = 200
        switch_rect = pygame.Rect(button_left, button_top, button_width, button_height)
        switch_color = (0, 0, 155)
        save_button = pygame.Rect(SCREEN_WIDTH // 2 - button_width - 25, button_top + 200, button_width, button_height)
        save_color = (0, 155, 0)
        cancel_button = pygame.Rect(SCREEN_WIDTH // 2 + 25, button_top + 200, button_width, button_height)
        cancel_color = (155, 0, 0)

        pygame.draw.rect(screen, WHITE, (button_left, button_top + 115, button_width, 10))
        volume_rect = pygame.Rect(button_left + volume, 305, 10, 30)
        volume_color = (0, 155, 0)

        if pygame.mouse.get_pressed()[0] and button_left <= mx <= button_left + button_width and 280 <= my <= 350:
            volume = pygame.mouse.get_pos()[0] - button_left

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                await quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    await quit_game()
                if event.key == pygame.K_m:
                    await main_menu()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if switch_rect.collidepoint(mx, my):
                    if switch_input == "Keyboard":
                        switch_input = "Mouse"
                    else:
                        switch_input = "Keyboard"
                elif save_button.collidepoint(mx, my):
                    params['volume'] = volume
                    params['input'] = switch_input
                    await save_pref(params)
                    await main_menu()
                elif cancel_button.collidepoint(mx, my):
                    await main_menu()
        if switch_rect.collidepoint(mx, my):
            switch_color = BLUE
        elif save_button.collidepoint(mx, my):
            save_color = GREEN
        elif pygame.Rect(button_left, button_top + 110, button_width, 30).collidepoint(mx, my):
            volume_color = GREEN
        elif cancel_button.collidepoint(mx, my):
            cancel_color = RED
        pygame.draw.rect(screen, switch_color, switch_rect)
        switch_text = font_small.render(switch_input, True, WHITE)
        screen.blit(switch_text,
                    switch_text.get_rect(center=(button_left + button_width // 2, 200 + button_height // 2)))
        volume_text = font_small.render("Volume : ", True, WHITE)
        screen.blit(volume_text, volume_text.get_rect(
            center=(button_left + button_width // 2 - 50, 260 + button_height // 2)))
        volume_text2 = font_small.render(str(volume // 2) + " %", True, volume_color)
        screen.blit(volume_text2, volume_text2.get_rect(
            center=(button_left + button_width - 30, 260 + button_height // 2)))
        pygame.draw.rect(screen, save_color, save_button)
        pygame.draw.rect(screen, volume_color, volume_rect)
        save_text = font_small.render("Save", True, WHITE)
        screen.blit(save_text, save_text.get_rect(
            center=(SCREEN_WIDTH // 2 - button_width - 25 + button_width // 2, 400 + button_height // 2)))
        pygame.draw.rect(screen, cancel_color, cancel_button)
        cancel_text = font_small.render("Cancel", True, WHITE)
        screen.blit(cancel_text,
                    cancel_text.get_rect(center=(SCREEN_WIDTH // 2 + 25 + button_width // 2, 400 + button_height // 2)))
        pygame.display.update()


async def main_menu():
    clock = pygame.time.Clock()
    await asyncio.sleep(0)
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

    level = 1
    lives = 5

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
            is_bounce, ball_dx, ball_dy = bounce(button[0], ball_x, ball_y, ball_dx, ball_dy)
            if is_bounce:
                button = (button[0], random_color())
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
                await quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_play.collidepoint(mx, my):
                    await game(level, lives)
                if button_options.collidepoint(mx, my):
                    await options()
                if button_exit.collidepoint(mx, my):
                    await quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    await quit_game()
                if event.key == pygame.K_g:
                    await game(level, lives)
                if event.key == pygame.K_o:
                    await options()
        pygame.display.update()
        clock.tick(60)
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main_menu())
