"""Fabriques de dibuixos. Cada funcio torna una Surface ja feta i guardada.

Res d'aqui no es torna a dibuixar mai: la primera crida el pinta, la resta
nomes el recupera de `cache`. Aixo es el que fa que el joc vagi rapid al web.
"""

import math
import pygame

from . import cache
from .config import (W, H, GROUND, HOLE_X0, HOLE_X1, GRASS, DIRT, SKIN, FUR,
                     SKY_OF, CLOUD_OF)

d = pygame.draw

GOLD_STEPS = 36          # fotogrames del 67 abans de repetir-se
SUN_STEPS = 12
STAR_STEPS = 4
CAVEMAN_PAD = 30


def lerp_color(a, b, k):
    return (int(a[0] + (b[0] - a[0]) * k),
            int(a[1] + (b[1] - a[1]) * k),
            int(a[2] + (b[2] - a[2]) * k))


def star_points(center, size):
    x, y = center
    q = size // 4
    return [(x, y - size), (x + q, y - q), (x + size, y), (x + q, y + q),
            (x, y + size), (x - q, y + q), (x - size, y), (x - q, y - q)]


def draw_star(screen, center, size, color):
    d.polygon(screen, color, star_points(center, size))


# ---------------------------------------------------------------- fruites --

def _make_fruit(kind):
    K = 5
    surf = cache.new_surface((120, 120))
    cx = cy = 60
    leaf = (50, 160, 60)

    def P(x, y):
        return (cx + x * K, cy + y * K)

    def E(x, y, w, h):
        return (cx + x * K, cy + y * K, w * K, h * K)

    face_y = 1
    if kind == 0:                                  # poma
        d.circle(surf, (215, 40, 40), P(0, 1), 11 * K)
        d.line(surf, (90, 60, 30), P(0, -9), P(2, -13), 2 * K)
        d.ellipse(surf, leaf, E(2, -13, 8, 5))
        d.circle(surf, (245, 110, 110), P(-6, -3), 2 * K)
    elif kind == 1:                                # platan
        d.arc(surf, (250, 220, 60), E(-12, -12, 24, 24), 3.3, 6.1, 9 * K)
        d.line(surf, (110, 80, 30), P(-11, 2), P(-12, -3), 3 * K)
        face_y = 6
    elif kind == 2:                                # raim
        for dx, dy in [(-5, -4), (5, -4), (0, -4), (-3, 2), (3, 2), (0, 8)]:
            d.circle(surf, (150, 70, 180), P(dx, dy), 5 * K)
        d.ellipse(surf, leaf, E(-1, -13, 8, 5))
        face_y = 0
    elif kind == 3:                                # taronja
        d.circle(surf, (255, 150, 30), P(0, 1), 11 * K)
        d.ellipse(surf, leaf, E(0, -13, 8, 5))
        d.circle(surf, (255, 195, 100), P(-6, -3), 2 * K)
    else:                                          # maduixa
        red = (235, 55, 85)
        d.polygon(surf, red, [P(-10, -5), P(10, -5), P(0, 12)])
        d.circle(surf, red, P(-5, -4), 6 * K)
        d.circle(surf, red, P(5, -4), 6 * K)
        d.polygon(surf, leaf, [P(-7, -10), P(7, -10), P(0, -4)])
    ex = 3.2 if kind != 1 else 2.6                 # cara maca
    for sx in (-1, 1):
        d.circle(surf, (40, 25, 25), P(sx * ex, face_y - 1), int(1.7 * K))
        d.circle(surf, (255, 255, 255), P(sx * ex + 0.6, face_y - 1.7), int(0.7 * K))
        d.circle(surf, (255, 140, 160), P(sx * (ex + 3.2), face_y + 2), int(1.5 * K))
    d.arc(surf, (60, 25, 25), E(-2, face_y, 4, 3), 3.5, 5.9, int(0.7 * K) + 1)
    return pygame.transform.smoothscale(surf, (34, 34))


def fruit(kind):
    return cache.sprite(("fruit", kind), lambda: _make_fruit(kind))


def _make_gold(i):
    """El 67: moneda, halo i espurnes. 36 variants que fan un bucle perfecte."""
    surf = cache.new_surface((130, 130))
    cx = cy = 65
    pulse = math.sin(2 * math.pi * i / 18.0)
    for rad, alpha in ((52, 25), (42, 40), (34, 60)):
        d.circle(surf, (255, 220, 80, alpha), (cx, cy), int(rad + 3 * pulse))
    R = 21 + int(pulse)
    d.circle(surf, (150, 90, 10), (cx, cy + 2), R + 2)
    d.circle(surf, (255, 190, 30), (cx, cy), R + 1)
    d.circle(surf, (255, 225, 90), (cx, cy), R - 4)
    d.circle(surf, (255, 205, 50), (cx, cy + 2), R - 7)
    d.circle(surf, (215, 140, 20), (cx, cy), R + 1, 2)
    d.ellipse(surf, (255, 250, 200), (cx - R + 6, cy - R + 5, 11, 6))
    f = cache.font(34)
    txt = f.render("67", True, (120, 60, 0))
    shine = f.render("67", True, (255, 245, 190))
    surf.blit(txt, txt.get_rect(center=(cx + 1, cy + 3)))
    surf.blit(shine, shine.get_rect(center=(cx, cy + 2)))
    surf.blit(txt, txt.get_rect(center=(cx, cy + 1)))
    for k in range(4):
        a = 2 * math.pi * i / GOLD_STEPS + k * math.pi / 2
        px = cx + int(math.cos(a) * (R + 9))
        py = cy + int(math.sin(a) * (R + 9))
        draw_star(surf, (px, py), 4 + int(2 * math.sin(2 * math.pi * i / 12.0 + k * 2)), (255, 255, 220))
    return surf


def gold(step):
    return cache.pick(cache.steps_of("gold67", GOLD_STEPS, _make_gold), step)


# ---------------------------------------------------------------- mamut ----

def _make_mammoth(phase):
    surf = cache.new_surface((170, 130))
    fur, dark, light = (112, 70, 42), (78, 46, 26), (150, 100, 62)
    gy = 126
    for lx, up in ((34, phase), (58, 1 - phase), (96, 1 - phase), (120, phase)):
        top, bot = 74, gy - 7 * up
        d.rect(surf, dark if lx in (34, 96) else fur, (lx, top, 24, bot - top), border_radius=8)
        d.ellipse(surf, (235, 225, 200), (lx - 1, bot - 9, 26, 11))
        d.ellipse(surf, (200, 190, 165), (lx + 3, bot - 5, 18, 6))
    d.line(surf, dark, (20, 62), (8, 86), 4)
    d.polygon(surf, dark, [(8, 82), (2, 98), (14, 94)])
    d.ellipse(surf, fur, (14, 30, 118, 72))
    d.ellipse(surf, light, (30, 66, 86, 30))
    for i in range(7):
        x = 24 + i * 15
        dy = abs(i - 3) * 2
        d.polygon(surf, dark, [(x, 40 + dy), (x + 9, 28 + dy), (x + 15, 42 + dy)])
    for i in range(6):
        x = 28 + i * 15
        d.polygon(surf, dark, [(x, 94), (x + 6, 112), (x + 13, 94)])
    d.ellipse(surf, fur, (96, 22, 62, 64))
    for px, py in [(104, 24), (116, 16), (130, 16), (143, 22)]:
        d.polygon(surf, dark, [(px - 7, py + 12), (px + 2, py - 12), (px + 9, py + 12)])
    d.ellipse(surf, dark, (84, 36, 30, 44))
    d.ellipse(surf, (200, 120, 110), (90, 44, 17, 28))
    pts = [(142 + 16 * math.sin(i / 14 * 2.4) * 0.9, 58 + 62 * i / 14) for i in range(15)]
    for i, (x, y) in enumerate(pts):
        d.circle(surf, fur, (int(x), int(y)), int(10 - i * 0.35))
    for i in range(0, 15, 3):
        x, y = pts[i]
        d.arc(surf, dark, (int(x) - 8, int(y) - 3, 16, 7), 3.3, 6.1, 2)
    for sx in (0, 12):
        for i in range(26):
            t = i / 25
            x = 134 + sx * 0.3 + 40 * t * (1 - 0.35 * t)
            y = 80 + 6 * math.sin(t * 2) - 46 * t * t + sx * 0.3
            d.circle(surf, (252, 248, 232) if sx == 0 else (232, 225, 205),
                     (int(x), int(y)), max(3, int(6 - 4 * t)))
    d.circle(surf, (255, 255, 255), (131, 50), 9)
    d.circle(surf, (200, 30, 30), (134, 51), 5)
    d.circle(surf, (0, 0, 0), (135, 51), 3)
    d.circle(surf, (255, 255, 255), (136, 49), 1)
    d.polygon(surf, (40, 20, 10), [(119, 34), (122, 30), (145, 46), (141, 51)])
    d.circle(surf, (200, 100, 90), (122, 64), 5)
    return pygame.transform.smoothscale(surf, (105, 80))


def mammoth(phase, facing):
    """Les 4 combinacions (2 passes x 2 direccions) ja girades."""
    def build():
        img = _make_mammoth(phase)
        return pygame.transform.flip(img, True, False) if facing < 0 else img
    return cache.sprite(("mammoth", phase, 1 if facing >= 0 else -1), build)


def shadow(width, height=10, alpha=60):
    def build():
        s = cache.new_surface((width, height))
        d.ellipse(s, (0, 0, 0, alpha), (0, 0, width, height))
        return s
    return cache.sprite(("shadow", width, height, alpha), build)


# ------------------------------------------------------------ cavernicola --

def caveman(facing, swing, on_ground, celebrate_up, club):
    """El cavernicola ja pintat. La clau cobreix totes les postures possibles."""
    key = ("caveman", facing, swing, on_ground, celebrate_up, club)

    def build():
        pad = CAVEMAN_PAD
        surf = cache.new_surface((30 + pad * 2, 50 + pad * 2))
        x = y = pad
        cx = x + 15
        d.rect(surf, SKIN, (cx - 9 + swing // 2, y + 40, 7, 10))
        d.rect(surf, SKIN, (cx + 2 - swing // 2, y + 40, 7, 10))
        hand_y = y + 28 - (10 if not on_ground else 0)
        if celebrate_up is None and club:
            d.line(surf, (100, 65, 30), (cx + 10 * facing, hand_y), (cx + 24 * facing, hand_y - 16), 5)
            d.circle(surf, (100, 65, 30), (cx + 24 * facing, hand_y - 16), 6)
        d.rect(surf, FUR, (x, y + 22, 30, 20), border_radius=4)
        for i in range(4):
            px = x + 2 + i * 8
            d.polygon(surf, FUR, [(px, y + 40), (px + 6, y + 40), (px + 3, y + 47)])
        if celebrate_up is not None:
            for side, hand_up in ((-1, celebrate_up), (1, not celebrate_up)):
                hx = cx + side * 24
                hy = y - 6 if hand_up else y + 46
                d.line(surf, SKIN, (cx + side * 12, y + 27), (hx, hy), 7)
                d.circle(surf, SKIN, (hx, hy), 7)
        else:
            d.circle(surf, SKIN, (cx + 8 * facing, hand_y), 5)
        d.circle(surf, SKIN, (cx, y + 12), 14)
        d.arc(surf, (60, 35, 15), (cx - 15, y - 3, 30, 24), 0, 3.15, 8)
        ex = cx + 5 * facing
        d.circle(surf, (255, 255, 255), (ex, y + 11), 4)
        d.circle(surf, (0, 0, 0), (ex + facing, y + 11), 2)
        if celebrate_up is not None:
            d.ellipse(surf, (150, 60, 50), (cx + 1 * facing - 4, y + 17, 10, 7))
        else:
            d.arc(surf, (150, 60, 50), (cx + 1 * facing - 4, y + 12, 10, 8), 3.4, 6.0, 2)
        return surf

    return cache.sprite(key, build)


# ----------------------------------------------------------- plataformes ---

PLAT_W, PLAT_H = 140, 18
PLAT_PAD_X, PLAT_PAD_TOP, PLAT_PAD_BOT = 10, 12, 20


def platform():
    """Plataforma sencera (ombra, arrels, pedra, herba i floretes) en 1 blit."""
    def build():
        surf = cache.new_surface((PLAT_W + PLAT_PAD_X * 2, PLAT_H + PLAT_PAD_TOP + PLAT_PAD_BOT))
        r = pygame.Rect(PLAT_PAD_X, PLAT_PAD_TOP, PLAT_W, PLAT_H)
        d.ellipse(surf, (0, 0, 0, 50), (r.x + 6, r.bottom + 6, r.w - 12, 10))
        for i, off in enumerate((18, 52, 90, 122)):
            x = r.x + off
            ln = 8 + (i * 5) % 11
            d.line(surf, (95, 65, 40), (x, r.bottom - 3), (x - 2, r.bottom + ln), 3)
            d.line(surf, (95, 65, 40), (x - 2, r.bottom + ln // 2), (x + 4, r.bottom + ln - 2), 2)
        d.rect(surf, (140, 125, 110), r, border_radius=9)
        d.rect(surf, (112, 98, 86), (r.x, r.centery + 2, r.w, r.h // 2 - 2),
               border_bottom_left_radius=9, border_bottom_right_radius=9)
        for row, yy in enumerate((r.y + 9, r.y + 15)):
            for x in range(r.x + 10 + (row % 2) * 12, r.right - 8, 24):
                d.line(surf, (100, 88, 76), (x, yy - 5 if row == 0 else yy - 4), (x, yy), 1)
        d.line(surf, (100, 88, 76), (r.x + 4, r.y + 10), (r.right - 4, r.y + 10), 1)
        d.rect(surf, (80, 68, 58), r, 2, border_radius=9)
        d.rect(surf, (85, 185, 75), (r.x - 2, r.y - 4, r.w + 4, 10), border_radius=5)
        d.rect(surf, (120, 215, 95), (r.x + 2, r.y - 4, r.w - 4, 3), border_radius=2)
        for x in range(r.x + 2, r.right - 6, 11):
            d.circle(surf, (85, 185, 75), (x + 4, r.y + 6), 5)
        for x in range(r.x + 8, r.right - 6, 17):
            d.polygon(surf, (60, 160, 60), [(x, r.y - 4), (x + 2, r.y - 10), (x + 4, r.y - 4)])
        for x, col in ((r.x + 28, (255, 120, 160)), (r.x + 78, (255, 220, 70)), (r.x + 114, (255, 255, 255))):
            d.line(surf, (50, 140, 50), (x, r.y - 4), (x, r.y - 9), 2)
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                d.circle(surf, col, (x + dx, r.y - 11 + dy), 2)
            d.circle(surf, (255, 170, 40), (x, r.y - 11), 1)
        return surf
    return cache.sprite("platform", build)


def platform_origin(rect):
    return (rect.x - PLAT_PAD_X, rect.y - PLAT_PAD_TOP)


# ---------------------------------------------------------------- terra ----

def ground_layer():
    """Herba, terra i el forat: tot el que hi ha de GROUND cap avall, en 1 blit."""
    def build():
        h = H - GROUND
        surf = cache.new_surface((W, h))
        d.rect(surf, GRASS, (0, 0, W, 14))
        d.rect(surf, DIRT, (0, 14, W, h))
        w = HOLE_X1 - HOLE_X0
        d.rect(surf, (25, 15, 30), (HOLE_X0, 0, w, h))
        for i in range(6):
            d.rect(surf, (45 - i * 6, 28 - i * 3, 40 - i * 5), (HOLE_X0, 4 + i * 8, w, 8))
        d.rect(surf, (25, 15, 30), (HOLE_X0, 40, w, h))
        d.rect(surf, (80, 55, 35), (HOLE_X0 - 6, 14, 6, h))
        d.rect(surf, (80, 55, 35), (HOLE_X1, 14, 6, h))
        d.rect(surf, GRASS, (HOLE_X0 - 10, 0, 10, 14), border_top_left_radius=6, border_bottom_left_radius=6)
        d.rect(surf, GRASS, (HOLE_X1, 0, 10, 14), border_top_right_radius=6, border_bottom_right_radius=6)
        return surf
    return cache.sprite("ground", build)


# ------------------------------------------------------------------ cel ---

def sun(step):
    def build(i):
        surf = cache.new_surface((170, 170))
        sx = sy = 85
        base = i * (math.pi / 6) / SUN_STEPS
        for k in range(12):
            a = base + k * math.pi / 6
            d.line(surf, (255, 235, 120), (sx + math.cos(a) * 52, sy + math.sin(a) * 52),
                   (sx + math.cos(a) * 78, sy + math.sin(a) * 78), 6)
        d.circle(surf, (255, 240, 150), (sx, sy), 54)
        d.circle(surf, (255, 215, 60), (sx, sy), 44)
        d.circle(surf, (255, 235, 130), (sx - 12, sy - 14), 12)
        for ex in (-14, 14):
            d.circle(surf, (120, 70, 20), (sx + ex, sy - 6), 4)
        d.arc(surf, (120, 70, 20), (sx - 15, sy - 2, 30, 22), 3.5, 5.9, 3)
        d.circle(surf, (255, 150, 90), (sx - 25, sy + 6), 6)
        d.circle(surf, (255, 150, 90), (sx + 25, sy + 6), 6)
        return surf
    return cache.pick(cache.steps_of("sun", SUN_STEPS, build), step)


def night_sky(step):
    def build(i):
        surf = cache.new_surface((W, GROUND))
        for k in range(45):
            x = (k * 211) % W
            y = (k * 97) % (GROUND - 160) + 10
            r = 1 + int(1.5 * abs(math.sin(2 * math.pi * i / STAR_STEPS + k)))
            d.circle(surf, (255, 255, 225), (x, y), r)
        mx, my = W - 130, 95
        d.circle(surf, (250, 245, 205), (mx, my), 42)
        d.circle(surf, SKY_OF["nit"], (mx + 18, my - 8), 36)
        d.circle(surf, (225, 220, 175), (mx - 22, my + 14), 5)
        d.circle(surf, (225, 220, 175), (mx - 12, my - 18), 3)
        return surf
    return cache.pick(cache.steps_of("night", STAR_STEPS, build), step)


def cloud(weather, k):
    def build():
        r = int(26 * k)
        surf = cache.new_surface((int(6 * r), int(4 * r)))
        cx, cy = int(3 * r), int(2 * r)
        color = CLOUD_OF[weather]
        shade = lerp_color(color, (120, 140, 170), 0.2)
        for dx, dy, rr in ((-1.4, 0.5, 0.8), (-0.6, -0.2, 1.1), (0.5, -0.4, 1.3),
                           (1.4, 0.3, 0.9), (0.2, 0.5, 1.0)):
            d.circle(surf, color, (int(cx + dx * r), int(cy + dy * r)), int(rr * r))
        d.rect(surf, color, (int(cx - 1.8 * r), int(cy + 0.5 * r), int(3.8 * r), int(0.9 * r)),
               border_radius=int(0.4 * r))
        d.rect(surf, shade, (int(cx - 1.7 * r), int(cy + 1.1 * r), int(3.6 * r), int(0.3 * r)),
               border_radius=int(0.15 * r))
        return surf
    return cache.sprite(("cloud", weather, k), build)


def darken(screen, amount):
    """Enfosqueix tota la pantalla. Un `fill` amb BLEND_MULT es ~10 vegades
    mes rapid que blitejar una Surface amb alfa, i amb negre dona el mateix."""
    k = 255 - amount
    screen.fill((k, k, k), special_flags=pygame.BLEND_MULT)


def tint(screen, mult):
    """Tenyeix tota la pantalla multiplicant (vel de color, pero barat)."""
    screen.fill(mult, special_flags=pygame.BLEND_MULT)


def draw_rain(screen, frames):
    """140 ratlles. Mesurat: mes barat que moure una capa de pantalla sencera."""
    for i in range(140):
        x = (i * 97 + frames * 3) % (W + 60) - 30
        y = (i * 53 + frames * 16) % H
        d.line(screen, (190, 215, 245), (x, y), (x - 5, y + 14), 2)


def draw_snow(screen, frames):
    for i in range(90):
        x = (i * 131 + math.sin(frames * 0.03 + i) * 25) % W
        y = (i * 71 + frames * (1.5 + i % 3 * 0.5)) % H
        d.circle(screen, (255, 255, 255), (int(x), int(y)), 2 + i % 3)


# -------------------------------------------------------------- objectes ---

def steak():
    """Un bistec: 10 bistecs fan una vida."""
    def build():
        surf = cache.new_surface((34, 28))
        d.ellipse(surf, (170, 50, 55), (2, 4, 30, 21))
        d.ellipse(surf, (205, 80, 80), (6, 7, 21, 13))
        d.ellipse(surf, (240, 235, 220), (22, 5, 10, 18))
        d.arc(surf, (120, 30, 35), (3, 5, 28, 19), 0, 6.3, 2)
        d.circle(surf, (245, 190, 185), (12, 12), 2)
        d.circle(surf, (245, 190, 185), (17, 16), 2)
        return surf
    return cache.sprite("steak", build)


def heart(full=True):
    def build():
        surf = cache.new_surface((30, 28))
        body = (235, 60, 70) if full else (90, 70, 75)
        glint = (255, 150, 160) if full else (120, 100, 105)
        d.circle(surf, body, (9, 10), 8)
        d.circle(surf, body, (21, 10), 8)
        d.polygon(surf, body, [(1, 12), (29, 12), (15, 27)])
        d.circle(surf, glint, (7, 8), 3)
        return surf
    return cache.sprite(("heart", full), build)


# ----------------------------------------------------------------- armes ---

def _club():
    surf = cache.new_surface((50, 50))
    d.line(surf, (100, 65, 30), (12, 38), (36, 12), 7)
    d.circle(surf, (120, 78, 36), (37, 11), 9)
    d.circle(surf, (150, 105, 55), (34, 8), 3)
    return surf


def club():
    return cache.sprite("club", _club)


def club_rotated(degrees):
    return cache.rotated("club", _club, degrees)


def _spear():
    surf = cache.new_surface((64, 16))
    d.line(surf, (120, 80, 40), (2, 8), (50, 8), 4)
    d.polygon(surf, (190, 195, 205), [(44, 1), (63, 8), (44, 15)])
    d.polygon(surf, (235, 240, 245), [(46, 4), (58, 8), (46, 8)])
    d.line(surf, (200, 60, 60), (6, 4), (10, 8), 2)
    d.line(surf, (200, 60, 60), (6, 12), (10, 8), 2)
    return surf


def spear():
    return cache.sprite("spear", _spear)


def spear_rotated(degrees):
    return cache.rotated("spear", _spear, degrees)


def stone():
    def build():
        surf = cache.new_surface((34, 20))
        for k in range(4, 0, -1):            # estela cap enrere
            d.circle(surf, (255, 255, 255, 90 - k * 18), (26 - k * 6, 10), 6 - k)
        d.circle(surf, (95, 95, 105), (26, 10), 8)
        d.circle(surf, (140, 140, 150), (24, 8), 6)
        d.circle(surf, (200, 200, 210), (23, 7), 2)
        return surf
    return cache.sprite("stone", build)


def arrow():
    def build():
        surf = cache.new_surface((60, 16))
        cx, cy = 36, 8
        d.line(surf, (150, 105, 55), (cx - 26, cy), (cx + 8, cy), 3)
        d.polygon(surf, (195, 200, 210), [(cx + 16, cy), (cx + 6, cy - 5), (cx + 6, cy + 5)])
        for off in (0, 6):
            d.line(surf, (210, 60, 60), (cx - 26 + off, cy), (cx - 31 + off, cy - 5), 2)
            d.line(surf, (210, 60, 60), (cx - 26 + off, cy), (cx - 31 + off, cy + 5), 2)
        return surf
    return cache.sprite("arrow", build)


def boulder(step, steps=16):
    def build(i):
        surf = cache.new_surface((56, 56))
        x = y = 28
        r = 24
        a = i * 2 * math.pi / steps
        d.circle(surf, (95, 90, 85), (x, y), r)
        d.circle(surf, (135, 128, 120), (x - 4, y - 4), r - 6)
        for k in range(3):
            aa = a + k * 2.1
            d.line(surf, (70, 66, 62), (x + math.cos(aa) * 4, y + math.sin(aa) * 4),
                   (x + math.cos(aa) * (r - 4), y + math.sin(aa) * (r - 4)), 3)
        d.circle(surf, (160, 155, 148), (x - 9, y - 10), 4)
        return surf
    return cache.pick(cache.steps_of(("boulder", steps), steps, build), step)


def fireball(step, ice=False, steps=6):
    def build(i):
        surf = cache.new_surface((60, 40))
        x, y = 42, 18
        f = int(2 * math.sin(2 * math.pi * i / steps))
        if ice:
            for k in range(4, 0, -1):
                d.circle(surf, (170 + k * 15, 225, 255), (x - k * 7, y + k * 2), max(2, 11 - k * 2))
            d.circle(surf, (90, 170, 235), (x, y), 14 + f)
            d.circle(surf, (170, 225, 255), (x - 2, y - 2), 10)
            d.line(surf, (255, 255, 255), (x - 8, y), (x + 8, y), 2)
            d.line(surf, (255, 255, 255), (x, y - 8), (x, y + 8), 2)
            d.circle(surf, (255, 255, 255), (x - 5, y - 6), 3)
        else:
            for k in range(4, 0, -1):
                d.circle(surf, (255, 140 + k * 20, 30), (x - k * 8, y + k * 2), max(2, 11 - k * 2))
            d.circle(surf, (255, 110, 20), (x, y), 13 + f)
            d.circle(surf, (255, 200, 50), (x, y), 9)
            d.circle(surf, (255, 250, 190), (x, y), 4)
        return surf
    return cache.pick(cache.steps_of(("fireball", ice, steps), steps, build), step)


def tornado(step, steps=12):
    def build(i):
        surf = cache.new_surface((120, 140))
        cx, base_y = 60, 132
        for k in range(9):
            w_ = 16 + k * 7
            y = base_y - 8 - k * 13
            sway = math.sin(2 * math.pi * i / steps + k * 0.8) * (4 + k)
            d.ellipse(surf, (165, 175, 190), (int(cx - w_ / 2 + sway), y, w_, 10))
            d.ellipse(surf, (225, 232, 240), (int(cx - w_ / 2 + sway), y, w_, 10), 2)
        for k in range(4):
            a = 2 * math.pi * i / steps + k * 1.6
            d.circle(surf, (110, 170, 90),
                     (int(cx + math.cos(a) * 38), int(base_y - 30 - k * 22 + math.sin(a) * 6)), 3)
        return surf
    return cache.pick(cache.steps_of(("tornado", steps), steps, build), step)


def slingshot():
    def build():
        surf = cache.new_surface((44, 36))
        bx, by = 28, 18
        d.line(surf, (100, 65, 30), (bx, by + 12), (bx, by), 5)
        d.line(surf, (100, 65, 30), (bx, by), (bx - 6, by - 12), 4)
        d.line(surf, (100, 65, 30), (bx, by), (bx + 6, by - 12), 4)
        d.line(surf, (200, 60, 60), (bx - 6, by - 12), (bx - 14, by - 4), 2)
        d.line(surf, (200, 60, 60), (bx + 6, by - 12), (bx - 14, by - 4), 2)
        d.circle(surf, (130, 130, 135), (bx - 14, by - 4), 5)
        return surf
    return cache.sprite("slingshot", build)
