import os
import asyncio
import sys
import json
import math
import random
import pygame

W, H = 1000, 600
FPS = 45
GROUND = H - 60
HOLE_X0, HOLE_X1 = W // 2 - 70, W // 2 + 70  # el forat del terra


def ground_x(lo=60, hi=None):
    """Un lloc del terra que no sigui el forat."""
    hi = W - 90 if hi is None else hi
    while True:
        x = random.randint(lo, hi)
        if not (HOLE_X0 - 30 < x < HOLE_X1 + 30):
            return x

SKY = (120, 190, 235)
GRASS = (70, 150, 70)
DIRT = (110, 80, 50)
SKIN = (235, 190, 150)
FUR = (150, 100, 50)
FOOD = (220, 60, 50)


_fruit_cache = {}


def make_fruit(kind):
    K = 5
    surf = pygame.Surface((120, 120), pygame.SRCALPHA)
    cx = cy = 60
    leaf = (50, 160, 60)
    d = pygame.draw

    def P(x, y):
        return (cx + x * K, cy + y * K)

    def E(x, y, w, h):
        return (cx + x * K, cy + y * K, w * K, h * K)

    face_y = 1
    if kind == 0:  # poma
        d.circle(surf, (215, 40, 40), P(0, 1), 11 * K)
        d.line(surf, (90, 60, 30), P(0, -9), P(2, -13), 2 * K)
        d.ellipse(surf, leaf, E(2, -13, 8, 5))
        d.circle(surf, (245, 110, 110), P(-6, -3), 2 * K)
    elif kind == 1:  # platan
        d.arc(surf, (250, 220, 60), E(-12, -12, 24, 24), 3.3, 6.1, 9 * K)
        d.line(surf, (110, 80, 30), P(-11, 2), P(-12, -3), 3 * K)
        face_y = 6
    elif kind == 2:  # raim
        for dx, dy in [(-5, -4), (5, -4), (0, -4), (-3, 2), (3, 2), (0, 8)]:
            d.circle(surf, (150, 70, 180), P(dx, dy), 5 * K)
        d.ellipse(surf, leaf, E(-1, -13, 8, 5))
        face_y = 0
    elif kind == 3:  # taronja
        d.circle(surf, (255, 150, 30), P(0, 1), 11 * K)
        d.ellipse(surf, leaf, E(0, -13, 8, 5))
        d.circle(surf, (255, 195, 100), P(-6, -3), 2 * K)
    elif kind == 5:  # el 67 daurat
        d.circle(surf, (255, 200, 40), P(0, 0), 12 * K)
        d.circle(surf, (200, 130, 20), P(0, 0), 12 * K, 3 * K // 2)
        d.circle(surf, (255, 235, 130), P(-6, -6), 3 * K)
        txt = pygame.font.Font(None, 16 * K).render("67", True, (120, 60, 0))
        surf.blit(txt, txt.get_rect(center=P(0, 1)))
        return pygame.transform.smoothscale(surf, (38, 38))
    else:  # maduixa
        red = (235, 55, 85)
        d.polygon(surf, red, [P(-10, -5), P(10, -5), P(0, 12)])
        d.circle(surf, red, P(-5, -4), 6 * K)
        d.circle(surf, red, P(5, -4), 6 * K)
        d.polygon(surf, leaf, [P(-7, -10), P(7, -10), P(0, -4)])
        face_y = 1
    # cara maca
    ex = 3.2 if kind != 1 else 2.6
    for sx in (-1, 1):
        d.circle(surf, (40, 25, 25), P(sx * ex, face_y - 1), int(1.7 * K))
        d.circle(surf, (255, 255, 255), P(sx * ex + 0.6, face_y - 1.7), int(0.7 * K))
        d.circle(surf, (255, 140, 160), P(sx * (ex + 3.2), face_y + 2), int(1.5 * K))
    d.arc(surf, (60, 25, 25), E(-2, face_y, 4, 3), 3.5, 5.9, int(0.7 * K) + 1)
    return pygame.transform.smoothscale(surf, (34, 34))


_font67 = {}


def draw_star(screen, c, size, color):
    x, y = c
    pygame.draw.polygon(screen, color, [(x, y - size), (x + size // 4, y - size // 4), (x + size, y),
                                         (x + size // 4, y + size // 4), (x, y + size),
                                         (x - size // 4, y + size // 4), (x - size, y),
                                         (x - size // 4, y - size // 4)])


def draw_gold67(screen, r, frames):
    """El 67 molt xulo: brilla, pulsa i té espurnes."""
    if "f" not in _font67:
        _font67["f"] = pygame.font.Font(None, 34)
    d = pygame.draw
    cx, cy = r.center
    cy -= 3
    pulse = math.sin(frames * 0.2)
    # halo lluminós
    glow = pygame.Surface((120, 120), pygame.SRCALPHA)
    for rad, alpha in ((52, 25), (42, 40), (34, 60)):
        d.circle(glow, (255, 220, 80, alpha), (60, 60), int(rad + 3 * pulse))
    screen.blit(glow, glow.get_rect(center=(cx, cy)))
    # moneda daurada amb vora
    R = 21 + int(pulse)
    d.circle(screen, (150, 90, 10), (cx, cy + 2), R + 2)
    d.circle(screen, (255, 190, 30), (cx, cy), R + 1)
    d.circle(screen, (255, 225, 90), (cx, cy), R - 4)
    d.circle(screen, (255, 205, 50), (cx, cy + 2), R - 7)
    d.circle(screen, (215, 140, 20), (cx, cy), R + 1, 2)
    # reflex que brilla
    d.ellipse(screen, (255, 250, 200), (cx - R + 6, cy - R + 5, 11, 6))
    # número amb contorn
    txt = _font67["f"].render("67", True, (120, 60, 0))
    shine = _font67["f"].render("67", True, (255, 245, 190))
    c = (cx, cy + 1)
    screen.blit(txt, txt.get_rect(center=(c[0] + 1, c[1] + 2)))
    screen.blit(shine, shine.get_rect(center=(c[0], c[1] + 1)))
    screen.blit(txt, txt.get_rect(center=c))
    # espurnes que giren
    for i in range(4):
        a = frames * 0.07 + i * math.pi / 2
        px = cx + int(math.cos(a) * (R + 9))
        py = cy + int(math.sin(a) * (R + 9))
        draw_star(screen, (px, py), 4 + int(2 * math.sin(frames * 0.3 + i * 2)), (255, 255, 220))


def draw_fruit(screen, r, kind, frames=0):
    if kind == 5:
        draw_gold67(screen, r, frames)
        return
    if kind not in _fruit_cache:
        _fruit_cache[kind] = make_fruit(kind)
    img = _fruit_cache[kind]
    screen.blit(img, img.get_rect(center=r.center))


def draw_platform(screen, r):
    d = pygame.draw
    # ombra suau a sota
    shadow = pygame.Surface((r.w, 10), pygame.SRCALPHA)
    d.ellipse(shadow, (0, 0, 0, 50), (6, 0, r.w - 12, 10))
    screen.blit(shadow, (r.x, r.bottom + 6))
    # arrels que pengen
    for i, off in enumerate((18, 52, 90, 122)):
        x = r.x + off
        ln = 8 + (i * 5) % 11
        d.line(screen, (95, 65, 40), (x, r.bottom - 3), (x - 2, r.bottom + ln), 3)
        d.line(screen, (95, 65, 40), (x - 2, r.bottom + ln // 2), (x + 4, r.bottom + ln - 2), 2)
    # cos de pedra amb maons
    d.rect(screen, (140, 125, 110), r, border_radius=9)
    d.rect(screen, (112, 98, 86), (r.x, r.centery + 2, r.w, r.h // 2 - 2),
           border_bottom_left_radius=9, border_bottom_right_radius=9)
    for row, y in enumerate((r.y + 9, r.y + 15)):
        for x in range(r.x + 10 + (row % 2) * 12, r.right - 8, 24):
            d.line(screen, (100, 88, 76), (x, y - 5 if row == 0 else y - 4), (x, y), 1)
    d.line(screen, (100, 88, 76), (r.x + 4, r.y + 10), (r.right - 4, r.y + 10), 1)
    d.rect(screen, (80, 68, 58), r, 2, border_radius=9)
    # capa d'herba amb vora ondulada
    d.rect(screen, (85, 185, 75), (r.x - 2, r.y - 4, r.w + 4, 10), border_radius=5)
    d.rect(screen, (120, 215, 95), (r.x + 2, r.y - 4, r.w - 4, 3), border_radius=2)
    for x in range(r.x + 2, r.right - 6, 11):
        d.circle(screen, (85, 185, 75), (x + 4, r.y + 6), 5)
    # borrissols d'herba
    for x in range(r.x + 8, r.right - 6, 17):
        d.polygon(screen, (60, 160, 60), [(x, r.y - 4), (x + 2, r.y - 10), (x + 4, r.y - 4)])
    # floretes
    for x, col in ((r.x + 28, (255, 120, 160)), (r.x + 78, (255, 220, 70)), (r.x + 114, (255, 255, 255))):
        d.line(screen, (50, 140, 50), (x, r.y - 4), (x, r.y - 9), 2)
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            d.circle(screen, col, (x + dx, r.y - 11 + dy), 2)
        d.circle(screen, (255, 170, 40), (x, r.y - 11), 1)


def draw_caveman(screen, player, facing, walking, on_ground, frames, celebrate=0, club=True):
    x, y, cx = player.x, player.y, player.centerx
    swing = 0
    if walking and on_ground:
        swing = 6 if (frames // 6) % 2 == 0 else -6
    if not on_ground:
        swing = 8
    # cames
    pygame.draw.rect(screen, SKIN, (cx - 9 + swing // 2, y + 40, 7, 10))
    pygame.draw.rect(screen, SKIN, (cx + 2 - swing // 2, y + 40, 7, 10))
    # porra de fusta (no la porta mentre fa el 67)
    hand_y = y + 28 - (10 if not on_ground else 0)
    if not celebrate and club:
        pygame.draw.line(screen, (100, 65, 30), (cx + 10 * facing, hand_y), (cx + 24 * facing, hand_y - 16), 5)
        pygame.draw.circle(screen, (100, 65, 30), (cx + 24 * facing, hand_y - 16), 6)
    # pell de pel
    pygame.draw.rect(screen, FUR, (x, y + 22, player.w, 20), border_radius=4)
    for i in range(4):
        px = x + 2 + i * 8
        pygame.draw.polygon(screen, FUR, [(px, y + 40), (px + 6, y + 40), (px + 3, y + 47)])
    # braç
    if celebrate:
        # el moviment del 67: una mà amunt i l'altra avall, i al revés!
        up = (celebrate // 7) % 2 == 0
        for side, hand_up in ((-1, up), (1, not up)):
            sx_, sy_ = cx + side * 12, y + 27
            hx = cx + side * 24
            hy = y - 6 if hand_up else y + 46
            pygame.draw.line(screen, SKIN, (sx_, sy_), (hx, hy), 7)
            pygame.draw.circle(screen, SKIN, (hx, hy), 7)
    else:
        pygame.draw.circle(screen, SKIN, (cx + 8 * facing, hand_y), 5)
    # cap
    pygame.draw.circle(screen, SKIN, (cx, y + 12), 14)
    # cabell
    pygame.draw.arc(screen, (60, 35, 15), (cx - 15, y - 3, 30, 24), 0, 3.15, 8)
    # ull
    ex = cx + 5 * facing
    pygame.draw.circle(screen, (255, 255, 255), (ex, y + 11), 4)
    pygame.draw.circle(screen, (0, 0, 0), (ex + facing, y + 11), 2)
    # somriure
    if celebrate:
        pygame.draw.ellipse(screen, (150, 60, 50), (cx + 1 * facing - 4, y + 17, 10, 7))
    else:
        pygame.draw.arc(screen, (150, 60, 50), (cx + 1 * facing - 4, y + 12, 10, 8), 3.4, 6.0, 2)


class Fruit(pygame.Rect):
    """Fruita que fa salts: pel terra, per la plataforma i d'una plataforma a una altra."""

    def __init__(self, home, platforms, kind=None):
        super().__init__(0, 0, 30, 30)
        self.kind = random.randint(0, 4) if kind is None else kind
        self.points = 10 if self.kind == 5 else 1  # el 67 val 10!
        self.home = home  # None = terra, o una plataforma
        self.off = random.randint(-55, 55) if home else ground_x()
        self.wait = random.randint(20, 150)
        self.t = 0
        self.rest_pos(platforms)

    def spot(self, home, off):
        """Punt (x, y_peus) on la fruita reposa en un lloc."""
        if home is None:
            return off, GROUND
        return home["r"].centerx + off, home["r"].top - 4

    def rest_pos(self, platforms):
        self.midbottom = self.spot(self.home, self.off)

    def update(self, platforms):
        if self.wait > 0:
            self.wait -= 1
            self.rest_pos(platforms)
            if self.wait == 0:
                self.choose(platforms)
            return
        self.t += 1
        s = self.t / self.dur
        ex, ey = self.spot(self.dest, self.dest_off)
        x = self.sx + (ex - self.sx) * s
        y = self.sy + (ey - self.sy) * s - self.lift * math.sin(math.pi * s)
        self.midbottom = (int(x), int(y))
        if self.t >= self.dur:
            self.home, self.off = self.dest, self.dest_off
            self.t = 0
            self.wait = random.randint(10, 40) if self.kind == 5 else random.randint(40, 160)
            self.rest_pos(platforms)

    def choose(self, platforms):
        """Tria un lloc proper: la mateixa plataforma, el terra o una altra plataforma."""
        self.sx, self.sy = self.midbottom
        options = [None] + platforms
        near = [h for h in options
                if h is not self.home and abs(self.spot(h, 0)[0] - self.sx) < 380
                and self.sy - self.spot(h, 0)[1] < 150]
        if near and random.random() < 0.7:
            self.dest = random.choice(near)
        else:
            self.dest = self.home
        if self.dest is None:
            self.dest_off = ground_x()
        else:
            self.dest_off = random.randint(-55, 55)
        ex, ey = self.spot(self.dest, self.dest_off)
        self.dur = 40 + int(abs(ex - self.sx) / 12)
        if self.kind == 5:
            self.dur = max(14, self.dur // 3)  # el 67 va molt més ràpid
        self.lift = 40 + max(0, self.sy - ey) * 0.6
        self.t = 1


_mammoth_cache = {}


def make_mammoth(phase):
    """Dibuixa un mamut mirant cap a la dreta (fase 0/1 = cames diferents)."""
    d = pygame.draw
    surf = pygame.Surface((170, 130), pygame.SRCALPHA)
    fur = (112, 70, 42)
    dark = (78, 46, 26)
    light = (150, 100, 62)
    gy = 126  # terra

    # cames (les de darrere i les del davant es mouen alternades)
    for lx, up in ((34, phase), (58, 1 - phase), (96, 1 - phase), (120, phase)):
        top = 74
        bot = gy - 7 * up
        d.rect(surf, dark if lx in (34, 96) else fur, (lx, top, 24, bot - top), border_radius=8)
        d.ellipse(surf, (235, 225, 200), (lx - 1, bot - 9, 26, 11))  # peülles
        d.ellipse(surf, (200, 190, 165), (lx + 3, bot - 5, 18, 6))
    # cua
    d.line(surf, dark, (20, 62), (8, 86), 4)
    d.polygon(surf, dark, [(8, 82), (2, 98), (14, 94)])
    # cos pelut
    d.ellipse(surf, fur, (14, 30, 118, 72))
    d.ellipse(surf, light, (30, 66, 86, 30))  # panxa clara
    # flocs de pèl al llom i a la panxa
    for i in range(7):
        x = 24 + i * 15
        d.polygon(surf, dark, [(x, 40 + abs(i - 3) * 2), (x + 9, 28 + abs(i - 3) * 2), (x + 15, 42 + abs(i - 3) * 2)])
    for i in range(6):
        x = 28 + i * 15
        d.polygon(surf, dark, [(x, 94), (x + 6, 112), (x + 13, 94)])
    # cap
    d.ellipse(surf, fur, (96, 22, 62, 64))
    # monyo de pèl al front
    for i, (px, py) in enumerate([(104, 24), (116, 16), (130, 16), (143, 22)]):
        d.polygon(surf, dark, [(px - 7, py + 12), (px + 2, py - 12), (px + 9, py + 12)])
    # orella
    d.ellipse(surf, dark, (84, 36, 30, 44))
    d.ellipse(surf, (200, 120, 110), (90, 44, 17, 28))
    # trompa (corba i acaba amunt)
    pts = []
    for i in range(15):
        t = i / 14
        x = 142 + 16 * math.sin(t * 2.4) * 0.9
        y = 58 + 62 * t - 10 * math.sin(t * math.pi) * 0 
        pts.append((x, y))
    for i, (x, y) in enumerate(pts):
        d.circle(surf, fur, (int(x), int(y)), int(10 - i * 0.35))
    for i in range(0, 15, 3):
        x, y = pts[i]
        d.arc(surf, dark, (int(x) - 8, int(y) - 3, 16, 7), 3.3, 6.1, 2)
    # ullals blancs i corbats
    for sx in (0, 12):
        prev = None
        for i in range(26):
            t = i / 25
            x = 134 + sx * 0.3 + 40 * t * (1 - 0.35 * t) 
            y = 80 + 6 * math.sin(t * 2) - 46 * t * t + sx * 0.3
            r = int(6 - 4 * t)
            d.circle(surf, (252, 248, 232) if sx == 0 else (232, 225, 205), (int(x), int(y)), max(3, r))
    # ull enfadat
    d.circle(surf, (255, 255, 255), (131, 50), 9)
    d.circle(surf, (200, 30, 30), (134, 51), 5)
    d.circle(surf, (0, 0, 0), (135, 51), 3)
    d.circle(surf, (255, 255, 255), (136, 49), 1)
    d.polygon(surf, (40, 20, 10), [(119, 34), (122, 30), (145, 46), (141, 51)])  # celles enfadades
    # galtes i bocí
    d.circle(surf, (200, 100, 90), (122, 64), 5)
    return surf


class Mammoth(Fruit):
    """Mamut dolent, petit i lent: passeja i puja per les plataformes."""

    def __init__(self, home, platforms, speed):
        super().__init__(home, platforms, 0)
        self.size = (78, 54)
        self.speed = speed
        self.dir = random.choice((-1, 1))
        self.step = random.randint(0, 30)
        self.stun = 0
        self.fall = 0.0  # >0: està caient pel forat
        self.drop = 0.0  # >0: torna a baixar des de dalt
        self.off = random.randint(-30, 30) if home else ground_x(300, W - 120)
        self.wait = random.randint(200, 500)
        self.rest_pos(platforms)

    def update(self, platforms):
        self.step += 1
        if self.fall:  # cau pel forat
            self.fall += 0.6
            self.y += int(self.fall)
            if self.top > H:  # torna a aparèixer per dalt, com el cavernícola
                self.fall = 0.0
                self.drop = 1.0
                self.dir = random.choice((-1, 1))
                self.off = ground_x(60, W - 90)
                self.wait = random.randint(200, 500)
                self.t = 0
                self.midbottom = (int(self.off), -10)
            return
        if self.drop:  # baixa des de dalt fins al terra
            self.drop += 0.6
            self.y += int(self.drop)
            if self.bottom >= GROUND:
                self.drop = 0.0
                self.rest_pos(platforms)
            return
        if self.stun > 0:  # marejat: no es mou (si no està saltant)
            self.stun -= 1
            if self.wait > 0:
                return
        if self.wait > 0:  # passeja
            self.wait -= 1
            lo, hi = (-34, 34) if self.home else (50, W - 50)
            self.off += self.speed * self.dir
            if self.off < lo or self.off > hi:
                self.dir = -self.dir
                self.off = max(lo, min(hi, self.off))
            elif not self.home and HOLE_X0 + 35 < self.off < HOLE_X1 - 35:
                self.fall = 1.0  # ha caigut al forat!
            self.rest_pos(platforms)
            if self.wait == 0:
                self.choose(platforms)
            return
        jumping = self.t > 0
        super().update(platforms)
        if jumping and self.t == 0:  # acaba d'aterrar
            self.wait = random.randint(250, 600)

    def choose(self, platforms):
        super().choose(platforms)
        if self.dest is not None:
            self.dest_off = max(-34, min(34, self.dest_off))
        ex, _ = self.spot(self.dest, self.dest_off)
        self.dir = 1 if ex >= self.sx else -1
        self.dur *= 3  # puja a poc a poc


def draw_mammoth(screen, m, frames):
    phase = (m.step // 14) % 2
    if phase not in _mammoth_cache:
        _mammoth_cache[phase] = pygame.transform.smoothscale(make_mammoth(phase), (105, 80))
    img = _mammoth_cache[phase]
    if m.dir < 0:
        img = pygame.transform.flip(img, True, False)
    sh = pygame.Surface((90, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 60), (0, 0, 90, 10))
    screen.blit(sh, (m.centerx - 45, m.bottom - 6))
    screen.blit(img, img.get_rect(midbottom=(m.centerx, m.bottom + 3)))
    if m.stun > 0:  # estrelletes de mareig
        for i in range(3):
            a = m.step * 0.15 + i * 2.09
            draw_star(screen, (m.centerx + m.dir * 14 + int(math.cos(a) * 22), m.top - 4 + int(math.sin(a) * 5)),
                      6, (255, 235, 90))


CLOUDS = [(80, 70, 1.0, 0.25), (380, 120, 1.4, 0.15), (620, 55, 0.9, 0.3), (850, 150, 1.2, 0.2), (200, 190, 0.8, 0.18)]


WEATHERS = ["sol", "pluja", "nit", "neu"]
WEATHER_NAME = {"sol": "Sol", "pluja": "Pluja", "nit": "Nit", "neu": "Neu"}
SKY_OF = {"sol": (120, 190, 235), "pluja": (105, 120, 145), "nit": (20, 25, 62), "neu": (185, 202, 220)}
CLOUD_OF = {"sol": (255, 255, 255), "pluja": (150, 155, 168), "nit": (70, 80, 115), "neu": (238, 242, 248)}


def lerp_color(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def draw_sun(screen, frames):
    d = pygame.draw
    sx, sy = W - 130, 95
    for i in range(12):  # raigs
        a = frames * 0.01 + i * math.pi / 6
        d.line(screen, (255, 235, 120), (sx + math.cos(a) * 52, sy + math.sin(a) * 52),
               (sx + math.cos(a) * 78, sy + math.sin(a) * 78), 6)
    d.circle(screen, (255, 240, 150), (sx, sy), 54)
    d.circle(screen, (255, 215, 60), (sx, sy), 44)
    d.circle(screen, (255, 235, 130), (sx - 12, sy - 14), 12)
    for ex in (-14, 14):  # cara contenta
        d.circle(screen, (120, 70, 20), (sx + ex, sy - 6), 4)
    d.arc(screen, (120, 70, 20), (sx - 15, sy - 2, 30, 22), 3.5, 5.9, 3)
    d.circle(screen, (255, 150, 90), (sx - 25, sy + 6), 6)
    d.circle(screen, (255, 150, 90), (sx + 25, sy + 6), 6)


def draw_moon_stars(screen, frames):
    d = pygame.draw
    for i in range(45):  # estrelles que parpellegen
        x = (i * 211) % W
        y = (i * 97) % (GROUND - 160) + 10
        r = 1 + int(1.5 * abs(math.sin(frames * 0.05 + i)))
        d.circle(screen, (255, 255, 225), (x, y), r)
    mx, my = W - 130, 95
    d.circle(screen, (250, 245, 205), (mx, my), 42)
    d.circle(screen, SKY_OF["nit"], (mx + 18, my - 8), 36)  # forma de lluna creixent
    d.circle(screen, (225, 220, 175), (mx - 22, my + 14), 5)
    d.circle(screen, (225, 220, 175), (mx - 12, my - 18), 3)


def draw_clouds(screen, frames, color, shade):
    d = pygame.draw
    for cx, cy, k, sp in CLOUDS:
        x = (cx + frames * sp) % (W + 300) - 150
        r = int(26 * k)
        for dx, dy, rr in ((-1.4, 0.5, 0.8), (-0.6, -0.2, 1.1), (0.5, -0.4, 1.3), (1.4, 0.3, 0.9), (0.2, 0.5, 1.0)):
            d.circle(screen, color, (int(x + dx * r), int(cy + dy * r)), int(rr * r))
        d.rect(screen, color, (int(x - 1.8 * r), int(cy + 0.5 * r), int(3.8 * r), int(0.9 * r)), border_radius=int(0.4 * r))
        d.rect(screen, shade, (int(x - 1.7 * r), int(cy + 1.1 * r), int(3.6 * r), int(0.3 * r)), border_radius=int(0.15 * r))


def draw_background(screen, frames, weather):
    if weather == "sol":
        draw_sun(screen, frames)
    elif weather == "nit":
        draw_moon_stars(screen, frames)
    col = CLOUD_OF[weather]
    draw_clouds(screen, frames, col, lerp_color(col, (120, 140, 170), 0.2))


def draw_weather_front(screen, frames, weather):
    """Pluja o neu per davant de tot, i una mica d'ombra si és de nit."""
    d = pygame.draw
    if weather == "pluja":
        for i in range(140):
            x = (i * 97 + frames * 3) % (W + 60) - 30
            y = (i * 53 + frames * 16) % H
            d.line(screen, (190, 215, 245), (x, y), (x - 5, y + 14), 2)
        veil = pygame.Surface((W, H), pygame.SRCALPHA)
        veil.fill((40, 55, 85, 35))
        screen.blit(veil, (0, 0))
    elif weather == "neu":
        for i in range(90):
            x = (i * 131 + math.sin(frames * 0.03 + i) * 25) % W
            y = (i * 71 + frames * (1.5 + i % 3 * 0.5)) % H
            d.circle(screen, (255, 255, 255), (int(x), int(y)), 2 + i % 3)
    elif weather == "nit":
        veil = pygame.Surface((W, H), pygame.SRCALPHA)
        veil.fill((10, 15, 50, 85))
        screen.blit(veil, (0, 0))


def draw_hole(screen):
    d = pygame.draw
    w = HOLE_X1 - HOLE_X0
    d.rect(screen, (25, 15, 30), (HOLE_X0, GROUND, w, H - GROUND))
    for i in range(6):  # fosc cap avall
        d.rect(screen, (45 - i * 6, 28 - i * 3, 40 - i * 5), (HOLE_X0, GROUND + 4 + i * 8, w, 8))
    d.rect(screen, (25, 15, 30), (HOLE_X0, GROUND + 40, w, H))
    d.rect(screen, (80, 55, 35), (HOLE_X0 - 6, GROUND + 14, 6, H - GROUND))  # parets de terra
    d.rect(screen, (80, 55, 35), (HOLE_X1, GROUND + 14, 6, H - GROUND))
    d.rect(screen, GRASS, (HOLE_X0 - 10, GROUND, 10, 14), border_top_left_radius=6, border_bottom_left_radius=6)
    d.rect(screen, GRASS, (HOLE_X1, GROUND, 10, 14), border_top_right_radius=6, border_bottom_right_radius=6)


_club_img = {}


def club_image():
    if "i" not in _club_img:
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.line(surf, (100, 65, 30), (12, 38), (36, 12), 7)
        pygame.draw.circle(surf, (120, 78, 36), (37, 11), 9)
        pygame.draw.circle(surf, (150, 105, 55), (34, 8), 3)
        _club_img["i"] = surf
    return _club_img["i"]


def draw_boomerang(screen, b):
    img = pygame.transform.rotate(club_image(), b["angle"])
    screen.blit(img, img.get_rect(center=(int(b["x"]), int(b["y"]))))


def draw_slingshot(screen, player, facing):
    """El tiratxines: una forquilla de fusta amb goma."""
    d = pygame.draw
    bx, by = player.centerx + 16 * facing, player.y + 30
    d.line(screen, (100, 65, 30), (bx, by + 12), (bx, by), 5)
    d.line(screen, (100, 65, 30), (bx, by), (bx - 6, by - 12), 4)
    d.line(screen, (100, 65, 30), (bx, by), (bx + 6, by - 12), 4)
    d.line(screen, (200, 60, 60), (bx - 6, by - 12), (bx - 14 * facing, by - 4), 2)
    d.line(screen, (200, 60, 60), (bx + 6, by - 12), (bx - 14 * facing, by - 4), 2)
    d.circle(screen, (130, 130, 135), (bx - 14 * facing, by - 4), 5)


def draw_stone(screen, st):
    x, y = int(st["x"]), int(st["y"])
    for k in range(1, 5):  # estela
        d_ = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(d_, (255, 255, 255, 90 - k * 18), (6, 6), 6 - k)
        screen.blit(d_, (x - st["dir"] * k * 9 - 6, y - 6))
    pygame.draw.circle(screen, (95, 95, 105), (x, y), 8)
    pygame.draw.circle(screen, (140, 140, 150), (x - 2, y - 2), 6)
    pygame.draw.circle(screen, (200, 200, 210), (x - 3, y - 3), 2)


WEAPONS = ["bumerang", "tiratxines", "porra", "llança", "roca", "foc", "arc", "gel", "tornado"]
WEAPON_NAME = {"bumerang": "Porra bumerang", "tiratxines": "Tiratxines", "porra": "Porra de cops",
               "llança": "Llança", "roca": "Roca rodant", "foc": "Bola de foc", "arc": "Arc i fletxa",
               "gel": "Bola de gel", "tornado": "Tornado"}
WEAPON_CD = {"bumerang": 0, "tiratxines": 18, "porra": 0, "llança": 26, "roca": 70, "foc": 30, "arc": 20, "gel": 32, "tornado": 70}
PICKUP_LIFE = 7  # segons que dura una arma al terra
_spear_img = {}


def spear_image():
    if "i" not in _spear_img:
        surf = pygame.Surface((64, 16), pygame.SRCALPHA)
        pygame.draw.line(surf, (120, 80, 40), (2, 8), (50, 8), 4)
        pygame.draw.polygon(surf, (190, 195, 205), [(44, 1), (63, 8), (44, 15)])
        pygame.draw.polygon(surf, (235, 240, 245), [(46, 4), (58, 8), (46, 8)])
        pygame.draw.line(surf, (200, 60, 60), (6, 4), (10, 8), 2)
        pygame.draw.line(surf, (200, 60, 60), (6, 12), (10, 8), 2)
        _spear_img["i"] = surf
    return _spear_img["i"]


def draw_weapon_icon(screen, kind, cx, cy, size=36):
    """Dibuixa la icona d'una arma dins d'una bombolla."""
    d = pygame.draw
    k = size / 36
    d.circle(screen, (255, 245, 190), (cx, cy), int(22 * k))
    d.circle(screen, (230, 170, 40), (cx, cy), int(22 * k), 3)
    if kind == "bumerang":
        img = pygame.transform.rotozoom(club_image(), 0, 0.8 * k)
        screen.blit(img, img.get_rect(center=(cx, cy)))
    elif kind == "porra":
        img = pygame.transform.rotozoom(club_image(), 30, 0.9 * k)
        screen.blit(img, img.get_rect(center=(cx, cy)))
        d.circle(screen, (255, 255, 255), (cx + int(9 * k), cy - int(9 * k)), int(3 * k))
    elif kind == "tiratxines":
        d.line(screen, (100, 65, 30), (cx, cy + int(12 * k)), (cx, cy), int(5 * k))
        d.line(screen, (100, 65, 30), (cx, cy), (cx - int(8 * k), cy - int(12 * k)), int(4 * k))
        d.line(screen, (100, 65, 30), (cx, cy), (cx + int(8 * k), cy - int(12 * k)), int(4 * k))
        d.circle(screen, (110, 110, 120), (cx, cy - int(13 * k)), int(4 * k))
    elif kind == "llança":
        img = pygame.transform.rotozoom(spear_image(), 35, 0.55 * k)
        screen.blit(img, img.get_rect(center=(cx, cy)))
    elif kind == "foc":
        d.circle(screen, (255, 120, 20), (cx, cy + int(2 * k)), int(12 * k))
        d.polygon(screen, (255, 120, 20), [(cx - int(8 * k), cy), (cx, cy - int(16 * k)), (cx + int(8 * k), cy)])
        d.circle(screen, (255, 210, 60), (cx, cy + int(4 * k)), int(7 * k))
        d.circle(screen, (255, 250, 200), (cx, cy + int(6 * k)), int(3 * k))
    elif kind == "arc":
        d.arc(screen, (120, 80, 40), (cx - int(14 * k), cy - int(15 * k), int(18 * k), int(30 * k)), -1.2, 1.2, 4)
        d.line(screen, (230, 230, 230), (cx - int(7 * k), cy - int(14 * k)), (cx - int(7 * k), cy + int(14 * k)), 1)
        d.line(screen, (120, 80, 40), (cx - int(8 * k), cy), (cx + int(14 * k), cy), 2)
        d.polygon(screen, (190, 195, 205), [(cx + int(14 * k), cy), (cx + int(8 * k), cy - int(4 * k)), (cx + int(8 * k), cy + int(4 * k))])
    elif kind == "gel":
        d.circle(screen, (110, 190, 245), (cx, cy), int(13 * k))
        d.circle(screen, (190, 235, 255), (cx - int(3 * k), cy - int(3 * k)), int(8 * k))
        d.line(screen, (255, 255, 255), (cx - int(9 * k), cy), (cx + int(9 * k), cy), 2)
        d.line(screen, (255, 255, 255), (cx, cy - int(9 * k)), (cx, cy + int(9 * k)), 2)
    elif kind == "tornado":
        for i in range(5):
            w_ = int((24 - i * 4) * k)
            d.ellipse(screen, (150, 160, 175), (cx - w_ // 2 + int((i % 2) * 2 * k), cy - int(13 * k) + int(i * 6 * k), w_, int(6 * k)), 2)
    else:  # roca
        d.circle(screen, (110, 105, 100), (cx, cy), int(13 * k))
        d.circle(screen, (150, 145, 138), (cx - int(3 * k), cy - int(3 * k)), int(9 * k))
        d.line(screen, (80, 75, 70), (cx - int(5 * k), cy + int(2 * k)), (cx + int(3 * k), cy - int(2 * k)), 2)


def draw_spear(screen, sp):
    ang = math.degrees(math.atan2(sp["vy"], sp["vx"]))
    img = pygame.transform.rotate(spear_image(), -ang)
    screen.blit(img, img.get_rect(center=(int(sp["x"]), int(sp["y"]))))


def draw_fireball(screen, fb, frames):
    x, y = int(fb["x"]), int(fb["y"])
    d = pygame.draw
    for k in range(1, 5):  # cua de flames
        d.circle(screen, (255, 140 + k * 20, 30), (x - int(fb["vx"] * k * 1.4), y + k * 2), max(2, 11 - k * 2))
    f = int(2 * math.sin(frames * 0.6))
    d.circle(screen, (255, 110, 20), (x, y), 13 + f)
    d.circle(screen, (255, 200, 50), (x, y), 9)
    d.circle(screen, (255, 250, 190), (x, y), 4)


def draw_fireball_ice(screen, fb, frames):
    x, y = int(fb["x"]), int(fb["y"])
    d = pygame.draw
    for k in range(1, 5):
        d.circle(screen, (170 + k * 15, 225, 255), (x - int(fb["vx"] * k * 1.6), y + k * 2), max(2, 11 - k * 2))
    d.circle(screen, (90, 170, 235), (x, y), 14)
    d.circle(screen, (170, 225, 255), (x - 2, y - 2), 10)
    d.line(screen, (255, 255, 255), (x - 8, y), (x + 8, y), 2)
    d.line(screen, (255, 255, 255), (x, y - 8), (x, y + 8), 2)
    d.circle(screen, (255, 255, 255), (x - 5, y - 6), 3)


def draw_arrow(screen, ar):
    x, y, dr = int(ar["x"]), int(ar["y"]), ar["dir"]
    d = pygame.draw
    d.line(screen, (150, 105, 55), (x - 26 * dr, y), (x + 8 * dr, y), 3)
    d.polygon(screen, (195, 200, 210), [(x + 16 * dr, y), (x + 6 * dr, y - 5), (x + 6 * dr, y + 5)])
    for off in (0, 6):  # plomes
        d.line(screen, (210, 60, 60), (x - 26 * dr + off * dr, y), (x - 31 * dr + off * dr, y - 5), 2)
        d.line(screen, (210, 60, 60), (x - 26 * dr + off * dr, y), (x - 31 * dr + off * dr, y + 5), 2)


def draw_tornado(screen, t, frames):
    d = pygame.draw
    base_y = GROUND
    for i in range(9):
        w_ = 16 + i * 7
        y = base_y - 8 - i * 13
        sway = math.sin(frames * 0.3 + i * 0.8) * (4 + i)
        d.ellipse(screen, (165, 175, 190), (int(t["x"] - w_ / 2 + sway), y, w_, 10))
        d.ellipse(screen, (225, 232, 240), (int(t["x"] - w_ / 2 + sway), y, w_, 10), 2)
    for i in range(4):  # trossets que giren
        a = frames * 0.4 + i * 1.6
        d.circle(screen, (110, 170, 90), (int(t["x"] + math.cos(a) * 38), int(base_y - 30 - i * 22 + math.sin(a) * 6)), 3)


def draw_boulder(screen, b):
    x, y, r = int(b["x"]), int(b["y"]), 24
    d = pygame.draw
    d.circle(screen, (95, 90, 85), (x, y), r)
    d.circle(screen, (135, 128, 120), (x - 4, y - 4), r - 6)
    a = b["rot"]
    for i in range(3):  # esquerdes que giren
        aa = a + i * 2.1
        d.line(screen, (70, 66, 62), (x + math.cos(aa) * 4, y + math.sin(aa) * 4),
               (x + math.cos(aa) * (r - 4), y + math.sin(aa) * (r - 4)), 3)
    d.circle(screen, (160, 155, 148), (x - 9, y - 10), 4)


def draw_swing(screen, player, facing, t, total):
    """Cop de porra: la porra gira de dalt cap a baix."""
    s = t / total
    th = math.radians(10 + 150 * s)
    px, py = player.centerx + 10 * facing, player.y + 26
    L = 40
    def pos(a):
        return px + L * math.sin(a) * facing, py - L * math.cos(a)
    # estela blanca
    for k in range(1, 6):
        a = th - k * 0.16
        if a > 0:
            x, y = pos(a)
            pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), 8 - k)
    x, y = pos(th)
    pygame.draw.line(screen, (100, 65, 30), (px, py), (int(x), int(y)), 7)
    pygame.draw.circle(screen, (120, 78, 36), (int(x), int(y)), 9)


HS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscores.json")


def load_scores():
    try:
        with open(HS_FILE) as f:
            return [(str(e.get("name", "???")), int(e["score"]), float(e["time"])) for e in json.load(f)][:5]
    except Exception:
        return []


def save_score(name, score, secs):
    """Guarda la puntuació i es queda només amb les 5 millors. Torna la posició (0-4) o -1."""
    entry = (name, score, round(secs, 1))
    entries = load_scores() + [entry]
    entries.sort(key=lambda e: (-e[1], e[2]))
    top = entries[:5]
    try:
        with open(HS_FILE, "w") as f:
            json.dump([{"name": n, "score": a, "time": b} for n, a, b in top], f)
    except Exception:
        pass
    return top.index(entry) if entry in top else -1


def fmt_time(secs):
    return f"{int(secs) // 60}:{int(secs) % 60:02d}"


def draw_win_panel(screen, big, font, score, secs, top, rank, name=None, frames=0, extra=None):
    BLUE, DBLUE, RED = (35, 80, 200), (20, 45, 130), (215, 40, 50)
    pw, ph = 540, 470
    r = pygame.Rect((W - pw) // 2, (H - ph) // 2 - 10, pw, ph)
    shade = pygame.Surface((W, H), pygame.SRCALPHA)
    shade.fill((0, 0, 0, 110))
    screen.blit(shade, (0, 0))
    pygame.draw.rect(screen, RED, r.inflate(12, 12), border_radius=22)
    pygame.draw.rect(screen, BLUE, r, border_radius=18)
    pygame.draw.rect(screen, RED, (r.x, r.y, pw, 8), border_top_left_radius=18, border_top_right_radius=18)
    pygame.draw.rect(screen, RED, (r.x, r.bottom - 8, pw, 8), border_bottom_left_radius=18, border_bottom_right_radius=18)
    t = big.render("Has guanyat!!!", True, (255, 225, 60))
    screen.blit(t, t.get_rect(center=(r.centerx, r.y + 55)))
    t = big.render(f"Puntuació: {score}", True, (255, 255, 255))
    screen.blit(t, t.get_rect(center=(r.centerx, r.y + 105)))
    if extra:
        base, bonus, pen = extra
        t = font.render(f"Punts {base}  +  Bonus rapidesa {bonus}", True, (255, 225, 60))
        screen.blit(t, t.get_rect(center=(r.centerx, r.y + 145)))
        txt = f"Temps: {fmt_time(secs)}" + (f"  (inclou +{pen}s per cops)" if pen else "")
    else:
        txt = f"Temps: {fmt_time(secs)}"
    t = font.render(txt, True, (255, 255, 255))
    screen.blit(t, t.get_rect(center=(r.centerx, r.y + 177)))
    box = pygame.Rect(r.x + 40, r.y + 200, pw - 80, 210)
    pygame.draw.rect(screen, DBLUE, box, border_radius=12)
    pygame.draw.rect(screen, RED, box, 4, border_radius=12)
    if name is not None:  # encara està escrivint el nom
        t = font.render("Escriu el teu nom:", True, (255, 225, 60))
        screen.blit(t, t.get_rect(center=(box.centerx, box.y + 45)))
        inp = pygame.Rect(box.x + 40, box.y + 80, box.w - 80, 50)
        pygame.draw.rect(screen, (255, 255, 255), inp, border_radius=10)
        pygame.draw.rect(screen, RED, inp, 3, border_radius=10)
        cur = "|" if (frames // 20) % 2 == 0 else ""
        t = big.render(name + cur, True, (20, 45, 130))
        screen.blit(t, t.get_rect(center=inp.center))
        t = font.render("Després prem INTRO", True, (255, 255, 255))
        screen.blit(t, t.get_rect(center=(box.centerx, box.y + 170)))
        return
    t = font.render("Les 5 millors", True, (255, 225, 60))
    screen.blit(t, t.get_rect(center=(box.centerx, box.y + 24)))
    for i, (nm, sc, tm) in enumerate(top):
        me = i == rank
        col = (255, 225, 60) if me else (255, 255, 255)
        y = box.y + 55 + i * 30
        if me:
            pygame.draw.rect(screen, RED, (box.x + 12, y - 13, box.w - 24, 27), border_radius=8)
        screen.blit(font.render(f"{i + 1}. {nm}", True, col), (box.x + 24, y - 10))
        pt = font.render(f"{sc} punts", True, col)
        screen.blit(pt, pt.get_rect(topleft=(box.x + 200, y - 10)))
        tt = font.render(fmt_time(tm), True, col)
        screen.blit(tt, tt.get_rect(topright=(box.right - 24, y - 10)))
    t = font.render("Prem INTRO per tornar a jugar", True, (255, 255, 255))
    screen.blit(t, t.get_rect(center=(r.centerx, r.bottom - 24)))


async def run_game(screen, clock, font, big, test):

    player = pygame.Rect(100, GROUND - 50, 30, 50)
    vx = vy = 0.0
    on_ground = True
    score = 0
    platforms = [
        {"r": pygame.Rect(320, GROUND - 110, 140, 18), "ax": 0, "ay": 40, "sp": 0.03, "x0": 320, "y0": GROUND - 110},
        {"r": pygame.Rect(650, GROUND - 190, 140, 18), "ax": 110, "ay": 0, "sp": 0.025, "x0": 650, "y0": GROUND - 190},
    ]
    # plataformes fixes (no es mouen)
    for x, h in [(30, 100), (190, 200), (450, 290), (860, 110), (790, 300)]:
        platforms.append({"r": pygame.Rect(x, GROUND - h, 140, 18), "ax": 0, "ay": 0, "sp": 0, "x0": x, "y0": GROUND - h})
    foods = [Fruit(None, platforms) for _ in range(5)] + [Fruit(p, platforms) for p in platforms]
    foods.append(Fruit(None, platforms, 5))
    frames = 0
    riding = None
    facing = 1
    celebrate = 0
    hurt = 0
    air_jumps = 0
    in_hole = False
    boom = None
    weapon = random.choice(WEAPONS)  # comences amb una arma a l'atzar
    pickups = []
    spears = []
    boulders = []
    weapon_msg = 0
    stones = []
    sling = 0
    sling_cd = 0
    reserve = 4
    respawns = []
    poofs = []
    swing = 0
    swing_hit = False
    SWING_LEN = 14
    fireballs = []
    arrows = []
    tornados = []
    mammoths = [Mammoth(None, platforms, random.uniform(0.3, 0.5)) for _ in range(2)]
    mammoths += [Mammoth(p, platforms, random.uniform(0.25, 0.4)) for p in random.sample(platforms[2:], 2)]

    won = False
    win_info = None
    win_name = None
    win_secs = 0.0
    win_score = 0
    win_extra = None
    hits = 0  # cops rebuts dels mamuts (cada un afegeix segons de penalització)
    combo_n = 0  # fruites/mamuts seguits sense parar
    combo_t = 0
    COMBO_FRAMES = 3 * FPS
    popups = []

    def add_points(base, x, y):
        """Suma punts amb el multiplicador de combo (x1 ... x5)."""
        nonlocal score, combo_n, combo_t
        mult = min(5, 1 + combo_n // 2)
        pts = base * mult
        score += pts
        combo_n += 1
        combo_t = COMBO_FRAMES
        popups.append([x, y, 45, f"+{pts}" + (f" x{mult}" if mult > 1 else ""), mult])
    win_top = False
    weather = random.choice(WEATHERS)
    weather_next = random.randint(25, 45) * FPS
    sky = SKY_OF[weather]
    confetti = []
    penalty_flash = 0
    running = True
    while running:
        frames += 1
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                running = False
            if won and e.type == pygame.KEYDOWN:
                if win_name is not None:  # escrivint el nom
                    if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        nm = win_name.strip() or "Jugador"
                        rank = save_score(nm, win_score, win_secs)
                        win_info = (win_score, win_secs, load_scores(), rank)
                        win_name = None
                    elif e.key == pygame.K_BACKSPACE:
                        win_name = win_name[:-1]
                    elif e.unicode and e.unicode.isprintable() and len(win_name) < 10 and e.key != pygame.K_ESCAPE:
                        win_name += e.unicode
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return "again"
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and not on_ground and air_jumps < 1:
                vy = -13  # doble salt: prem ESPAI un altre cop a l'aire!
                air_jumps += 1
            if e.type == pygame.KEYDOWN and e.key == pygame.K_m and sling_cd == 0:
                if weapon == "bumerang" and boom is None:
                    boom = {"x": float(player.centerx), "y": float(player.y + 20), "dir": facing,
                            "phase": 0, "dist": 0, "angle": 0, "life": 0, "hit": False}
                elif weapon == "tiratxines":
                    stones.append({"x": float(player.centerx + 16 * facing), "y": float(player.y + 24), "dir": facing})
                    sling = 10
                elif weapon == "porra" and swing == 0:
                    swing = SWING_LEN
                    swing_hit = False
                elif weapon == "llança":
                    spears.append({"x": float(player.centerx + 14 * facing), "y": float(player.y + 24),
                                   "vx": 12.0 * facing, "vy": -3.5})
                elif weapon == "foc":
                    fireballs.append({"x": float(player.centerx + 20 * facing), "y": float(player.y + 20),
                                      "vx": 7.0 * facing, "vy": 0.0})
                elif weapon == "arc":
                    arrows.append({"x": float(player.centerx + 20 * facing), "y": float(player.y + 22), "dir": facing})
                elif weapon == "gel":
                    fireballs.append({"x": float(player.centerx + 20 * facing), "y": float(player.y + 16),
                                      "vx": 5.0 * facing, "vy": -4.0, "ice": True})
                elif weapon == "tornado" and not tornados:
                    tornados.append({"x": float(player.centerx + 40 * facing), "dir": facing})
                elif weapon == "roca" and not boulders:
                    boulders.append({"x": float(player.centerx + 30 * facing), "y": float(GROUND - 24),
                                     "dir": facing, "rot": 0.0, "fall": 0.0})
                sling_cd = WEAPON_CD[weapon]
        keys = pygame.key.get_pressed()
        vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vx = -5
            facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vx = 5
            facing = 1
        if keys[pygame.K_SPACE] and on_ground:
            vy = -13
            on_ground = False

        for p in platforms:
            ox, oy = p["r"].x, p["r"].y
            p["r"].x = p["x0"] + int(p["ax"] * math.sin(frames * p["sp"]))
            p["r"].y = p["y0"] + int(p["ay"] * math.sin(frames * p["sp"]))
            if p is riding:
                player.x += p["r"].x - ox
        riding = None
        player.x = max(0, min(W - player.w, player.x + vx))
        vy += 0.6
        player.y += int(vy)
        on_ground = False
        over_hole = player.left > HOLE_X0 and player.right < HOLE_X1
        if over_hole and player.bottom > GROUND:
            in_hole = True  # ha caigut al forat
        if in_hole:
            # dins del forat: les parets no et deixen sortir pels costats
            player.left = max(player.left, HOLE_X0)
            player.right = min(player.right, HOLE_X1)
        elif player.bottom >= GROUND and not over_hole:
            player.bottom = GROUND
            vy = 0
            on_ground = True
        if player.top > H:  # has caigut pel forat: tornes a aparèixer per dalt!
            player.x = random.choice((HOLE_X0 - 70, HOLE_X1 + 40))
            player.bottom = -10
            vy = 0
            in_hole = False
        for p in platforms:
            if vy >= 0 and player.colliderect(p["r"]) and player.bottom - int(vy) <= p["r"].top + 6:
                player.bottom = p["r"].top
                vy = 0
                on_ground = True
                riding = p

        if on_ground:
            air_jumps = 0
        boom_rect = None
        if boom is not None:
            boom["life"] += 1
            boom["angle"] += 28
            if boom["phase"] == 0:
                boom["x"] += 10 * boom["dir"]
                boom["dist"] += 10
                if boom["dist"] >= 280:
                    boom["phase"] = 1
            else:
                dx, dy = player.centerx - boom["x"], player.centery - boom["y"]
                dist = math.hypot(dx, dy)
                if dist < 22 or boom["life"] > 200:
                    boom = None
                else:
                    boom["x"] += 12 * dx / dist
                    boom["y"] += 12 * dy / dist
            if boom is not None:
                boom_rect = pygame.Rect(0, 0, 36, 36)
                boom_rect.center = (int(boom["x"]), int(boom["y"]))
        swing_rect = None
        if swing > 0:
            swing -= 1
            if 3 <= SWING_LEN - swing <= 11:
                swing_rect = pygame.Rect(player.right - 5 if facing == 1 else player.left - 55, player.y - 10, 60, 70)
        if sling:
            sling -= 1
        if sling_cd:
            sling_cd -= 1
        for st in stones:
            st["x"] += 16 * st["dir"]
        stones = [st for st in stones if -20 < st["x"] < W + 20]  # arriba fins a l'altra punta
        for sp in spears:
            sp["x"] += sp["vx"]
            sp["y"] += sp["vy"]
            sp["vy"] += 0.3
        spears = [sp for sp in spears if -40 < sp["x"] < W + 40 and sp["y"] < GROUND]
        for bl in boulders:
            bl["rot"] += 0.25 * bl["dir"]
            if bl["fall"]:
                bl["fall"] += 0.6
                bl["y"] += bl["fall"]
            else:
                bl["x"] += 6 * bl["dir"]
                if HOLE_X0 + 24 < bl["x"] < HOLE_X1 - 24:
                    bl["fall"] = 1.0  # cau pel forat
        boulders = [bl for bl in boulders if -60 < bl["x"] < W + 60 and bl["y"] < H + 40]
        for fb in fireballs:  # la bola bota pel terra
            fb["x"] += fb["vx"]
            fb["vy"] += 0.5
            fb["y"] += fb["vy"]
            if fb["y"] >= GROUND - 12 and not (HOLE_X0 < fb["x"] < HOLE_X1):
                fb["y"] = GROUND - 12
                fb["vy"] = -12.5 if fb.get("ice") else -8.5
        fireballs = [fb for fb in fireballs if -30 < fb["x"] < W + 30 and fb["y"] < GROUND + 40]
        for ar in arrows:
            ar["x"] += 22 * ar["dir"]
        arrows = [ar for ar in arrows if -40 < ar["x"] < W + 40]
        for tn in tornados:
            tn["x"] += 4 * tn["dir"]
        tornados = [tn for tn in tornados if -60 < tn["x"] < W + 60]
        dead_now = []
        gone = []
        for m in mammoths:
            m.update(platforms)
            if m.fall:
                if m.top > H:
                    gone.append(m)  # ha caigut pel forat
                continue
            hit_stone = next((st for st in stones if m.colliderect(pygame.Rect(int(st["x"]) - 8, int(st["y"]) - 8, 16, 16))), None)
            if hit_stone is not None:
                stones.remove(hit_stone)  # la pedra s'acaba aquí
            hit_spear = next((sp for sp in spears if m.colliderect(pygame.Rect(int(sp["x"]) - 14, int(sp["y"]) - 8, 28, 16))), None)
            if hit_spear is not None:
                spears.remove(hit_spear)
            hit_boulder = next((bl for bl in boulders if m.colliderect(pygame.Rect(int(bl["x"]) - 22, int(bl["y"]) - 22, 44, 44))), None)
            if hit_boulder is not None:
                boulders.remove(hit_boulder)
            hit_fire = next((fb for fb in fireballs if m.colliderect(pygame.Rect(int(fb["x"]) - 12, int(fb["y"]) - 12, 24, 24))), None)
            if hit_fire is not None:
                fireballs.remove(hit_fire)
                if hit_fire.get("ice"):
                    m.ice = True
            hit_boom = boom is not None and not boom["hit"] and boom_rect is not None and boom_rect.colliderect(m)
            if hit_boom:
                boom["hit"] = True  # el bumerang només en pot tocar un
            hit_swing = swing_rect is not None and not swing_hit and swing_rect.colliderect(m)
            if hit_swing:
                swing_hit = True  # un cop de porra, un mamut
            hit_arrow = next((ar for ar in arrows if m.colliderect(pygame.Rect(int(ar["x"]) - 24, int(ar["y"]) - 6, 48, 12))), None)
            if hit_arrow is not None:
                arrows.remove(hit_arrow)
            hit_tornado = next((tn for tn in tornados if m.colliderect(pygame.Rect(int(tn["x"]) - 30, GROUND - 125, 60, 125))), None)
            if hit_tornado is not None:
                tornados.remove(hit_tornado)
            if (hit_stone is not None or hit_spear is not None or hit_boulder is not None or hit_fire is not None
                    or hit_boom or hit_swing or hit_arrow is not None or hit_tornado is not None):
                dead_now.append(m)  # el mamut fa "puf!" i desapareix
                continue
            if player.colliderect(m.inflate(-18, -8)):
                if vy > 2 and player.bottom <= m.top + 24:
                    vy = -13  # bot a sobre del mamut!
                    air_jumps = 0
                elif hurt == 0 and m.stun == 0:
                    hurt = 100
                    hits += 1
                    combo_n = combo_t = 0  # perds el combo
                    score = max(0, score - 3)
                    side = 1 if player.centerx > m.centerx else -1
                    player.x = max(0, min(W - player.w, player.x + side * 80))
                    vy = -9
                    celebrate = 0
        for m in dead_now + gone:
            mammoths.remove(m)
            if m in dead_now:
                poofs.append([m.centerx, m.centery, 40, (150, 220, 255) if getattr(m, "ice", False) else (255, 225, 80)])
                add_points(5, m.centerx, m.top)
                dx = max(30, min(W - 70, m.centerx))
                if HOLE_X0 - 25 < dx < HOLE_X1 + 25:  # que no caigui al forat
                    dx = HOLE_X0 - 40 if dx < W // 2 else HOLE_X1 + 40
                pickups.append({"kind": random.choice([w_ for w_ in WEAPONS if w_ != weapon]), "r": pygame.Rect(dx - 18, -50, 36, 36),
                                "vy": 0.0, "plat": None, "off": 0, "life": PICKUP_LIFE * FPS})
            if reserve > 0:  # surt un mamut de reserva d'aquí a 3 segons
                reserve -= 1
                respawns.append(3 * FPS)
        respawns = [t - 1 for t in respawns]
        for t in respawns:
            if t <= 0:
                new = Mammoth(None, platforms, random.uniform(0.3, 0.5))
                mammoths.append(new)
                poofs.append([new.centerx, new.centery, 40])
        respawns = [t for t in respawns if t > 0]
        if not won and not mammoths and reserve == 0 and not respawns:
            won = True  # no queda cap mamut!
            pen = 5 * hits  # cada cop rebut = 5 segons més
            win_secs = frames / FPS + pen
            bonus = max(0, int(400 - 3 * win_secs))  # com més ràpid, més bonus
            win_score = score + bonus
            win_extra = (score, bonus, pen)
            rows = sorted(load_scores() + [("", win_score, round(win_secs, 1))], key=lambda e: (-e[1], e[2]))
            win_top = ("", win_score, round(win_secs, 1)) in rows[:5]  # entra a les 5 millors?
            win_name = ""  # ara et demana el nom
            win_info = (win_score, win_secs, load_scores(), -1)
        if combo_t > 0:
            combo_t -= 1
            if combo_t == 0:
                combo_n = 0  # has parat massa estona: es perd el combo
        if not won and frames % (10 * FPS) == 0:  # cada 10 segons perds 1 punt
            if score > 0:
                score -= 1
            penalty_flash = 60
        for pk in pickups[:]:
            pk["life"] -= 1
            r_ = pk["r"]
            if pk["plat"] is not None:  # va amb la plataforma
                r_.midbottom = (pk["plat"]["r"].centerx + pk["off"], pk["plat"]["r"].top)
            else:
                pk["vy"] = min(pk["vy"] + 0.5, 9)
                r_.y += int(pk["vy"])
                for p in platforms:
                    if pk["vy"] >= 0 and r_.colliderect(p["r"]) and r_.bottom - int(pk["vy"]) <= p["r"].top + 6:
                        pk["plat"], pk["off"] = p, r_.centerx - p["r"].centerx
                        r_.bottom = p["r"].top
                        break
                else:
                    if r_.bottom >= GROUND and not (HOLE_X0 < r_.centerx < HOLE_X1):
                        r_.bottom = GROUND
                        pk["vy"] = 0
                        pk["plat"] = None
                        pk["life"] = min(pk["life"], pk["life"])
            if player.colliderect(r_):
                weapon = pk["kind"]
                weapon_msg = 100
                for other in pickups:  # que cap altra arma al terra sigui igual que la que ja tens
                    if other["kind"] == weapon:
                        other["kind"] = random.choice([w_ for w_ in WEAPONS if w_ != weapon])
                boom = None
                swing = 0
                pickups.remove(pk)
            elif pk["life"] <= 0 or r_.top > H:
                pickups.remove(pk)  # no l'has agafat: et quedes amb la que tenies
        if weapon_msg:
            weapon_msg -= 1
        if hurt:
            hurt -= 1
        for f in foods:
            f.update(platforms)
        for f in foods[:]:
            if player.colliderect(f) or (boom_rect is not None and boom_rect.colliderect(f)):
                foods.remove(f)
                add_points(f.points, f.centerx, f.y)
                if f.kind == 5:
                    celebrate = 120  # 2 segons fent el 67
        if not any(f.kind != 5 for f in foods):
            foods = [Fruit(None, platforms) for _ in range(5)] + [Fruit(p, platforms) for p in platforms]
            foods.append(Fruit(None, platforms, 5))

        if frames >= weather_next:  # canvia el temps
            weather = random.choice([w for w in WEATHERS if w != weather])
            weather_next = frames + random.randint(25, 45) * FPS
        sky = lerp_color(sky, SKY_OF[weather], 0.03)
        screen.fill(sky)
        draw_background(screen, frames, weather)
        pygame.draw.rect(screen, GRASS, (0, GROUND, W, 14))
        pygame.draw.rect(screen, DIRT, (0, GROUND + 14, W, H))
        draw_hole(screen)
        for p in platforms:
            draw_platform(screen, p["r"])
        for f in foods:
            draw_fruit(screen, f, f.kind, frames)
        for m in mammoths:
            draw_mammoth(screen, m, frames)
        for pf in poofs[:]:
            pf[2] -= 1
            k = (40 - pf[2]) / 40
            for i in range(6):
                a = i * 1.047 + k
                cx_, cy_ = pf[0] + math.cos(a) * 40 * k, pf[1] + math.sin(a) * 30 * k
                pygame.draw.circle(screen, (245, 245, 245), (int(cx_), int(cy_)), int(18 * (1 - k)) + 3)
                draw_star(screen, (int(pf[0] + math.cos(a + 0.5) * 55 * k), int(pf[1] + math.sin(a + 0.5) * 45 * k)),
                          7, pf[3] if len(pf) > 3 else (255, 225, 80))
            if pf[2] <= 0:
                poofs.remove(pf)
        if hurt == 0 or (hurt // 5) % 2 == 0:
            draw_caveman(screen, player, facing, vx != 0, on_ground, frames, celebrate,
                         club=(boom is None and swing == 0 and sling == 0))
        if sling:
            draw_slingshot(screen, player, facing)
        for st in stones:
            draw_stone(screen, st)
        for sp in spears:
            draw_spear(screen, sp)
        for bl in boulders:
            draw_boulder(screen, bl)
        for fb in fireballs:
            if fb.get("ice"):
                draw_fireball_ice(screen, fb, frames)
            else:
                draw_fireball(screen, fb, frames)
        for ar in arrows:
            draw_arrow(screen, ar)
        for tn in tornados:
            draw_tornado(screen, tn, frames)
        for pk in pickups:
            blink = pk["life"] < 2 * FPS and (pk["life"] // 5) % 2 == 0
            if not blink:
                cx_, cy_ = pk["r"].center
                bob = int(3 * math.sin(frames * 0.2))
                draw_weapon_icon(screen, pk["kind"], cx_, cy_ + bob)
                frac = pk["life"] / (PICKUP_LIFE * FPS)
                pygame.draw.arc(screen, (255, 120, 60), (cx_ - 26, cy_ + bob - 26, 52, 52), math.pi / 2,
                                math.pi / 2 + 2 * math.pi * frac, 4)
        if swing > 0:
            draw_swing(screen, player, facing, SWING_LEN - swing, SWING_LEN)
        if boom is not None:
            draw_boomerang(screen, boom)
        if player.bottom > GROUND + 10:
            lab = big.render("Uiii!", True, (255, 255, 255))
            screen.blit(lab, lab.get_rect(midbottom=(player.centerx, max(40, player.y - 8))))
        if hurt > 60:
            lab = big.render("Au!", True, (230, 40, 40))
            screen.blit(lab, lab.get_rect(midbottom=(player.centerx, player.y - 8)))
        if celebrate:
            celebrate -= 1
            lab = big.render("67!", True, (255, 220, 40))
            screen.blit(lab, lab.get_rect(midbottom=(player.centerx, player.y - 25)))
        draw_weather_front(screen, frames, weather)
        mult = min(5, 1 + combo_n // 2)
        if combo_n > 0:
            col = [(255, 255, 255), (255, 235, 120), (255, 190, 60), (255, 130, 50), (255, 70, 70)][mult - 1]
            screen.blit(big.render(f"Combo x{mult}", True, col), (15, 158))
            pygame.draw.rect(screen, (0, 0, 0), (15, 198, 154, 12), border_radius=6)
            pygame.draw.rect(screen, col, (17, 200, int(150 * combo_t / COMBO_FRAMES), 8), border_radius=4)
        for pu in popups[:]:
            pu[1] -= 1.2
            pu[2] -= 1
            c_ = [(255, 255, 255), (255, 235, 120), (255, 190, 60), (255, 130, 50), (255, 70, 70)][pu[4] - 1]
            t_ = font.render(pu[3], True, c_)
            screen.blit(t_, t_.get_rect(center=(int(pu[0]), int(pu[1]))))
            if pu[2] <= 0:
                popups.remove(pu)
        screen.blit(font.render(f"Menjar: {score}", True, (255, 255, 255)), (15, 15))
        screen.blit(font.render(f"Mamuts de reserva: {reserve + len(respawns)}", True, (255, 255, 255)), (15, 45))
        screen.blit(font.render(f"Clima: {WEATHER_NAME[weather]}", True, (255, 255, 255)), (15, 75))
        draw_weapon_icon(screen, weapon, 32, 128, 30)
        screen.blit(font.render(f"Arma: {WEAPON_NAME[weapon]}  (M)", True, (255, 255, 255)), (58, 118))
        if weapon_msg:
            lab = big.render("Arma nova!", True, (255, 225, 60))
            screen.blit(lab, lab.get_rect(midbottom=(player.centerx, player.y - 40)))
        screen.blit(font.render("Fletxes: moure · Espai: saltar · M: usar l'arma · Esc: sortir", True, (255, 255, 255)), (15, H - 35))
        if penalty_flash > 0:
            penalty_flash -= 1
            lab = font.render("-1 punt (temps!)", True, (255, 90, 90))
            screen.blit(lab, (150, 15))
        if won and win_top:  # confeti!
            colors = [(255, 70, 70), (70, 120, 255), (255, 220, 50), (80, 220, 120), (255, 120, 220), (255, 255, 255)]
            for _ in range(2):
                confetti.append([random.uniform(0, W), -10.0, random.uniform(-1.5, 1.5), random.uniform(2, 5),
                                 random.choice(colors), random.uniform(0, 6)])
            for c in confetti[:]:
                c[0] += c[2] + math.sin(frames * 0.1 + c[5]) * 1.2
                c[1] += c[3]
                w_ = 6 + int(4 * abs(math.sin(frames * 0.2 + c[5])))
                pygame.draw.rect(screen, c[4], (int(c[0]), int(c[1]), w_, 10))
                if c[1] > H:
                    confetti.remove(c)
        if won:
            draw_win_panel(screen, big, font, win_info[0], win_info[1], win_info[2], win_info[3], win_name, frames, win_extra)
        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(0)  # necessari perquè funcioni al navegador (pygbag)
        if test and frames >= 120:
            break
    return "quit"


async def main():
    test = "--test" in sys.argv
    pygame.init()
    try:
        if sys.platform == "emscripten":  # al navegador, la pàgina ja fa de pantalla
            raise pygame.error("web")
        # pantalla completa: el joc s'escala al màxim que permet el dispositiu
        screen = pygame.display.set_mode((W, H), pygame.SCALED | pygame.FULLSCREEN)
    except pygame.error:
        screen = pygame.display.set_mode((W, H), pygame.SCALED | pygame.RESIZABLE)
    pygame.mouse.set_visible(False)
    pygame.display.set_caption("Cavernícola")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    big = pygame.font.Font(None, 64)
    while await run_game(screen, clock, font, big, test) == "again":
        pass
    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
