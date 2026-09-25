# main.py - My City Game
# Шаг 10: рабочие кнопки и экономика

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
BTN_GREEN = (80, 180, 80)
BTN_GREEN_DARK = (50, 130, 50)
BTN_GREY = (100, 100, 110)
BTN_GREY_DARK = (60, 60, 70)

font_big = pygame.font.SysFont("Arial", 20, bold=True)
font_mid = pygame.font.SysFont("Arial", 16, bold=True)
font_small = pygame.font.SysFont("Arial", 13, bold=True)

# --- Экономика игрока ---
player_gold = 73900   # 73.9K
player_gems = 875


# --- Класс здания ---
class Building:
    def __init__(self, x, y, w, h, name, roof_color=ROOF_RED, level=1):
        self.rect = pygame.Rect(x, y, w, h)
        self.name = name
        self.roof_color = roof_color
        self.level = level

    def upgrade_cost(self):
        return self.level * 100

    def income(self):
        return self.level * 10

    def draw(self, surface, cam_x, cam_y):
        r = self.rect.move(cam_x, cam_y)

        # Тень
        shadow = pygame.Surface((r.width + 20, r.height + 30), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80),
                            (0, 0, r.width + 20, r.height + 20))
        surface.blit(shadow, (r.x - 10, r.y + r.height - 10))

        # Стены
        pygame.draw.rect(surface, WOOD_WALL, r, border_radius=6)
        pygame.draw.rect(surface, WOOD_WALL_DARK, r, width=3, border_radius=6)

        # Окна
        win_size = 14
        win_y = r.y + 10
        for i in range(2):
            win_x = r.x + 12 + i * (r.width - 40)
            pygame.draw.rect(surface, WINDOW_COLOR,
                             (win_x, win_y, win_size, win_size), border_radius=3)
            pygame.draw.rect(surface, (80, 60, 30),
                             (win_x, win_y, win_size, win_size), 2, border_radius=3)

        # Дверь
        door_w, door_h = 16, 22
        door_x = r.x + r.width // 2 - door_w // 2
        door_y = r.y + r.height - door_h
        pygame.draw.rect(surface, (80, 50, 30),
                         (door_x, door_y, door_w, door_h),
                         border_top_left_radius=8, border_top_right_radius=8)

        # Крыша
        roof_pts = [
            (r.x - 12, r.y),
            (r.x + r.width // 2, r.y - 40),
            (r.x + r.width + 12, r.y),
        ]
        pygame.draw.polygon(surface, self.roof_color, roof_pts)
        pygame.draw.polygon(surface, (0, 0, 0, 60), roof_pts, 2)

        # Уровень здания (звёздочка сверху)
        lvl_txt = font_small.render(f"Lv.{self.level}", True, GOLD)
        lvl_rect = lvl_txt.get_rect(center=(r.centerx, r.y - 50))
        surface.blit(lvl_txt, lvl_rect)

        # Название
        text = font_small.render(self.name, True, WHITE)
        text_rect = text.get_rect(center=(r.centerx, r.bottom - 8))
        bg = pygame.Surface((text_rect.width + 10, text_rect.height + 4),
                            pygame.SRCALPHA)
        bg.fill((0, 0, 0, 140))
        surface.blit(bg, (text_rect.x - 5, text_rect.y - 2))
        surface.blit(text, text_rect)

    def hit(self, pos, cam_x, cam_y):
        r = self.rect.move(cam_x, cam_y)
        return r.collidepoint(pos)


# --- Дерево ---
class Tree:
    def __init__(self, x, y, size=30):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, surface, cam_x, cam_y):
        x = self.x + cam_x
        y = self.y + cam_y
        pygame.draw.rect(surface, TREE_TRUNK,
                         (x - 4, y, 8, self.size), border_radius=2)
        pygame.draw.circle(surface, TREE_LEAVES_DARK, (x, y - 8), self.size)
        pygame.draw.circle(surface, TREE_LEAVES,
                           (x - 6, y - 14), self.size - 6)
        pygame.draw.circle(surface, TREE_LEAVES,
                           (x + 8, y - 10), self.size - 8)


def draw_path(surface, cam_x, cam_y, points, width=30):
    moved = [(x + cam_x, y + cam_y) for x, y in points]
    for i in range(len(moved) - 1):
        pygame.draw.line(surface, PATH_DARK, moved[i], moved[i + 1], width + 4)
        pygame.draw.line(surface, PATH_COLOR, moved[i], moved[i + 1], width)


def draw_river(surface, cam_x, cam_y):
    river_pts = []
    for i in range(-200, 1200, 40):
        wave = math.sin(i * 0.01) * 20
        river_pts.append((i + cam_x, 80 + wave + cam_y))
    if len(river_pts) > 1:
        pygame.draw.lines(surface, WATER_DARK, False, river_pts, 50)
        pygame.draw.lines(surface, WATER_COLOR, False, river_pts, 40)
        for i in range(0, len(river_pts) - 1, 3):
            x1, y1 = river_pts[i]
            x2, y2 = river_pts[i + 1]
            mid = ((x1 + x2) // 2, (y1 + y2) // 2)
            pygame.draw.circle(surface, (200, 230, 255, 100), mid, 3)


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


def draw_top_panel(surface):
    pygame.draw.rect(surface, PANEL_DARK, (0, 0, SCREEN_WIDTH, 50))
    pygame.draw.line(surface, (80, 80, 110), (0, 50), (SCREEN_WIDTH, 50), 2)

    timer = font_big.render("01:19", True, WHITE)
    surface.blit(timer, (20, 14))

    people = font_big.render("8/8", True, WHITE)
    surface.blit(people, (170, 14))

    # Золото
    pygame.draw.circle(surface, GOLD, (320, 25), 12)
    pygame.draw.circle(surface, (180, 140, 30), (320, 25), 12, 2)
    gold_str = f"{player_gold / 1000:.1f}K" if player_gold >= 1000 else str(player_gold)
    gold = font_big.render(gold_str, True, GOLD)
    surface.blit(gold, (340, 14))

    # Алмаз
    diamond_pts = [(540, 14), (552, 25), (540, 36), (528, 25)]
    pygame.draw.polygon(surface, GEM_BLUE, diamond_pts)
    pygame.draw.polygon(surface, (60, 130, 200), diamond_pts, 2)
    gems = font_big.render(str(player_gems), True, GEM_BLUE)
    surface.blit(gems, (560, 14))


def draw_bottom_panel(surface):
    panel_y = SCREEN_HEIGHT - 70
    pygame.draw.rect(surface, PANEL_DARK, (0, panel_y, SCREEN_WIDTH, 70))
    pygame.draw.line(surface, (80, 80, 110), (0, panel_y), (SCREEN_WIDTH, panel_y), 2)

    items = ["Завоевание", "Герои", "Замок", "Магазин", "Мир"]
    button_width = SCREEN_WIDTH // len(items)

    for i, label in enumerate(items):
        cx = i * button_width + button_width // 2
        cy = panel_y + 35

        btn_rect = pygame.Rect(cx - 30, cy - 22, 60, 44)
        pygame.draw.rect(surface, (45, 45, 60), btn_rect, border_radius=10)
        pygame.draw.rect(surface, (90, 90, 120), btn_rect, 2, border_radius=10)
        pygame.draw.circle(surface, (150, 150, 180), (cx, cy - 8), 8)

        txt = font_small.render(label, True, (220, 220, 240))
        tr = txt.get_rect(center=(cx, cy + 14))
        surface.blit(txt, tr)


def draw_popup(surface, building):
    """Рисует всплывающее окно. Возвращает (btn_upgrade_rect, btn_close_rect)"""
    # Затемнение
    dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 140))
    surface.blit(dim, (0, 0))

    # Окно
    w, h = 500, 360
    x = (SCREEN_WIDTH - w) // 2
    y = (SCREEN_HEIGHT - h) // 2
    popup_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, (50, 50, 70), popup_rect, border_radius=15)
    pygame.draw.rect(surface, (120, 120, 160), popup_rect, 3, border_radius=15)

    # Заголовок
    title = font_big.render(f"{building.name} — Уровень {building.level}", True, WHITE)
    title_rect = title.get_rect(center=(x + w // 2, y + 30))
    surface.blit(title, title_rect)

    pygame.draw.line(surface, (120, 120, 160),
                     (x + 20, y + 55), (x + w - 20, y + 55), 2)

    # Информация
    cost = building.upgrade_cost()
    income = building.income()
    next_income = (building.level + 1) * 10

    info_lines = [
        "Здание приносит ресурсы каждый час.",
        f"Текущий доход: +{income} в час",
        f"Следующий уровень: +{next_income} в час",
        f"Стоимость улучшения: {cost} золота",
    ]
    for i, line in enumerate(info_lines):
        txt = font_mid.render(line, True, (220, 220, 240))
        surface.blit(txt, (x + 30, y + 80 + i * 30))

    # Кнопка Улучшить
    btn_w, btn_h = 220, 50
    btn_x = x + w // 2 - btn_w // 2
    btn_y = y + h - 80
    btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

    # Если золота не хватает — серая
    if player_gold >= cost:
        color = BTN_GREEN
        color_dark = BTN_GREEN_DARK
        label = "УЛУЧШИТЬ"
    else:
        color = BTN_GREY
        color_dark = BTN_GREY_DARK
        label = "НЕ ХВАТАЕТ ЗОЛОТА"

    pygame.draw.rect(surface, color, btn_rect, border_radius=10)
    pygame.draw.rect(surface, color_dark, btn_rect, 3, border_radius=10)

    # Размер шрифта подгоняем
    if player_gold >= cost:
        btn_text = font_big.render(label, True, WHITE)
    else:
        btn_text = font_mid.render(label, True, WHITE)

    btn_text_rect = btn_text.get_rect(center=btn_rect.center)
    surface.blit(btn_text, btn_text_rect)

    # Кнопка закрыть
    close_rect = pygame.Rect(x + w - 40, y + 10, 30, 30)
    pygame.draw.rect(surface, (180, 60, 60), close_rect, border_radius=8)
    pygame.draw.line(surface, WHITE, (x + w - 33, y + 17), (x + w - 17, y + 33), 3)
    pygame.draw.line(surface, WHITE, (x + w - 17, y + 17), (x + w - 33, y + 33), 3)

    return btn_rect, close_rect


def draw_notification(surface, text, timer):
    """Всплывающее уведомление снизу"""
    if timer <= 0:
        return
    alpha = min(255, timer * 4)
    w, h = 300, 50
    x = (SCREEN_WIDTH - w) // 2
    y = SCREEN_HEIGHT - 150

    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill((30, 30, 40, alpha))
    surface.blit(bg, (x, y))
    pygame.draw.rect(surface, (100, 200, 100, alpha), (x, y, w, h), 2, border_radius=10)

    txt = font_mid.render(text, True, (255, 255, 255))
    tr = txt.get_rect(center=(x + w // 2, y + h // 2))
    surface.blit(txt, tr)


# --- Данные ---
buildings = [
    Building(180, 180, 90, 70, "Ратуша", ROOF_RED, level=2),
    Building(400, 130, 80, 60, "Лесопилка", ROOF_BROWN, level=1),
    Building(560, 280, 80, 60, "Ферма", ROOF_RED, level=3),
    Building(80, 380, 90, 70, "Казарма", ROOF_BROWN, level=1),
    Building(680, 430, 80, 60, "Шахта", ROOF_BROWN, level=2),
]

trees = []
random.seed(42)
for _ in range(25):
    x = random.randint(-200, 1000)
    y = random.randint(180, 700)
    if not any(abs(x - b.rect.x) < 130 and abs(y - b.rect.y) < 100 for b in buildings):
        trees.append(Tree(x, y, random.randint(20, 35)))

path_points = [
    (220, 250), (440, 200), (600, 340), (120, 450), (720, 490)
]

cam_x = 0
cam_y = 0
dragging = False
last_mouse_x = 0
last_mouse_y = 0
selected_building = None
mouse_down_pos = None
notification_text = ""
notification_timer = 0


def main():
    global cam_x, cam_y, dragging, last_mouse_x, last_mouse_y
    global selected_building, mouse_down_pos
    global player_gold, notification_text, notification_timer

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down_pos = event.pos
                dragging = True
                last_mouse_x, last_mouse_y = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False

                if mouse_down_pos:
                    dx = abs(event.pos[0] - mouse_down_pos[0])
                    dy = abs(event.pos[1] - mouse_down_pos[1])
                    is_tap = dx < 10 and dy < 10

                    if is_tap:
                        if selected_building:
                            # Открыто меню — проверяем кнопки
                            btn_rect, close_rect = draw_popup(screen, selected_building)

                            if close_rect.collidepoint(event.pos):
                                selected_building = None
                            elif btn_rect.collidepoint(event.pos):
                                cost = selected_building.upgrade_cost()
                                if player_gold >= cost:
                                    player_gold -= cost
                                    selected_building.level += 1
                                    notification_text = f"{selected_building.name} улучшен до ур. {selected_building.level}!"
                                    notification_timer = 120
                                else:
                                    notification_text = "Недостаточно золота!"
                                    notification_timer = 120
                        else:
                            # Проверяем попадание по зданию
                            for b in buildings:
                                if b.hit(event.pos, cam_x, cam_y):
                                    selected_building = b
                                    break

                    mouse_down_pos = None

            elif event.type == pygame.MOUSEMOTION and dragging and not selected_building:
                dx = event.pos[0] - last_mouse_x
                dy = event.pos[1] - last_mouse_y
                cam_x += dx
                cam_y += dy
                last_mouse_x, last_mouse_y = event.pos

        cam_x = max(-400, min(400, cam_x))
        cam_y = max(-300, min(300, cam_y))

        # Таймер уведомления
        if notification_timer > 0:
            notification_timer -= 1

        # --- Отрисовка ---
        draw_background(screen, cam_x, cam_y)
        draw_river(screen, cam_x, cam_y)

        for i in range(len(path_points) - 1):
            draw_path(screen, cam_x, cam_y,
                      [path_points[i], path_points[i + 1]], 28)

        for t in sorted(trees, key=lambda t: t.y):
            t.draw(screen, cam_x, cam_y)

        for b in buildings:
            b.draw(screen, cam_x, cam_y)

        draw_top_panel(screen)
        draw_bottom_panel(screen)

        if selected_building:
            draw_popup(screen, selected_building)

        if notification_timer > 0:
            draw_notification(screen, notification_text, notification_timer)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
