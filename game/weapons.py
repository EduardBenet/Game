"""Les armes, com a dades.

Afegir una arma nova = una classe `Projectile` + una entrada a `register(...)`.
Ni el bucle del joc ni les col.lisions no s'han de tocar mai mes.
"""

import math
import pygame

from . import art, cache
from .config import W, GROUND, HOLE_X0, HOLE_X1

d = pygame.draw


# ------------------------------------------------------------ projectils ---

class Projectile:
    """Base de tot el que vola i pot matar un mamut."""

    consumed_on_hit = True    # desapareix quan toca un mamut
    one_kill = True           # nomes pot matar un mamut
    ice = False               # deixa el mamut congelat

    def __init__(self, x, y, facing):
        self.x = float(x)
        self.y = float(y)
        self.dir = facing
        self.life = 0
        self.spent = False    # ja ha fet la seva mort

    def update(self, world):
        """Mou el projectil. Torna False quan ha de desapareixer."""
        self.life += 1
        return True

    def hitbox(self):
        return pygame.Rect(int(self.x) - 10, int(self.y) - 10, 20, 20)

    def can_hit(self):
        return not self.spent

    def draw(self, screen, frames):
        raise NotImplementedError

    def _inside(self, margin=40):
        return -margin < self.x < W + margin


class Boomerang(Projectile):
    """La porra bumerang: va, torna i es queda a la ma."""

    consumed_on_hit = False

    def __init__(self, x, y, facing):
        super().__init__(x, y, facing)
        self.phase = 0
        self.dist = 0.0
        self.angle = 0.0

    def update(self, world):
        self.life += 1
        self.angle += 28
        if self.phase == 0:
            self.x += 10 * self.dir
            self.dist += 10
            if self.dist >= 280:
                self.phase = 1
            return True
        dx = world.body.centerx - self.x
        dy = world.body.centery - self.y
        dist = math.hypot(dx, dy)
        if dist < 22 or self.life > 200:
            return False
        self.x += 12 * dx / dist
        self.y += 12 * dy / dist
        return True

    def hitbox(self):
        return pygame.Rect(int(self.x) - 18, int(self.y) - 18, 36, 36)

    def draw(self, screen, frames):
        img = art.club_rotated(self.angle % 360)
        screen.blit(img, img.get_rect(center=(int(self.x), int(self.y))))


class Swing(Projectile):
    """El cop de porra: no vola, acompanya el cavernicola."""

    consumed_on_hit = False
    LEN = 14

    def update(self, world):
        self.life += 1
        self.dir = world.facing
        self.x = world.body.centerx
        self.y = world.body.y
        return self.life <= self.LEN

    def can_hit(self):
        return not self.spent and 3 <= self.life <= 11

    def hitbox(self):
        if not (3 <= self.life <= 11):
            return pygame.Rect(0, 0, 0, 0)
        x = self.x + 10 if self.dir == 1 else self.x - 65
        return pygame.Rect(int(x), int(self.y) - 10, 60, 70)

    def draw(self, screen, frames):
        s = min(1.0, self.life / self.LEN)
        th = math.radians(10 + 150 * s)
        px, py = self.x + 10 * self.dir, self.y + 26
        L = 40

        def pos(a):
            return px + L * math.sin(a) * self.dir, py - L * math.cos(a)

        for k in range(1, 6):
            a = th - k * 0.16
            if a > 0:
                tx, ty = pos(a)
                d.circle(screen, (255, 255, 255), (int(tx), int(ty)), 8 - k)
        tx, ty = pos(th)
        d.line(screen, (100, 65, 30), (int(px), int(py)), (int(tx), int(ty)), 7)
        d.circle(screen, (120, 78, 36), (int(tx), int(ty)), 9)


class Stone(Projectile):
    """Pedra del tiratxines: va recta i molt rapida."""

    def update(self, world):
        self.life += 1
        self.x += 16 * self.dir
        return -20 < self.x < W + 20

    def hitbox(self):
        return pygame.Rect(int(self.x) - 8, int(self.y) - 8, 16, 16)

    def draw(self, screen, frames):
        img = art.stone()
        if self.dir < 0:
            img = pygame.transform.flip(img, True, False)
        screen.blit(img, img.get_rect(center=(int(self.x), int(self.y))))


class Spear(Projectile):
    """Llanca: vola i va caient."""

    def __init__(self, x, y, facing):
        super().__init__(x, y, facing)
        self.vx = 12.0 * facing
        self.vy = -3.5

    def update(self, world):
        self.life += 1
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        return self._inside() and self.y < GROUND

    def hitbox(self):
        return pygame.Rect(int(self.x) - 14, int(self.y) - 8, 28, 16)

    def draw(self, screen, frames):
        ang = math.degrees(math.atan2(self.vy, self.vx))
        img = art.spear_rotated((-ang) % 360)
        screen.blit(img, img.get_rect(center=(int(self.x), int(self.y))))


class Boulder(Projectile):
    """Roca rodant: va per terra i cau pel forat."""

    def __init__(self, x, y, facing):
        super().__init__(x, GROUND - 24, facing)
        self.rot = 0.0
        self.fall = 0.0

    def update(self, world):
        self.life += 1
        self.rot += 0.25 * self.dir
        if self.fall:
            self.fall += 0.6
            self.y += self.fall
        else:
            self.x += 6 * self.dir
            if HOLE_X0 + 24 < self.x < HOLE_X1 - 24:
                self.fall = 1.0
        return self._inside(60) and self.y < GROUND + 120

    def hitbox(self):
        return pygame.Rect(int(self.x) - 22, int(self.y) - 22, 44, 44)

    def draw(self, screen, frames):
        img = art.boulder(int(self.rot * 2.5))
        screen.blit(img, img.get_rect(center=(int(self.x), int(self.y))))


class Fireball(Projectile):
    """Bola de foc: bota pel terra."""

    BOUNCE = -8.5

    def __init__(self, x, y, facing):
        super().__init__(x, y, facing)
        self.vx = 7.0 * facing
        self.vy = 0.0

    def update(self, world):
        self.life += 1
        self.x += self.vx
        self.vy += 0.5
        self.y += self.vy
        if self.y >= GROUND - 12 and not (HOLE_X0 < self.x < HOLE_X1):
            self.y = GROUND - 12
            self.vy = self.BOUNCE
        return self._inside(30) and self.y < GROUND + 40

    def hitbox(self):
        return pygame.Rect(int(self.x) - 12, int(self.y) - 12, 24, 24)

    def draw(self, screen, frames):
        img = art.fireball(frames // 2, ice=self.ice)
        if self.vx < 0:
            img = pygame.transform.flip(img, True, False)
        screen.blit(img, img.get_rect(center=(int(self.x), int(self.y))))


class Iceball(Fireball):
    """Bola de gel: bota mes alt i congela el mamut."""

    ice = True
    BOUNCE = -12.5

    def __init__(self, x, y, facing):
        super().__init__(x, y, facing)
        self.vx = 5.0 * facing
        self.vy = -4.0


class Arrow(Projectile):
    """Fletxa: la mes rapida de totes."""

    def update(self, world):
        self.life += 1
        self.x += 22 * self.dir
        return self._inside()

    def hitbox(self):
        return pygame.Rect(int(self.x) - 24, int(self.y) - 6, 48, 12)

    def draw(self, screen, frames):
        img = art.arrow()
        if self.dir < 0:
            img = pygame.transform.flip(img, True, False)
        screen.blit(img, img.get_rect(center=(int(self.x), int(self.y))))


class Tornado(Projectile):
    """Tornado: camina pel terra i s'emporta el mamut que troba."""

    def update(self, world):
        self.life += 1
        self.x += 4 * self.dir
        return self._inside(60)

    def hitbox(self):
        return pygame.Rect(int(self.x) - 30, GROUND - 125, 60, 125)

    def draw(self, screen, frames):
        img = art.tornado(frames // 2)
        screen.blit(img, img.get_rect(midbottom=(int(self.x), GROUND + 8)))


# -------------------------------------------------------------- registre ---

class WeaponSpec:
    """Tot el que el joc necessita saber d'una arma."""

    def __init__(self, key, name, cls, cooldown, limit=0, offset=(20, 20), icon=None):
        self.key = key
        self.name = name
        self.cls = cls
        self.cooldown = cooldown
        self.limit = limit            # 0 = tants com vulguis a la vegada
        self.offset = offset          # d'on surt, respecte al cavernicola
        self.icon = icon or (lambda surf, cx, cy, k: None)

    def spawn(self, world):
        ox, oy = self.offset
        return self.cls(world.body.centerx + ox * world.facing,
                        world.body.y + oy, world.facing)


WEAPONS = {}
WEAPON_KEYS = []


def register(spec):
    WEAPONS[spec.key] = spec
    WEAPON_KEYS.append(spec.key)
    return spec


def spec(key):
    return WEAPONS[key]


def name_of(key):
    return WEAPONS[key].name


def others_than(key):
    return [k for k in WEAPON_KEYS if k != key]


# -------------------------------------------------------------- icones -----

def _icon_boomerang(surf, cx, cy, k):
    img = pygame.transform.rotozoom(art.club(), 0, 0.8 * k)
    surf.blit(img, img.get_rect(center=(cx, cy)))


def _icon_club(surf, cx, cy, k):
    img = pygame.transform.rotozoom(art.club(), 30, 0.9 * k)
    surf.blit(img, img.get_rect(center=(cx, cy)))
    d.circle(surf, (255, 255, 255), (cx + int(9 * k), cy - int(9 * k)), int(3 * k))


def _icon_sling(surf, cx, cy, k):
    d.line(surf, (100, 65, 30), (cx, cy + int(12 * k)), (cx, cy), int(5 * k))
    d.line(surf, (100, 65, 30), (cx, cy), (cx - int(8 * k), cy - int(12 * k)), int(4 * k))
    d.line(surf, (100, 65, 30), (cx, cy), (cx + int(8 * k), cy - int(12 * k)), int(4 * k))
    d.circle(surf, (110, 110, 120), (cx, cy - int(13 * k)), int(4 * k))


def _icon_spear(surf, cx, cy, k):
    img = pygame.transform.rotozoom(art.spear(), 35, 0.55 * k)
    surf.blit(img, img.get_rect(center=(cx, cy)))


def _icon_fire(surf, cx, cy, k):
    d.circle(surf, (255, 120, 20), (cx, cy + int(2 * k)), int(12 * k))
    d.polygon(surf, (255, 120, 20), [(cx - int(8 * k), cy), (cx, cy - int(16 * k)), (cx + int(8 * k), cy)])
    d.circle(surf, (255, 210, 60), (cx, cy + int(4 * k)), int(7 * k))
    d.circle(surf, (255, 250, 200), (cx, cy + int(6 * k)), int(3 * k))


def _icon_bow(surf, cx, cy, k):
    d.arc(surf, (120, 80, 40), (cx - int(14 * k), cy - int(15 * k), int(18 * k), int(30 * k)), -1.2, 1.2, 4)
    d.line(surf, (230, 230, 230), (cx - int(7 * k), cy - int(14 * k)), (cx - int(7 * k), cy + int(14 * k)), 1)
    d.line(surf, (120, 80, 40), (cx - int(8 * k), cy), (cx + int(14 * k), cy), 2)
    d.polygon(surf, (190, 195, 205), [(cx + int(14 * k), cy), (cx + int(8 * k), cy - int(4 * k)),
                                      (cx + int(8 * k), cy + int(4 * k))])


def _icon_ice(surf, cx, cy, k):
    d.circle(surf, (110, 190, 245), (cx, cy), int(13 * k))
    d.circle(surf, (190, 235, 255), (cx - int(3 * k), cy - int(3 * k)), int(8 * k))
    d.line(surf, (255, 255, 255), (cx - int(9 * k), cy), (cx + int(9 * k), cy), 2)
    d.line(surf, (255, 255, 255), (cx, cy - int(9 * k)), (cx, cy + int(9 * k)), 2)


def _icon_tornado(surf, cx, cy, k):
    for i in range(5):
        w_ = int((24 - i * 4) * k)
        d.ellipse(surf, (150, 160, 175),
                  (cx - w_ // 2 + int((i % 2) * 2 * k), cy - int(13 * k) + int(i * 6 * k), w_, int(6 * k)), 2)


def _icon_rock(surf, cx, cy, k):
    d.circle(surf, (110, 105, 100), (cx, cy), int(13 * k))
    d.circle(surf, (150, 145, 138), (cx - int(3 * k), cy - int(3 * k)), int(9 * k))
    d.line(surf, (80, 75, 70), (cx - int(5 * k), cy + int(2 * k)), (cx + int(3 * k), cy - int(2 * k)), 2)


def icon(key, size=36):
    """Bombolla amb la icona de l'arma, ja dibuixada i guardada."""
    def build():
        k = size / 36.0
        side = int(52 * k)
        surf = cache.new_surface((side, side))
        c = side // 2
        d.circle(surf, (255, 245, 190), (c, c), int(22 * k))
        d.circle(surf, (230, 170, 40), (c, c), int(22 * k), 3)
        WEAPONS[key].icon(surf, c, c, k)
        return surf
    return cache.sprite(("weapon_icon", key, size), build)


def draw_icon(screen, key, cx, cy, size=36):
    img = icon(key, size)
    screen.blit(img, img.get_rect(center=(cx, cy)))


# --- el cataleg ------------------------------------------------------------
# Per afegir una arma: una classe a dalt i una linia aqui. Res mes.

register(WeaponSpec("bumerang", "Porra bumerang", Boomerang, cooldown=0, limit=1,
                    offset=(0, 20), icon=_icon_boomerang))
register(WeaponSpec("tiratxines", "Tiratxines", Stone, cooldown=18,
                    offset=(16, 24), icon=_icon_sling))
register(WeaponSpec("porra", "Porra de cops", Swing, cooldown=0, limit=1,
                    offset=(0, 0), icon=_icon_club))
register(WeaponSpec("llanca", "Llança", Spear, cooldown=26,
                    offset=(14, 24), icon=_icon_spear))
register(WeaponSpec("roca", "Roca rodant", Boulder, cooldown=70, limit=1,
                    offset=(30, 0), icon=_icon_rock))
register(WeaponSpec("foc", "Bola de foc", Fireball, cooldown=30,
                    offset=(20, 20), icon=_icon_fire))
register(WeaponSpec("arc", "Arc i fletxa", Arrow, cooldown=20,
                    offset=(20, 22), icon=_icon_bow))
register(WeaponSpec("gel", "Bola de gel", Iceball, cooldown=32,
                    offset=(20, 16), icon=_icon_ice))
register(WeaponSpec("tornado", "Tornado", Tornado, cooldown=70, limit=1,
                    offset=(40, 0), icon=_icon_tornado))
