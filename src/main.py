# main.py - My City Game
# Шаг 8: улучшенная графика

import pygame
import sys
import random
import math

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("My City Game")

# --- Палитра ---
GRASS_LIGHT = (86, 152, 70)
GRASS_DARK = (68, 130, 56)
PATH_COLOR = (196, 160, 110)
PATH_DARK = (160, 128, 86)
WATER_COLOR = (70, 130, 200)
WATER_DARK = (50, 100, 170)
WOOD_WALL = (150, 100, 60)
WOOD_WALL_DARK = (110, 70, 40)
ROOF_RED = (190, 70, 55)
ROOF_RED_DARK = (140, 45, 35)
ROOF_BROWN = (120, 70, 40)
WINDOW_COLOR = (255, 220, 130)
TREE_TRUNK = (90, 60, 35)
TREE_LEAVES = (60, 130, 60)
TREE_LEAVES_DARK = (40, 100, 45)
WHITE = (255, 255, 255)
BLACK = (18, 18, 25)
PANEL_DARK = (28, 28, 40)
GOLD = (255, 210, 60)
GEM_BLUE = (110, 200, 255)

font_big = pygame.font.SysFont("Arial", 20, bold=True)
font_small = pygame.font.SysFont("Arial", 14, bold=True)


# --- Класс здания ---
class Building:
    def __init__(self, x, y, w, h, name, roof_color=ROOF_RED, style="house"):
        self.rect = pygame.Rect(x, y, w, h)
        self.name = name
        self.roof_color = roof_color
        self.style = style  # "house" или "tower"

    def draw(self, surface, cam_x, cam_y):
        r = self.rect.move(cam_x, cam_y)

        # Тень
        shadow = pygame.Surface((r.width + 20, r.height + 30), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80),
                            (0, 0, r.width + 20, r.height + 20))
        surface.blit(shadow, (r.x - 10, r.y + r.height - 10))

        # Стены (два тона для объёма)
        pygame.draw.rect(surface, WOOD_WALL, r, border_radius=6)
        pygame.draw.rect(surface, WOOD_WALL_DARK, r, width=3, border_radius=6)

        # Окна
        win_size = 16
        win_y = r.y + r.height // 2 - win_size // 2
        for i in range(2):
            win_x = r.x + 12 + i * (r.width - 40)
            pygame.draw.rect(surface, WINDOW_COLOR,
                             (win_x, win_y, win_size, win_size), border_radius=3)
            pygame.draw.rect(surface, (80, 60, 30),
                             (win_x, win_y, win_size, win_size), 2, border_radius=3)

        # Дверь
        door_w, door_h = 18, 26
        door_x = r.x + r.width // 2 - door_w // 2
        door_y = r.y + r.height - door_h
        pygame.draw.rect(surface, (80, 50, 30),
                         (door_x, door_y, door_w, door_h),
                         border_top_left_radius=8, border_top_right_radius=8)

        # Крыша (треугольник с тенью)
        roof_pts = [
            (r.x - 12, r.y),
            (r.x + r.width // 2, r.y - 40),
            (r.x + r.width + 12, r.y),
        ]
        pygame.draw.polygon(surface, self.roof_color, roof_pts)
        pygame.draw.polygon(surface, (0, 0, 0, 60), roof_pts, 2)

        # Тень под крышей
        pygame.draw.line(surface, (0, 0, 0, 50),
                         (r.x - 12, r.y), (r.x + r.width + 12, r.y), 3)

        # Название
        text = font_small.render(self.name, True, WHITE)
        text_rect = text.get_rect(center=r.center)
        bg = pygame.Surface((text_rect.width + 10, text_rect.height + 4),
                            pygame.SRCALPHA)
        bg.fill((0, 0, 0, 120))
        surface.blit(bg, (text_rect.x - 5, text_rect.y - 2))
        surface.blit(text, text_rect)


# --- Класс дерева ---
class Tree:
    def __init__(self, x, y, size=30):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, surface, cam_x, cam_y):
        x = self.x + cam_x
        y = self.y + cam_y
        # Ствол
        pygame.draw.rect(surface, TREE_TRUNK,
                         (x - 4, y, 8, self.size), border_radius=2)
        # Крона (3 круга)
        pygame.draw.circle(surface, TREE_LEAVES_DARK,
                           (x, y - 8), self.size)
        pygame.draw.circle(surface, TREE_LEAVES,
                           (x - 6, y - 14), self.size - 6)
        pygame.draw.circle(surface, TREE_LEAVES,
                           (x + 8, y - 10), self.size - 8)


# --- Дорожки ---
def draw_path(surface, cam_x, cam_y, points, width=30):
    """Рисует дорожку по точкам"""
    moved = [(x + cam_x, y + cam_y) for x, y in points]
    for i in range(len(moved) - 1):
        pygame.draw.line(surface, PATH_DARK, moved[i], moved[i + 1], width + 4)
        pygame.draw.line(surface, PATH_COLOR, moved[i], moved[i + 1], width)


# --- Река ---
def draw_river(surface, cam_x, cam_y):
    river_pts = []
    for i in range(-200, 1200, 40):
        wave = math.sin(i * 0.01) * 20
        river_pts.append((i + cam_x, 80 + wave + cam_y))
    if len(river_pts) > 1:
        pygame.draw.lines(surface, WATER_DARK, False, river_pts, 50)
        pygame.draw.lines(surface, WATER_COLOR, False, river_pts, 40)
        # Блики
        for i in range(0, len(river_pts) - 1, 3):
            x1, y1 = river_pts[i]
            x2, y2 = river_pts[i + 1]
            mid = ((x1 + x2) // 2, (y1 + y2) // 2)
            pygame.draw.circle(surface, (200, 230, 255, 100), mid, 3)


# --- Фон ---
def draw_background(surface, cam_x, cam_y):
    surface.fill(GRASS_LIGHT)
    tile = 80
    start_x = -(cam_x % tile) - tile
    start_y = -(cam_y % tile) - tile
    for x in range(start_x, SCREEN_WIDTH + tile, tile):
        for y in range(start_y, SCREEN_HEIGHT + tile, tile):
            gx = (x - cam_x) // tile
            gy = (y - cam_y) // tile
            if (gx + gy) % 2 == 0:
                pygame.draw.rect(surface, GRASS_DARK, (x, y, tile, tile))


# --- Верхняя панель ---
def draw_top_panel(surface):
    pygame.draw.rect(surface, PANEL_DARK, (0, 0, SCREEN_WIDTH, 50))
    pygame.draw.line(surface, (80, 80, 110), (0, 50), (SCREEN_WIDTH, 50), 2)

    # Таймер
    timer = font_big.render("01:19", True, WHITE)
    surface.blit(timer, (20, 14))

    # Люди
    people = font_big.render("8/8", True, WHITE)
    surface.blit(people, (170, 14))

    # Золото (монетка + текст)
    pygame.draw.circle(surface, GOLD, (320, 25), 12)
    pygame.draw.circle(surface, (180, 140, 30), (320, 25), 12, 2)
    gold = font_big.render("73.9K", True, GOLD)
    surface.blit(gold, (340, 14))

    # Алмаз
    diamond_pts = [(540, 14), (552, 25), (540, 36), (528, 25)]
    pygame.draw.polygon(surface, GEM_BLUE, diamond_pts)
    pygame.draw.polygon(surface, (60, 130, 200), diamond_pts, 2)
    gems = font_big.render("875", True, GEM_BLUE)
    surface.blit(gems, (560, 14))


# --- Нижняя панель ---
def draw_bottom_panel(surface):
    panel_y = SCREEN_HEIGHT - 70
    pygame.draw.rect(surface, PANEL_DARK, (0, panel_y, SCREEN_WIDTH, 70))
    pygame.draw.line(surface, (80, 80, 110), (0, panel_y), (SCREEN_WIDTH, panel_y), 2)

    items = ["Завоевание", "Герои", "Замок", "Магазин", "Мир"]
    button_width = SCREEN_WIDTH // len(items)

    for i, label in enumerate(items):
        cx = i * button_width + button_width // 2
        cy = panel_y + 35

        # Фон кнопки
        btn_rect = pygame.Rect(cx - 30, cy - 22, 60, 44)
        pygame.draw.rect(surface, (45, 45, 60), btn_rect, border_radius=10)
        pygame.draw.rect(surface, (90, 90, 120), btn_rect, 2, border_radius=10)

        # Иконка-заглушка (круг)
        pygame.draw.circle(surface, (150, 150, 180), (cx, cy - 8), 8)

        # Подпись
        txt = font_small.render(label, True, (220, 220, 240))
        tr = txt.get_rect(center=(cx, cy + 14))
        surface.blit(txt, tr)


# --- Данные ---
buildings = [
    Building(180, 180, 90, 70, "Ратуша", ROOF_RED),
    Building(400, 130, 80, 60, "Лесопилка", ROOF_BROWN),
    Building(560, 280, 80, 60, "Ферма", ROOF_RED),
    Building(80, 380, 90, 70, "Казарма", ROOF_BROWN),
    Building(680, 430, 80, 60, "Шахта", ROOF_BROWN),
]

trees = []
random.seed(42)
for _ in range(25):
    x = random.randint(-200, 1000)
    y = random.randint(180, 700)
    # Не ставим деревья на здания
    if not any(abs(x - b.rect.x) < 120 and abs(y - b.rect.y) < 120 for b in buildings):
        trees.append(Tree(x, y, random.randint(20, 35)))

# Дорожки между зданиями
path_points = [
    (220, 250), (440, 200), (600, 340), (120, 450), (720, 490)
]

# Камера
cam_x = 0
cam_y = 0
dragging = False
last_mouse_x = 0
last_mouse_y = 0


def main():
    global cam_x, cam_y, dragging, last_mouse_x, last_mouse_y

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                dragging = True
                last_mouse_x, last_mouse_y = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                dx = event.pos[0] - last_mouse_x
                dy = event.pos[1] - last_mouse_y
                cam_x += dx
                cam_y += dy
                last_mouse_x, last_mouse_y = event.pos

        cam_x = max(-400, min(400, cam_x))
        cam_y = max(-300, min(300, cam_y))

        # Отрисовка
        draw_background(screen, cam_x, cam_y)
        draw_river(screen, cam_x, cam_y)

        # Дорожки
        for i in range(len(path_points) - 1):
            draw_path(screen, cam_x, cam_y,
                      [path_points[i], path_points[i + 1]], 28)

        # Деревья (сзади)
        for t in sorted(trees, key=lambda t: t.y):
            t.draw(screen, cam_x, cam_y)

        # Здания
        for b in buildings:
            b.draw(screen, cam_x, cam_y)

        # Панели
        draw_top_panel(screen)
        draw_bottom_panel(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
