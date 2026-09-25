# main.py - My City Game
# Шаг 16: Магазин зданий

import pygame
import sys
import random
import math
import json
import os

pygame.init()

try:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
except Exception:
    SCREEN_WIDTH, SCREEN_HEIGHT = 540, 960
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

if SCREEN_WIDTH < 400:
    SCREEN_WIDTH = 540
if SCREEN_HEIGHT < 600:
    SCREEN_HEIGHT = 960
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("My City Game")
print(f"📱 Экран: {SCREEN_WIDTH} × {SCREEN_HEIGHT}")

SCALE = min(SCREEN_WIDTH / 540, SCREEN_HEIGHT / 960)
SCALE_X = SCREEN_WIDTH / 540
SCALE_Y = SCREEN_HEIGHT / 960

TOP_PANEL_H = int(50 * SCALE_Y)
BOTTOM_PANEL_H = int(70 * SCALE_Y)


def S(v): return max(1, int(v * SCALE))
def SX(v): return max(1, int(v * SCALE_X))
def SY(v): return max(1, int(v * SCALE_Y))


# Палитра
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
ROOF_BLUE = (70, 100, 180)
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
BTN_BLUE = (70, 130, 220)
BTN_BLUE_DARK = (40, 90, 160)

font_big = pygame.font.SysFont("Arial", max(14, int(20 * SCALE)), bold=True)
font_mid = pygame.font.SysFont("Arial", max(12, int(16 * SCALE)), bold=True)
font_small = pygame.font.SysFont("Arial", max(10, int(13 * SCALE)), bold=True)

SAVE_FILE = "save_data.json"

player_gold = 73900
player_gems = 875
gold_income_timer = 0

# Шаблоны зданий для магазина
SHOP_CATALOG = [
    {"name": "Дом", "cost": 500, "income": 15, "color": ROOF_RED},
    {"name": "Мельница", "cost": 1200, "income": 30, "color": ROOF_BROWN},
    {"name": "Кузница", "cost": 2500, "income": 60, "color": ROOF_RED},
    {"name": "Храм", "cost": 5000, "income": 120, "color": ROOF_BLUE},
]


class Building:
    def __init__(self, x, y, w, h, name, roof_color=ROOF_RED, level=1, base_income=10):
        self.rect = pygame.Rect(x, y, w, h)
        self.name = name
        self.roof_color = roof_color
        self.level = level
        self.base_income = base_income

    def upgrade_cost(self):
        return self.level * 100

    def income(self):
        return self.level * self.base_income

    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "x": self.rect.x,
            "y": self.rect.y,
            "w": self.rect.width,
            "h": self.rect.height,
            "base_income": self.base_income,
        }

    def draw(self, surface, cam_x, cam_y):
        r = self.rect.move(cam_x, cam_y)
        shadow = pygame.Surface((r.width + S(15), r.height + S(20)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 80),
                            (0, 0, r.width + S(15), r.height + S(15)))
        surface.blit(shadow, (r.x - S(8), r.y + r.height - S(8)))

        pygame.draw.rect(surface, WOOD_WALL, r, border_radius=S(6))
        pygame.draw.rect(surface, WOOD_WALL_DARK, r, width=S(2), border_radius=S(6))

        win_size = S(12)
        win_y = r.y + S(8)
        for i in range(2):
            win_x = r.x + S(10) + i * (r.width - S(35))
            pygame.draw.rect(surface, WINDOW_COLOR,
                             (win_x, win_y, win_size, win_size), border_radius=S(2))
            pygame.draw.rect(surface, (80, 60, 30),
                             (win_x, win_y, win_size, win_size), S(2), border_radius=S(2))

        door_w, door_h = S(14), S(20)
        door_x = r.x + r.width // 2 - door_w // 2
        door_y = r.y + r.height - door_h
        pygame.draw.rect(surface, (80, 50, 30),
                         (door_x, door_y, door_w, door_h),
                         border_top_left_radius=S(6), border_top_right_radius=S(6))

        roof_pts = [(r.x - S(10), r.y),
                    (r.x + r.width // 2, r.y - S(30)),
                    (r.x + r.width + S(10), r.y)]
        pygame.draw.polygon(surface, self.roof_color, roof_pts)
        pygame.draw.polygon(surface, (0, 0, 0, 60), roof_pts, S(2))

        lvl_txt = font_small.render(f"Lv.{self.level}", True, GOLD)
        lvl_rect = lvl_txt.get_rect(center=(r.centerx, r.y - S(42)))
        surface.blit(lvl_txt, lvl_rect)

        text = font_small.render(self.name, True, WHITE)
        text_rect = text.get_rect(center=(r.centerx, r.bottom - S(8)))
        bg = pygame.Surface((text_rect.width + S(8), text_rect.height + S(4)),
                            pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        surface.blit(bg, (text_rect.x - S(4), text_rect.y - S(2)))
        surface.blit(text, text_rect)

    def hit(self, pos, cam_x, cam_y):
        return self.rect.move(cam_x, cam_y).collidepoint(pos)


class Tree:
    def __init__(self, x, y, size=25):
        self.x, self.y, self.size = x, y, size

    def draw(self, surface, cam_x, cam_y):
        x = self.x + cam_x
        y = self.y + cam_y
        pygame.draw.rect(surface, TREE_TRUNK,
                         (x - S(3), y, S(6), self.size), border_radius=S(2))
        pygame.draw.circle(surface, TREE_LEAVES_DARK, (x, y - S(6)), self.size)
        pygame.draw.circle(surface, TREE_LEAVES,
                           (x - S(5), y - S(12)), self.size - S(5))
        pygame.draw.circle(surface, TREE_LEAVES,
                           (x + S(7), y - S(8)), self.size - S(6))


def load_game():
    global player_gold, player_gems, buildings
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            player_gold = data.get("gold", 73900)
            player_gems = data.get("gems", 875)
            saved_buildings = data.get("buildings", [])
            if saved_buildings:
                buildings.clear()
                for b in saved_buildings:
                    buildings.append(Building(
                        b.get("x", 0), b.get("y", 0),
                        b.get("w", 80), b.get("h", 60),
                        b.get("name", "Дом"),
                        ROOF_RED,
                        b.get("level", 1),
                        b.get("base_income", 10),
                    ))
            print("✅ Игра загружена")
        except Exception as e:
            print("⚠ Ошибка загрузки:", e)


def save_game():
    data = {"gold": player_gold, "gems": player_gems,
            "buildings": [b.to_dict() for b in buildings]}
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("💾 Игра сохранена")
    except Exception as e:
        print("⚠ Ошибка сохранения:", e)


def find_free_spot():
    """Ищет свободное место для нового здания"""
    for _ in range(100):
        x = random.randint(-350, 350)
        y = random.randint(-250, 280)
        new_rect = pygame.Rect(x, y, 80, 65)
        if not any(new_rect.colliderect(b.rect.inflate(40, 40)) for b in buildings):
            return x, y
    return random.randint(-300, 300), random.randint(-200, 250)


def draw_path(surface, cam_x, cam_y, points, width=30):
    moved = [(x + cam_x, y + cam_y) for x, y in points]
    for i in range(len(moved) - 1):
        pygame.draw.line(surface, PATH_DARK, moved[i], moved[i + 1], width + S(4))
        pygame.draw.line(surface, PATH_COLOR, moved[i], moved[i + 1], width)


def draw_river(surface, cam_x, cam_y):
    river_pts = []
    for i in range(-300, SCREEN_WIDTH + 600, S(40)):
        wave = math.sin(i * 0.01) * S(20)
        river_pts.append((i + cam_x, S(100) + wave + cam_y))
    if len(river_pts) > 1:
        pygame.draw.lines(surface, WATER_DARK, False, river_pts, S(45))
        pygame.draw.lines(surface, WATER_COLOR, False, river_pts, S(35))
        for i in range(0, len(river_pts) - 1, 3):
            mid = ((river_pts[i][0] + river_pts[i + 1][0]) // 2,
                   (river_pts[i][1] + river_pts[i + 1][1]) // 2)
            pygame.draw.circle(surface, (200, 230, 255, 100), mid, S(3))


def draw_background(surface, cam_x, cam_y):
    surface.fill(GRASS_LIGHT)
    tile = S(60)
    start_x = -(cam_x % tile) - tile
    start_y = -(cam_y % tile) - tile
    for x in range(int(start_x), SCREEN_WIDTH + tile, tile):
        for y in range(int(start_y), SCREEN_HEIGHT + tile, tile):
            gx = (x - cam_x) // tile
            gy = (y - cam_y) // tile
            if (gx + gy) % 2 == 0:
                pygame.draw.rect(surface, GRASS_DARK, (x, y, tile, tile))


def draw_top_panel(surface):
    pygame.draw.rect(surface, PANEL_DARK, (0, 0, SCREEN_WIDTH, TOP_PANEL_H))
    pygame.draw.line(surface, (80, 80, 110),
                     (0, TOP_PANEL_H), (SCREEN_WIDTH, TOP_PANEL_H), S(2))

    cy = TOP_PANEL_H // 2
    timer = font_mid.render("01:19", True, WHITE)
    surface.blit(timer, (S(10), cy - timer.get_height() // 2))

    people = font_mid.render("8/8", True, WHITE)
    surface.blit(people, (SCREEN_WIDTH * 0.18, cy - people.get_height() // 2))

    gold_x = int(SCREEN_WIDTH * 0.4)
    pygame.draw.circle(surface, GOLD, (gold_x, cy), S(9))
    pygame.draw.circle(surface, (180, 140, 30), (gold_x, cy), S(9), S(2))
    gold_str = f"{player_gold / 1000:.1f}K" if player_gold >= 1000 else str(int(player_gold))
    gold = font_mid.render(gold_str, True, GOLD)
    surface.blit(gold, (gold_x + S(15), cy - gold.get_height() // 2))

    gem_x = int(SCREEN_WIDTH * 0.75)
    diamond_pts = [(gem_x, cy - S(8)), (gem_x + S(8), cy),
                   (gem_x, cy + S(8)), (gem_x - S(8), cy)]
    pygame.draw.polygon(surface, GEM_BLUE, diamond_pts)
    pygame.draw.polygon(surface, (60, 130, 200), diamond_pts, S(2))
    gems = font_mid.render(str(int(player_gems)), True, GEM_BLUE)
    surface.blit(gems, (gem_x + S(15), cy - gems.get_height() // 2))


def get_bottom_buttons():
    """Возвращает список (rect, name) кнопок нижней панели"""
    panel_y = SCREEN_HEIGHT - BOTTOM_PANEL_H
    items = ["Завоевание", "Герои", "Замок", "Магазин", "Мир"]
    button_width = SCREEN_WIDTH // len(items)
    result = []
    for i, label in enumerate(items):
        r = pygame.Rect(i * button_width + S(4),
                        panel_y + S(8),
                        button_width - S(8),
                        BOTTOM_PANEL_H - S(16))
        result.append((r, label))
    return result


def draw_bottom_panel(surface):
    panel_y = SCREEN_HEIGHT - BOTTOM_PANEL_H
    pygame.draw.rect(surface, PANEL_DARK, (0, panel_y, SCREEN_WIDTH, BOTTOM_PANEL_H))
    pygame.draw.line(surface, (80, 80, 110),
                     (0, panel_y), (SCREEN_WIDTH, panel_y), S(2))

    for btn_rect, label in get_bottom_buttons():
        pygame.draw.rect(surface, (45, 45, 60), btn_rect, border_radius=S(8))
        pygame.draw.rect(surface, (90, 90, 120), btn_rect, S(2), border_radius=S(8))
        cx = btn_rect.centerx
        pygame.draw.circle(surface, (150, 150, 180), (cx, btn_rect.y + S(18)), S(8))
        txt = font_small.render(label, True, (220, 220, 240))
        tr = txt.get_rect(center=(cx, btn_rect.bottom - S(12)))
        surface.blit(txt, tr)


def draw_popup(surface, building):
    """Меню улучшения здания. Возвращает (btn_rect, close_rect)"""
    dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 160))
    surface.blit(dim, (0, 0))

    w = int(SCREEN_WIDTH * 0.9)
    h = int(SCREEN_HEIGHT * 0.45)
    x = (SCREEN_WIDTH - w) // 2
    y = (SCREEN_HEIGHT - h) // 2
    pygame.draw.rect(surface, (50, 50, 70), (x, y, w, h), border_radius=S(15))
    pygame.draw.rect(surface, (120, 120, 160), (x, y, w, h), S(3), border_radius=S(15))

    title = font_big.render(building.name, True, WHITE)
    surface.blit(title, title.get_rect(center=(x + w // 2, y + S(35))))

    lvl = font_mid.render(f"Уровень {building.level}", True, GOLD)
    surface.blit(lvl, lvl.get_rect(center=(x + w // 2, y + S(70))))

    pygame.draw.line(surface, (120, 120, 160),
                     (x + S(25), y + S(95)), (x + w - S(25), y + S(95)), S(2))

    cost = building.upgrade_cost()
    info_lines = [
        f"Доход: +{building.income()} в час",
        f"Следующий: +{(building.level + 1) * building.base_income} в час",
        f"Стоимость: {cost} золота",
    ]
    for i, line in enumerate(info_lines):
        txt = font_mid.render(line, True, (220, 220, 240))
        surface.blit(txt, txt.get_rect(center=(x + w // 2, y + S(135) + i * S(40))))

    btn_w = int(w * 0.75)
    btn_h = S(60)
    btn_rect = pygame.Rect(x + (w - btn_w) // 2, y + h - S(85), btn_w, btn_h)

    if player_gold >= cost:
        color, dark, label = BTN_GREEN, BTN_GREEN_DARK, "УЛУЧШИТЬ"
    else:
        color, dark, label = BTN_GREY, BTN_GREY_DARK, "НЕ ХВАТАЕТ"

    pygame.draw.rect(surface, color, btn_rect, border_radius=S(10))
    pygame.draw.rect(surface, dark, btn_rect, S(3), border_radius=S(10))
    btn_text = font_big.render(label, True, WHITE)
    surface.blit(btn_text, btn_text.get_rect(center=btn_rect.center))

    close_rect = pygame.Rect(x + w - S(45), y + S(12), S(35), S(35))
    pygame.draw.rect(surface, (180, 60, 60), close_rect, border_radius=S(8))
    pygame.draw.line(surface, WHITE, (x + w - S(36), y + S(22)),
                     (x + w - S(20), y + S(38)), S(3))
    pygame.draw.line(surface, WHITE, (x + w - S(20), y + S(22)),
                     (x + w - S(36), y + S(38)), S(3))

    return btn_rect, close_rect


def draw_shop(surface):
    """Магазин. Возвращает (list_of_item_rects, close_rect)"""
    dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 170))
    surface.blit(dim, (0, 0))

    w = int(SCREEN_WIDTH * 0.92)
    h = int(SCREEN_HEIGHT * 0.7)
    x = (SCREEN_WIDTH - w) // 2
    y = (SCREEN_HEIGHT - h) // 2
    pygame.draw.rect(surface, (50, 50, 70), (x, y, w, h), border_radius=S(15))
    pygame.draw.rect(surface, (120, 120, 160), (x, y, w, h), S(3), border_radius=S(15))

    title = font_big.render("🏪 МАГАЗИН", True, WHITE)
    surface.blit(title, title.get_rect(center=(x + w // 2, y + S(35))))

    pygame.draw.line(surface, (120, 120, 160),
                     (x + S(25), y + S(60)), (x + w - S(25), y + S(60)), S(2))

    item_rects = []
    item_h = S(75)
    start_y = y + S(75)
    padding = S(15)

    for i, item in enumerate(SHOP_CATALOG):
        item_y = start_y + i * (item_h + padding)
        item_rect = pygame.Rect(x + S(20), item_y, w - S(40), item_h)
        item_rects.append(item_rect)

        affordable = player_gold >= item["cost"]
        bg_color = (70, 90, 60) if affordable else (70, 50, 50)
        border_color = (120, 180, 120) if affordable else (150, 90, 90)

        pygame.draw.rect(surface, bg_color, item_rect, border_radius=S(10))
        pygame.draw.rect(surface, border_color, item_rect, S(2), border_radius=S(10))

        # Иконка-домик слева
        icon_rect = pygame.Rect(item_rect.x + S(15),
                                item_rect.y + S(12),
                                S(40), item_rect.height - S(24))
        pygame.draw.rect(surface, WOOD_WALL, icon_rect, border_radius=S(4))
        roof_pts = [(icon_rect.x - S(4), icon_rect.y),
                    (icon_rect.centerx, icon_rect.y - S(15)),
                    (icon_rect.right + S(4), icon_rect.y)]
        pygame.draw.polygon(surface, item["color"], roof_pts)

        # Название
        name_txt = font_mid.render(item["name"], True, WHITE)
        surface.blit(name_txt, (item_rect.x + S(75),
                                item_rect.y + S(12)))

        # Доход и цена
        info_txt = font_small.render(
            f"+{item['income']} в час  |  {item['cost']} золота",
            True, (220, 220, 240))
        surface.blit(info_txt, (item_rect.x + S(75),
                                item_rect.y + S(40)))

        # Кнопка "КУПИТЬ"
        buy_rect = pygame.Rect(item_rect.right - S(110),
                               item_rect.y + S(15),
                               S(95), item_rect.height - S(30))
        if affordable:
            pygame.draw.rect(surface, BTN_BLUE, buy_rect, border_radius=S(8))
            pygame.draw.rect(surface, BTN_BLUE_DARK, buy_rect, S(2), border_radius=S(8))
            buy_txt = font_mid.render("КУПИТЬ", True, WHITE)
        else:
            pygame.draw.rect(surface, BTN_GREY, buy_rect, border_radius=S(8))
            pygame.draw.rect(surface, BTN_GREY_DARK, buy_rect, S(2), border_radius=S(8))
            buy_txt = font_small.render("МАЛО ЗОЛОТА", True, WHITE)

        surface.blit(buy_txt, buy_txt.get_rect(center=buy_rect.center))
        item_rects[i] = (item_rect, buy_rect, item)

    close_rect = pygame.Rect(x + w - S(45), y + S(12), S(35), S(35))
    pygame.draw.rect(surface, (180, 60, 60), close_rect, border_radius=S(8))
    pygame.draw.line(surface, WHITE, (x + w - S(36), y + S(22)),
                     (x + w - S(20), y + S(38)), S(3))
    pygame.draw.line(surface, WHITE, (x + w - S(20), y + S(22)),
                     (x + w - S(36), y + S(38)), S(3))

    return item_rects, close_rect


def draw_notification(surface, text, timer):
    if timer <= 0:
        return
    alpha = min(255, timer * 4)
    w = int(SCREEN_WIDTH * 0.9)
    h = S(50)
    x = (SCREEN_WIDTH - w) // 2
    y = SCREEN_HEIGHT - BOTTOM_PANEL_H - S(80)

    bg = pygame.Surface((w, h), pygame.SRCALPHA)
    bg.fill((30, 30, 40, alpha))
    surface.blit(bg, (x, y))
    pygame.draw.rect(surface, (100, 200, 100, alpha),
                     (x, y, w, h), S(2), border_radius=S(10))

    txt = font_mid.render(text, True, (255, 255, 255))
    surface.blit(txt, txt.get_rect(center=(x + w // 2, y + h // 2)))


# --- Данные ---
buildings = [
    Building(-90, -90, 80, 65, "Ратуша", ROOF_RED, 2, 10),
    Building(120, -130, 75, 60, "Лесопилка", ROOF_BROWN, 1, 10),
    Building(180, 40, 75, 60, "Ферма", ROOF_RED, 3, 10),
    Building(-180, 80, 80, 65, "Казарма", ROOF_BROWN, 1, 10),
    Building(120, 160, 75, 60, "Шахта", ROOF_BROWN, 2, 10),
]

trees = []
random.seed(42)
for _ in range(35):
    x = random.randint(-350, 350)
    y = random.randint(-220, 280)
    if not any(abs(x - b.rect.x) < 120 and abs(y - b.rect.y) < 100 for b in buildings):
        trees.append(Tree(x, y, random.randint(18, 32)))

path_points = [(-90, -50), (120, -90), (180, 90), (-180, 130), (120, 210)]

cam_x = SCREEN_WIDTH // 2
cam_y = SCREEN_HEIGHT // 2

dragging = False
last_mouse_x = 0
last_mouse_y = 0
selected_building = None
shop_open = False
mouse_down_pos = None
notification_text = ""
notification_timer = 0


def main():
    global cam_x, cam_y, dragging, last_mouse_x, last_mouse_y
    global selected_building, shop_open, mouse_down_pos
    global player_gold, notification_text, notification_timer, gold_income_timer

    load_game()

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game()
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
                    is_tap = dx < S(12) and dy < S(12)

                    if is_tap:
                        # 1. Магазин открыт?
                        if shop_open:
                            item_rects, close_rect = draw_shop(screen)
                            if close_rect.collidepoint(event.pos):
                                shop_open = False
                            else:
                                for item_rect, buy_rect, item in item_rects:
                                    if buy_rect.collidepoint(event.pos):
                                        if player_gold >= item["cost"]:
                                            player_gold -= item["cost"]
                                            nx, ny = find_free_spot()
                                            new_b = Building(
                                                nx, ny, 80, 65,
                                                item["name"], item["color"],
                                                1, item["income"]
                                            )
                                            buildings.append(new_b)
                                            notification_text = f"Куплено: {item['name']}!"
                                            notification_timer = 120
                                            save_game()
                                        else:
                                            notification_text = "Недостаточно золота!"
                                            notification_timer = 120
                                        break

                        # 2. Меню улучшения открыто?
                        elif selected_building:
                            btn_rect, close_rect = draw_popup(screen, selected_building)
                            if close_rect.collidepoint(event.pos):
                                selected_building = None
                            elif btn_rect.collidepoint(event.pos):
                                cost = selected_building.upgrade_cost()
                                if player_gold >= cost:
                                    player_gold -= cost
                                    selected_building.level += 1
                                    notification_text = f"{selected_building.name} → ур. {selected_building.level}!"
                                    notification_timer = 120
                                    save_game()
                                else:
                                    notification_text = "Недостаточно золота!"
                                    notification_timer = 120

                        # 3. Тап по нижней панели
                        else:
                            bottom_y = SCREEN_HEIGHT - BOTTOM_PANEL_H
                            if event.pos[1] >= bottom_y:
                                for btn_rect, label in get_bottom_buttons():
                                    if btn_rect.collidepoint(event.pos):
                                        if label == "Магазин":
                                            shop_open = True
                                        break
                            elif TOP_PANEL_H < event.pos[1] < bottom_y:
                                # Тап по зданию
                                for b in buildings:
                                    if b.hit(event.pos, cam_x, cam_y):
                                        selected_building = b
                                        break

                    mouse_down_pos = None

            elif event.type == pygame.MOUSEMOTION and dragging:
                if not selected_building and not shop_open:
                    if mouse_down_pos and TOP_PANEL_H < mouse_down_pos[1] < SCREEN_HEIGHT - BOTTOM_PANEL_H:
                        dx = event.pos[0] - last_mouse_x
                        dy = event.pos[1] - last_mouse_y
                        cam_x += dx
                        cam_y += dy
                        last_mouse_x, last_mouse_y = event.pos

        gold_income_timer += 1
        if gold_income_timer >= 60:
            gold_income_timer = 0
            player_gold += sum(b.income() for b in buildings)

        if notification_timer > 0:
            notification_timer -= 1

        # --- Отрисовка ---
        draw_background(screen, cam_x, cam_y)
        draw_river(screen, cam_x, cam_y)

        for i in range(len(path_points) - 1):
            draw_path(screen, cam_x, cam_y,
                      [path_points[i], path_points[i + 1]], S(30))

        for t in sorted(trees, key=lambda t: t.y):
            t.draw(screen, cam_x, cam_y)

        for b in buildings:
            b.draw(screen, cam_x, cam_y)

        draw_top_panel(screen)
        draw_bottom_panel(screen)

        if selected_building:
            draw_popup(screen, selected_building)

        if shop_open:
            draw_shop(screen)

        if notification_timer > 0:
            draw_notification(screen, notification_text, notification_timer)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
