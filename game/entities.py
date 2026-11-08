"""Els personatges: fruites, el 67, mamuts i el cavernicola.

Tots els que salten d'un lloc a un altre comparteixen `Hopper`, aixi que un
bestiar nou nomes ha d'heretar i canviar el que faci diferent.
"""

import math
import random
import pygame

from . import art
from .config import (W, H, GROUND, HOLE_X0, HOLE_X1, GRAVITY, JUMP_V, MOVE_V,
                     AIR_JUMPS, POINTS_FRUIT, POINTS_GOLD, POINTS_MAMMOTH)
from .level import ground_x


class Hopper(pygame.Rect):
    """Base del que salta entre el terra i les plataformes."""

    size_px = (30, 30)
    points = 0
    wait_range = (40, 160)
    first_wait = (20, 150)
    jump_slow = 1          # >1 = salta mes a poc a poc

    def __init__(self, home, platforms):
        super().__init__(0, 0, *self.size_px)
        self.home = home                     # None = terra, o una Platform
        self.off = self.start_offset(home)
        self.wait = random.randint(*self.first_wait)
        self.t = 0
        self.dest = home
        self.dest_off = self.off
        self.dur = 1
        self.lift = 0.0
        self.sx, self.sy = 0, 0
        self.rest_pos()

    def start_offset(self, home):
        return random.randint(-55, 55) if home else ground_x()

    def spot(self, home, off):
        if home is None:
            return off, GROUND
        return home.top_at(off)

    def rest_pos(self):
        self.midbottom = self.spot(self.home, self.off)

    def land(self):
        self.wait = random.randint(*self.wait_range)

    def update(self, platforms):
        if self.wait > 0:
            self.wait -= 1
            self.rest_pos()
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
            self.land()
            self.rest_pos()

    def choose(self, platforms):
        """Tria un lloc proper: la mateixa plataforma, el terra o una altra."""
        self.sx, self.sy = self.midbottom
        options = [None] + list(platforms)
        near = [h for h in options
                if h is not self.home
                and abs(self.spot(h, 0)[0] - self.sx) < 380
                and self.sy - self.spot(h, 0)[1] < 150]
        self.dest = random.choice(near) if (near and random.random() < 0.7) else self.home
        self.dest_off = ground_x() if self.dest is None else random.randint(-55, 55)
        ex, ey = self.spot(self.dest, self.dest_off)
        self.dur = (40 + int(abs(ex - self.sx) / 12)) * self.jump_slow
        self.lift = 40 + max(0, self.sy - ey) * 0.6
        self.t = 1


class Fruit(Hopper):
    """Fruita que fa salts. Val 1 punt."""

    points = POINTS_FRUIT

    def __init__(self, home, platforms):
        self.kind = random.randint(0, 4)
        super().__init__(home, platforms)

    def draw(self, screen, frames):
        img = art.fruit(self.kind)
        screen.blit(img, img.get_rect(center=self.center))


class Gold67(Hopper):
    """El 67 daurat: molt rar, va molt rapid i acaba el nivell."""

    size_px = (38, 38)
    points = POINTS_GOLD
    wait_range = (10, 40)
    first_wait = (6, 20)

    def __init__(self, home, platforms, stay_frames):
        super().__init__(home, platforms)
        self.stay = stay_frames

    def update(self, platforms):
        self.stay -= 1
        super().update(platforms)

    @property
    def leaving(self):
        return self.stay <= 0

    def choose(self, platforms):
        super().choose(platforms)
        self.dur = max(14, self.dur // 3)

    def draw(self, screen, frames):
        img = art.gold(frames)
        screen.blit(img, img.get_rect(center=(self.centerx, self.centery - 3)))


class Mammoth(Hopper):
    """Mamut dolent: passeja, puja per les plataformes i cau pel forat."""

    size_px = (78, 54)
    points = POINTS_MAMMOTH
    wait_range = (250, 600)
    first_wait = (200, 500)
    jump_slow = 3

    def __init__(self, home, platforms, speed, from_sky=False):
        self.speed = speed
        super().__init__(home, platforms)
        self.dir = random.choice((-1, 1))
        self.step = random.randint(0, 30)
        self.stun = 0
        self.frozen = False
        self.fall = 0.0                    # cau pel forat
        self.drop = 1.0 if from_sky else 0.0
        if from_sky:
            self.home = None
            self.off = ground_x(60, W - 90)
            self.midbottom = (int(self.off), -10)

    def start_offset(self, home):
        return random.randint(-30, 30) if home else ground_x(300, W - 120)

    def update(self, platforms):
        self.step += 1
        if self.fall:
            self.fall += 0.6
            self.y += int(self.fall)
            return
        if self.drop:
            self.drop += 0.6
            self.y += int(self.drop)
            if self.bottom >= GROUND:
                self.drop = 0.0
                self.home = None
                self.wait = random.randint(*self.wait_range)
                self.off = max(60, min(W - 90, self.centerx))
                self.rest_pos()
            return
        if self.stun > 0:
            self.stun -= 1
            if self.wait > 0:
                return
        if self.wait > 0:                  # passeja
            self.wait -= 1
            lo, hi = (-34, 34) if self.home else (50, W - 50)
            self.off += self.speed * self.dir
            if self.off < lo or self.off > hi:
                self.dir = -self.dir
                self.off = max(lo, min(hi, self.off))
            elif not self.home and HOLE_X0 + 35 < self.off < HOLE_X1 - 35:
                self.fall = 1.0            # ha caigut al forat!
            self.rest_pos()
            if self.wait == 0:
                self.choose(platforms)
            return
        jumping = self.t > 0
        super().update(platforms)
        if jumping and self.t == 0:
            self.wait = random.randint(*self.wait_range)

    @property
    def fell_out(self):
        return self.fall and self.top > H

    def choose(self, platforms):
        super().choose(platforms)
        if self.dest is not None:
            self.dest_off = max(-34, min(34, self.dest_off))
        ex, _ = self.spot(self.dest, self.dest_off)
        self.dir = 1 if ex >= self.sx else -1

    def draw(self, screen, frames):
        img = art.mammoth((self.step // 14) % 2, self.dir)
        sh = art.shadow(90)
        screen.blit(sh, (self.centerx - 45, self.bottom - 6))
        screen.blit(img, img.get_rect(midbottom=(self.centerx, self.bottom + 3)))
        if self.stun > 0:
            for i in range(3):
                a = self.step * 0.15 + i * 2.09
                art.draw_star(screen,
                              (self.centerx + self.dir * 14 + int(math.cos(a) * 22),
                               self.top - 4 + int(math.sin(a) * 5)), 6, (255, 235, 90))


class Player:
    """El cavernicola: moviment, salts, el forat i els cops rebuts."""

    def __init__(self):
        self.rect = pygame.Rect(100, GROUND - 50, 30, 50)
        self.vx = 0.0
        self.vy = 0.0
        self.facing = 1
        self.on_ground = True
        self.in_hole = False
        self.air_jumps = 0
        self.hurt = 0
        self.celebrate = 0
        self.riding = None

    # --- comoditats ---
    @property
    def centerx(self):
        return self.rect.centerx

    @property
    def walking(self):
        return self.vx != 0

    @property
    def invulnerable(self):
        return self.hurt > 0

    @property
    def visible(self):
        return self.hurt == 0 or (self.hurt // 5) % 2 == 0

    def jump(self):
        """Salta des del terra, o fa el doble salt a l'aire."""
        if self.on_ground:
            self.vy = JUMP_V
            self.on_ground = False
        elif self.air_jumps < AIR_JUMPS:
            self.vy = JUMP_V
            self.air_jumps += 1

    def bounce(self):
        self.vy = JUMP_V
        self.air_jumps = 0

    def knock_back(self, from_x, hurt_frames):
        self.hurt = hurt_frames
        side = 1 if self.rect.centerx > from_x else -1
        self.rect.x = max(0, min(W - self.rect.w, self.rect.x + side * 80))
        self.vy = -9
        self.celebrate = 0

    def move(self, left, right):
        self.vx = 0.0
        if left:
            self.vx = -MOVE_V
            self.facing = -1
        if right:
            self.vx = MOVE_V
            self.facing = 1

    def physics(self, platforms):
        r = self.rect
        if self.riding is not None:
            r.x += self.riding.dx
        self.riding = None
        r.x = max(0, min(W - r.w, r.x + int(self.vx)))
        self.vy += GRAVITY
        r.y += int(self.vy)
        self.on_ground = False
        over_hole = r.left > HOLE_X0 and r.right < HOLE_X1
        if over_hole and r.bottom > GROUND:
            self.in_hole = True
        if self.in_hole:
            r.left = max(r.left, HOLE_X0)
            r.right = min(r.right, HOLE_X1)
        elif r.bottom >= GROUND and not over_hole:
            r.bottom = GROUND
            self.vy = 0
            self.on_ground = True
        if r.top > H:                       # surt per dalt un altre cop
            r.x = random.choice((HOLE_X0 - 70, HOLE_X1 + 40))
            r.bottom = -10
            self.vy = 0
            self.in_hole = False
        for p in platforms:
            if self.vy >= 0 and r.colliderect(p.rect) and r.bottom - int(self.vy) <= p.rect.top + 6:
                r.bottom = p.rect.top
                self.vy = 0
                self.on_ground = True
                self.riding = p
        if self.on_ground:
            self.air_jumps = 0
        if self.hurt:
            self.hurt -= 1
        if self.celebrate:
            self.celebrate -= 1

    def draw(self, screen, frames, club=True):
        if not self.visible:
            return
        swing = 0
        if self.walking and self.on_ground:
            swing = 6 if (frames // 6) % 2 == 0 else -6
        if not self.on_ground:
            swing = 8
        celebrate_up = None
        if self.celebrate:
            celebrate_up = (self.celebrate // 7) % 2 == 0
        img = art.caveman(self.facing, swing, self.on_ground, celebrate_up, club)
        screen.blit(img, (self.rect.x - art.CAVEMAN_PAD, self.rect.y - art.CAVEMAN_PAD))
