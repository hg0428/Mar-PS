import pygame
import sys
import random
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 640
HEIGHT = 480
CELL_SIZE = 20
FPS = 15

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Directions
UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"


class Game:
    def __init__(self):
        self.width = WIDTH // CELL_SIZE
        self.height = HEIGHT // CELL_SIZE
        self.snake_list = [(10, 5), (9, 5), (8, 5)]
        self.direction = RIGHT
        self.food_position = place_food(self.snake_list, self.width, self.height)
        self.score = 0
        self.game_over = False

    def move_snake(self):
        head = self.snake_list[0]
        if self.direction == UP:
            new_head = (head[0], head[1] - 1)
        elif self.direction == DOWN:
            new_head = (head[0], head[1] + 1)
        elif self.direction == LEFT:
            new_head = (head[0] - 1, head[1])
        elif self.direction == RIGHT:
            new_head = (head[0] + 1, head[1])

        if check_collision(new_head, self.snake_list):
            self.game_over = True
            return

        self.snake_list.insert(0, new_head)

        if new_head == self.food_position:
            self.score += 1
            self.food_position = place_food(self.snake_list, self.width, self.height)
        else:
            self.snake_list.pop()

    def eat_food(self):
        self.score += 1
        self.food_position = place_food(self.snake_list, self.width, self.height)

    def draw_game(self, surface):
        surface.fill(WHITE)
        for pos in self.snake_list:
            pygame.draw.rect(
                surface,
                GREEN,
                (pos[0] * CELL_SIZE, pos[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
            )
        pygame.draw.rect(
            surface,
            RED,
            (
                self.food_position[0] * CELL_SIZE,
                self.food_position[1] * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            ),
        )
        font = pygame.font.SysFont(None, 36)
        text = font.render(f"Score: {self.score}", True, BLACK)
        surface.blit(text, (10, 10))


def place_food(snake_list, width, height):
    while True:
        food_position = (random.randint(0, width - 1), random.randint(0, height - 1))
        if food_position not in snake_list:
            return food_position


def check_collision(head, snake_list):
    return (
        head[0] < 0
        or head[0] >= WIDTH // CELL_SIZE
        or head[1] < 0
        or head[1] >= HEIGHT // CELL_SIZE
        or head in snake_list[1:]
    )


def main():
    pygame.display.set_caption("Snake Game")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    game = Game()

    while not game.game_over:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if (
                    (event.key == K_UP and game.direction != DOWN)
                    or (event.key == K_DOWN and game.direction != UP)
                    or (event.key == K_LEFT and game.direction != RIGHT)
                    or (event.key == K_RIGHT and game.direction != LEFT)
                ):
                    if event.key == K_UP:
                        game.direction = UP
                    elif event.key == K_DOWN:
                        game.direction = DOWN
                    elif event.key == K_LEFT:
                        game.direction = LEFT
                    elif event.key == K_RIGHT:
                        game.direction = RIGHT

        if game.direction:
            game.move_snake()

        screen.fill(WHITE)
        game.draw_game(screen)
        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
