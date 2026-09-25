# main.py - My City Game
# Первый прототип игры на Pygame

import pygame
import sys

# Инициализация Pygame
pygame.init()

# Настройки экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My City Game")

# Цвета
GRASS_GREEN = (60, 140, 60)
DARK_GREEN = (45, 110, 45)
WOOD_COLOR = (160, 82, 45)
ROOF_COLOR = (200, 80, 60)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Шрифт
font = pygame.font.SysFont("Arial", 20, bold=True)

# Класс здания
class Building:
    def __init__(self, x, y, width, height, name):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name

    def draw(self, surface):
        # Тень
        shadow = self.rect.move(5, 5)
        pygame.draw.rect(surface, (0, 0, 0, 80), shadow, border_radius=5)

        # Стены
        pygame.draw.rect(surface, WOOD_COLOR, self.rect, border_radius=5)

        # Крыша (треугольник)
        roof_points = [
            (self.rect.x - 10, self.rect.y),
            (self.rect.x + self.rect.width // 2, self.rect.y - 35),
            (self.rect.x + self.rect.width + 10, self.rect.y),
        ]
        pygame.draw.polygon(surface, ROOF_COLOR, roof_points)

        # Название здания
        text = font.render(self.name, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)


# Создаём список зданий
buildings = [
    Building(200, 200, 90, 70, "Ратуша"),
    Building(400, 150, 80, 60, "Лесопилка"),
    Building(550, 300, 80, 60, "Ферма"),
    Building(100, 400, 90, 70, "Казарма"),
]

# Главный игровой цикл
def main():
    clock = pygame.time.Clock()
    running = True

    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 1. Рисуем фон (трава в клеточку)
        screen.fill(GRASS_GREEN)
        tile_size = 50
        for x in range(0, SCREEN_WIDTH, tile_size):
            for y in range(0, SCREEN_HEIGHT, tile_size):
                if (x // tile_size + y // tile_size) % 2 == 0:
                    pygame.draw.rect(screen, DARK_GREEN, (x, y, tile_size, tile_size))

        # 2. Рисуем здания
        for building in buildings:
            building.draw(screen)

        # 3. Рисуем верхнюю панель (HUD)
        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, 40))
        gold_text = font.render("💰 73,9K", True, (255, 215, 0))
        timer_text = font.render("⏱ 01:19", True, WHITE)
        screen.blit(gold_text, (20, 10))
        screen.blit(timer_text, (200, 10))

        # Обновляем экран
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
