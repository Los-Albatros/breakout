import pygame
import sys
import random
import math

pygame.init()

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
GAME_WIDTH = 800

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BALL_RADIUS = 10
BALL_COLOR = WHITE
BALL_SPEED = [5, 5]

PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_COLOR = GREEN
PADDLE_SPEED = 20

BRICK_WIDTH = 80
BRICK_HEIGHT = 30
BRICK_GAP = 1  
NUM_ROWS = 5
NUM_COLS = 10

COUNTDOWN_TIME = 5  # en secondes

LIVES = 5

screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Breakout")

font_large = pygame.font.Font(None, 70)
font_small = pygame.font.Font(None, 36)

brick_break = pygame.mixer.Sound("../ressources/sounds/bottle_break.wav")
brick_break.set_volume(0.1)

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

def random_color():
    return (random.randint(100, 245), random.randint(100, 245), random.randint(100, 245))

def draw_countdown(count):
    text = font_large.render(str(count), True, WHITE)
    text_rect = text.get_rect(center=(GAME_WIDTH + 80, SCREEN_HEIGHT // 2))
    pygame.draw.rect(screen, (0,0,0), text_rect)
    screen.blit(text, text_rect)
    pygame.display.flip()

def draw_lives(lives):
    pygame.draw.rect(screen, GREEN, (GAME_WIDTH+10, 0, 2, SCREEN_HEIGHT))
    x = GAME_WIDTH + 50
    for _ in range(lives):
        pygame.draw.circle(screen, WHITE, (x, 10), BALL_RADIUS * 0.67)
        x += BALL_RADIUS + 10

def main():
    clock = pygame.time.Clock()
    paddle_x = (SCREEN_WIDTH - PADDLE_WIDTH) // 2
    ball_x, ball_y = GAME_WIDTH // 2, SCREEN_HEIGHT // 2
    ball_dx, ball_dy = BALL_SPEED

    bricks = create_bricks()

    countdown = COUNTDOWN_TIME
    lives = LIVES
    game_over = False

    while not game_over:
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, _ = pygame.mouse.get_pos()
                paddle_x = min(mouse_x,GAME_WIDTH-PADDLE_WIDTH + 10)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle_x > 0:
            paddle_x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] and paddle_x < GAME_WIDTH - PADDLE_WIDTH:
            paddle_x += PADDLE_SPEED

        ball_x += ball_dx
        ball_y += ball_dy

        if ball_x <= BALL_RADIUS or ball_x >= SCREEN_WIDTH - BALL_RADIUS:
            ball_dx *= -1
        if ball_y <= BALL_RADIUS:
            ball_dy *= -1

        if ball_y + BALL_RADIUS >= SCREEN_HEIGHT - PADDLE_HEIGHT-1 and ball_x >= paddle_x and ball_x <= paddle_x + PADDLE_WIDTH:
            ball_dy *= -1

        if ball_x >= GAME_WIDTH - BALL_RADIUS:
            ball_dx *= -1

        if ball_y >= SCREEN_HEIGHT:
            lives -= 1
            ball_x, ball_y = GAME_WIDTH // 2, SCREEN_HEIGHT // 2
            ball_dx, ball_dy = BALL_SPEED

        for brick in bricks:
            if brick[0].colliderect(pygame.Rect(ball_x - BALL_RADIUS, ball_y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)):
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

    screen.fill((0, 0, 0))
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

if __name__ == "__main__":
    main()

