import pygame
import time
import random

# Initialize pygame
pygame.init()

# Colors (RGB)
white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

# Screen dimensions
width = 600
height = 400

# Create game window
game_window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game")

# Define the clock
clock = pygame.time.Clock()

# Snake block size and speed
snake_block = 10
snake_speed = 12

# Font settings
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)


def score_display(score):
    """Displays the score at the top left corner."""
    value = score_font.render("Score: " + str(score), True, yellow)
    game_window.blit(value, [0, 0])


def draw_snake(snake_block, snake_list):
    """Draws the snake by updating each part of the body."""
    for block in snake_list:
        pygame.draw.rect(
            game_window, green, [block[0], block[1], snake_block, snake_block]
        )


def message(msg, color):
    """Displays the endgame message in the center of the screen."""
    mesg = font_style.render(msg, True, color)
    game_window.blit(mesg, [width / 6, height / 3])


def game_loop():
    # Initial position and variables
    game_over = False
    game_close = False

    x = width / 2
    y = height / 2
    x_change = 0
    y_change = 0

    snake_list = []
    length_of_snake = 1

    # Random placement for the first food
    food_x = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
    food_y = round(random.randrange(0, height - snake_block) / 10.0) * 10.0

    while not game_over:

        while game_close:
            # Display message if the game is over
            game_window.fill(black)
            message("Game Over! Press Q-Quit or C-Play Again", red)
            score_display(length_of_snake - 1)
            pygame.display.update()

            # Event handling for restarting or quitting the game
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop()

        # Event handling for movement
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x_change = -snake_block
                    y_change = 0
                elif event.key == pygame.K_RIGHT:
                    x_change = snake_block
                    y_change = 0
                elif event.key == pygame.K_UP:
                    y_change = -snake_block
                    x_change = 0
                elif event.key == pygame.K_DOWN:
                    y_change = snake_block
                    x_change = 0

        # Updating the snake's position
        if x >= width or x < 0 or y >= height or y < 0:
            game_close = True
        x += x_change
        y += y_change

        game_window.fill(blue)
        pygame.draw.rect(game_window, red, [food_x, food_y, snake_block, snake_block])

        snake_head = [x, y]
        snake_list.append(snake_head)

        if len(snake_list) > length_of_snake:
            del snake_list[0]

        # Collision with itself
        for block in snake_list[:-1]:
            if block == snake_head:
                game_close = True

        draw_snake(snake_block, snake_list)
        score_display(length_of_snake - 1)

        pygame.display.update()

        # Snake eats the food
        if x == food_x and y == food_y:
            food_x = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
            food_y = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
            length_of_snake += 1

        # Control the speed of the snake
        clock.tick(snake_speed)

    pygame.quit()
    quit()


# Run the game
game_loop()
