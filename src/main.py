# main.py - My City Game
# Шаг 6: камера + нижняя панель меню

import pygame
import sys

# Инициализация
pygame.init()

# Экран
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
BLACK = (20, 20, 30)
GOLD = (255, 215, 0)

# Шрифты
font_big = pygame.font.SysFont("Arial", 22, bold=True)
font_small = pygame.font.SysFont("Arial", 16)

# Класс здания
class Building:
    def __init__(self, x, y, width, height, name):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name

    def draw(self, surface, cam_x, cam_y):
        # Сдвигаем здание с учётом камеры
        draw_rect = self.rect.move(cam_x, cam_y)

        # Тень
        shadow = draw_rect.move(5, 5)
        pygame.draw.rect(surface, (30, 60, 30), shadow, border_radius=5)

        # Стены
        pygame.draw.rect(surface, WOOD_COLOR, draw_rect, border_radius=5)

        # Крыша
        roof_points = [
            (draw_rect.x - 10, draw_rect.y),
            (draw_rect.x + draw_rect.width // 2, draw_rect.y - 35),
            (draw_rect.x + draw_rect.width + 10, draw_rect.y),
        ]
        pygame.draw.polygon(surface, ROOF_COLOR, roof_points)

        # Название
        text = font_small.render(self.name, True, WHITE)
        text_rect = text.get_rect(center=draw_rect.center)
        surface.blit(text, text_rect)


# Здания на карте
buildings = [
    Building(200, 200, 90, 70, "Ратуша"),
    Building(400, 150, 80, 60, "Лесопилка"),
    Building(550, 300, 80, 60, "Ферма"),
    Building(100, 400, 90, 70, "Казарма"),
    Building(700, 450, 80, 60, "Шахта"),
]

# Камера
cam_x = 0
cam_y = 0
CAM_SPEED = 8

# Нижняя панель
PANEL_HEIGHT = 70
menu_items = [
    ("⚔", "Завоевание"),
    ("🛡", "Герои"),
    ("🔒", ""),
    ("🔒", ""),
    ("🌍", "Мир"),
]


def draw_background(surface, cam_x, cam_y):
    """Рисует траву с учётом камеры"""
    surface.fill(GRASS_GREEN)
    tile = 60
    start_x = -(cam_x % tile)
    start_y = -(cam_y % tile)

    for x in range(start_x, SCREEN_WIDTH + tile, tile):
        for y in range(start_y, SCREEN_HEIGHT + tile, tile):
            grid_x = (x - cam_x) // tile
            grid_y = (y - cam_y) // tile
            if (grid_x + grid_y) % 2 == 0:
                pygame.draw.rect(surface, DARK_GREEN, (x, y, tile, tile))


def draw_top_panel(surface):
    """Верхняя панель с ресурсами"""
    pygame.draw.rect(surface, BLACK, (0, 0, SCREEN_WIDTH, 50))
    pygame.draw.line(surface, (60, 60, 80), (0, 50), (SCREEN_WIDTH, 50), 2)

    timer = font_big.render("⏱ 01:19", True, WHITE)
    gold = font_big.render("💰 73,9K", True, GOLD)
    gems = font_big.render("💎 875", True, (100, 200, 255))
    people = font_big.render("👥 8/8", True, WHITE)

    surface.blit(timer, (20, 12))
    surface.blit(people, (180, 12))
    surface.blit(gold, (340, 12))
    surface.blit(gems, (560, 12))


def draw_bottom_panel(surface):
    """Нижняя панель меню"""
    panel_y = SCREEN_HEIGHT - PANEL_HEIGHT
    pygame.draw.rect(surface, BLACK, (0, panel_y, SCREEN_WIDTH, PANEL_HEIGHT))
    pygame.draw.line(surface, (60, 60, 80), (0, panel_y), (SCREEN_WIDTH, panel_y), 2)

    # Кнопки
    button_width = SCREEN_WIDTH // len(menu_items)
    for i, (icon, label) in enumerate(menu_items):
        x = i * button_width
        center_x = x + button_width // 2

        # Иконка
        icon_text = font_big.render(icon, True, WHITE)
        icon_rect = icon_text.get_rect(center=(center_x, panel_y + 25))
        surface.blit(icon_text, icon_rect)

        # Подпись
        if label:
            label_text = font_small.render(label, True, (200, 200, 220))
            label_rect = label_text.get_rect(center=(center_x, panel_y + 52))
            surface.blit(label_text, label_rect)


def main():
    global cam_x, cam_y

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Управление камерой стрелками
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            cam_x += CAM_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            cam_x -= CAM_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            cam_y += CAM_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            cam_y -= CAM_SPEED

        # Ограничение движения камеры
        cam_x = max(-400, min(400, cam_x))
        cam_y = max(-300, min(300, cam_y))

        # 1. Фон
        draw_background(screen, cam_x, cam_y)

        # 2. Здания
        for b in buildings:
            b.draw(screen, cam_x, cam_y)

        # 3. Верхняя панель
        draw_top_panel(screen)

        # 4. Нижняя панель
        draw_bottom_panel(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
