"""El nivell mentre s'hi juga: regles, col.lisions i ordre de dibuix.

Aquesta classe no sap res de finestres ni de fotogrames reals: fa un pas de
simulacio quan li ho demanen i es dibuixa quan li ho demanen.
"""

import math
import random
import pygame

from . import art, entities, hud, level as level_mod, scenery, scores, weapons
from .config import (W, H, FPS, GROUND, HOLE_X0, HOLE_X1, LIVES_START, LIVES_MAX,
                     STEAKS_PER_LIFE, MAMMOTH_SPAWN_GAP, GOLD_FIRST, GOLD_AGAIN,
                     GOLD_STAY, COMBO_SECONDS, COMBO_MAX, HURT_FRAMES,
                     TIME_PENALTY_EVERY, HIT_TIME_PENALTY, PICKUP_LIFE)

d = pygame.draw


def _secs(span):
    lo, hi = span
    return int(random.uniform(lo, hi) * FPS)


class Popup:
    """El `+5 x2` que puja i s'esvaeix."""

    __slots__ = ("x", "y", "life", "label", "mult")

    def __init__(self, x, y, label, mult):
        self.x, self.y = x, y
        self.life = 45
        self.label = label
        self.mult = mult

    def update(self):
        self.y -= 1.2
        self.life -= 1
        return self.life > 0


class Poof:
    """El nuvol de fum d'un mamut que desapareix."""

    __slots__ = ("x", "y", "life", "color")
    TOTAL = 40

    def __init__(self, x, y, color=(255, 225, 80)):
        self.x, self.y = x, y
        self.life = self.TOTAL
        self.color = color

    @property
    def progress(self):
        return (self.TOTAL - self.life) / self.TOTAL

    def update(self):
        self.life -= 1
        return self.life > 0


class Pickup:
    """Una arma que cau al terra i es pot agafar durant uns segons."""

    __slots__ = ("kind", "rect", "vy", "plat", "off", "life")

    def __init__(self, kind, x):
        self.kind = kind
        self.rect = pygame.Rect(x - 18, -50, 36, 36)
        self.vy = 0.0
        self.plat = None
        self.off = 0
        self.life = int(PICKUP_LIFE * FPS)

    def update(self, platforms):
        self.life -= 1
        r = self.rect
        if self.plat is not None:
            r.midbottom = (self.plat.rect.centerx + self.off, self.plat.rect.top)
        else:
            self.vy = min(self.vy + 0.5, 9)
            r.y += int(self.vy)
            for p in platforms:
                if self.vy >= 0 and r.colliderect(p.rect) and r.bottom - int(self.vy) <= p.rect.top + 6:
                    self.plat, self.off = p, r.centerx - p.rect.centerx
                    r.bottom = p.rect.top
                    break
            else:
                if r.bottom >= GROUND and not (HOLE_X0 < r.centerx < HOLE_X1):
                    r.bottom = GROUND
                    self.vy = 0
        return self.life > 0 and r.top <= H

    @property
    def blinking(self):
        return self.life < 2 * FPS and (self.life // 5) % 2 == 0


class Result:
    """Com ha acabat la partida."""

    def __init__(self, won, score, secs, base=0, bonus=0, penalty=0.0):
        self.won = won
        self.score = score
        self.secs = secs
        self.base = base
        self.bonus = bonus
        self.penalty = penalty
        self.name = "" if scores.would_enter(score, secs) else None
        self.top = scores.load()
        self.rank = -1
        self.confetti = []

    def submit(self):
        name = (self.name or "").strip() or "Jugador"
        self.rank = scores.save(name, self.score, self.secs)
        self.top = scores.load()
        self.name = None

    @property
    def celebrating(self):
        return self.won and (self.name is not None or self.rank >= 0)


class Stage:
    """Un nivell en marxa."""

    def __init__(self, level_index=0):
        self.level = level_mod.build(level_index)
        self.scenery = scenery.Scenery(self.level)
        self.player = entities.Player()
        self.frames = 0

        plats = self.level.platforms
        self.fruits = ([entities.Fruit(None, plats) for _ in range(self.level.fruits_ground)]
                       + [entities.Fruit(p, plats) for p in plats])
        self.mammoths = [entities.Mammoth(None, plats, random.uniform(0.3, 0.5))
                         for _ in range(self.level.mammoth_start)]
        self.projectiles = []
        self.pickups = []
        self.poofs = []
        self.popups = []

        self.score = 0
        self.lives = LIVES_START
        self.steaks = 0
        self.weapon = random.choice(weapons.WEAPON_KEYS)
        self.weapon_msg = 0
        self.cooldown = 0
        self.hits = 0
        self.combo_n = 0
        self.combo_t = 0
        self.penalty_flash = 0

        self.spawn_gap = 0
        self.gold = None
        self.gold_timer = _secs(GOLD_FIRST)
        self.result = None

    # ---------------------------------------------------------- comoditats --
    @property
    def body(self):
        """El Rect del cavernicola: el que les armes necessiten saber."""
        return self.player.rect

    @property
    def facing(self):
        return self.player.facing

    @property
    def elapsed(self):
        return self.frames / FPS

    @property
    def multiplier(self):
        return min(COMBO_MAX, 1 + self.combo_n // 2)

    @property
    def combo_frac(self):
        return self.combo_t / (COMBO_SECONDS * FPS)

    @property
    def over(self):
        return self.result is not None

    @property
    def mammoth_target(self):
        """Cada cop n'hi ha mes: no s'acaben mai."""
        grown = self.level.mammoth_start + int(self.elapsed / self.level.mammoth_every)
        return min(self.level.mammoth_max, grown)

    # ------------------------------------------------------------- events ---
    def handle_key(self, event):
        """Tecles que son un cop sol (no aguantades)."""
        if self.over:
            return self._handle_result_key(event)
        if event.key == pygame.K_UP:
            self.player.jump()
        elif event.key == pygame.K_z:
            self.fire()
        return None

    def _handle_result_key(self, event):
        r = self.result
        if r.name is not None:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                r.submit()
            elif event.key == pygame.K_BACKSPACE:
                r.name = r.name[:-1]
            elif event.unicode and event.unicode.isprintable() and len(r.name) < 10:
                r.name += event.unicode
            return None
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return "again"
        return None

    def handle_touch(self, controls):
        """Botons de la pantalla: un cop per toc."""
        if self.over:
            if controls.any_tap:
                r = self.result
                if r.name is not None:
                    r.submit()
                else:
                    return "again"
            return None
        if controls.tapped("jump"):
            self.player.jump()
        if controls.tapped("attack"):
            self.fire()
        return None

    # -------------------------------------------------------------- armes ---
    def fire(self):
        if self.cooldown > 0:
            return
        spec = weapons.spec(self.weapon)
        if spec.limit:
            alive = sum(1 for p in self.projectiles if isinstance(p, spec.cls))
            if alive >= spec.limit:
                return
        self.projectiles.append(spec.spawn(self))
        self.cooldown = spec.cooldown

    # ------------------------------------------------------------- punts ----
    def add_points(self, base, x, y):
        mult = self.multiplier
        pts = base * mult
        self.score += pts
        self.combo_n += 1
        self.combo_t = int(COMBO_SECONDS * FPS)
        self.popups.append(Popup(x, y, f"+{pts}" + (f" x{mult}" if mult > 1 else ""), mult))

    def break_combo(self):
        self.combo_n = self.combo_t = 0

    def add_steak(self):
        """Un mamut mort = un bistec. 10 bistecs = una vida mes."""
        self.steaks += 1
        if self.steaks >= STEAKS_PER_LIFE:
            self.steaks -= STEAKS_PER_LIFE
            self.lives = min(LIVES_MAX, self.lives + 1)
            self.popups.append(Popup(self.player.centerx, self.player.rect.y - 50,
                                     "+1 vida!", COMBO_MAX))

    def take_hit(self, from_x):
        self.player.knock_back(from_x, HURT_FRAMES)
        self.hits += 1
        self.lives -= 1
        self.break_combo()
        self.score = max(0, self.score - 3)
        if self.lives <= 0:
            self.game_over()

    # --------------------------------------------------------------- final --
    def game_over(self):
        self.result = Result(False, self.score, self.elapsed)

    def stage_clear(self):
        penalty = HIT_TIME_PENALTY * self.hits
        secs = self.elapsed + penalty
        bonus = max(0, int(400 - 3 * secs))
        self.result = Result(True, self.score + bonus, secs,
                             base=self.score, bonus=bonus, penalty=penalty)

    # ---------------------------------------------------------- simulacio ---
    def update(self, controls):
        self.frames += 1
        self.scenery.update()
        if self.over:
            self._update_confetti()
            return
        self.level.update(self.frames)
        self._update_player(controls)
        self._update_projectiles()
        self._update_mammoths()
        self._spawn_mammoths()
        self._update_fruits()
        self._update_gold()
        self._update_pickups()
        self._update_timers()
        self.poofs = [p for p in self.poofs if p.update()]
        self.popups = [p for p in self.popups if p.update()]

    def _update_player(self, controls):
        p = self.player
        p.move(controls.left, controls.right)
        p.physics(self.level.platforms)

    def _update_projectiles(self):
        if self.cooldown:
            self.cooldown -= 1
        self.projectiles = [pr for pr in self.projectiles if pr.update(self)]

    def _update_mammoths(self):
        alive = []
        for m in self.mammoths:
            m.update(self.level.platforms)
            if m.fell_out:
                continue                              # ha caigut pel forat
            alive.append(m)
            if m.fall:
                continue
            killer = self._hit_by(m)
            if killer is not None:
                alive.pop()
                self._kill(m, killer)
                continue
            self._player_vs_mammoth(m)
        self.mammoths = alive

    def _hit_by(self, mammoth):
        """Quin projectil li ha tocat? Les armes son dades: cap `if` per arma."""
        for pr in self.projectiles:
            if pr.can_hit() and mammoth.colliderect(pr.hitbox()):
                return pr
        return None

    def _kill(self, mammoth, projectile):
        if projectile.one_kill:
            projectile.spent = True
        if projectile.consumed_on_hit and projectile in self.projectiles:
            self.projectiles.remove(projectile)
        color = (150, 220, 255) if projectile.ice else (255, 225, 80)
        self.poofs.append(Poof(mammoth.centerx, mammoth.centery, color))
        self.add_points(mammoth.points, mammoth.centerx, mammoth.top)
        self.add_steak()
        self._drop_weapon(mammoth.centerx)

    def _drop_weapon(self, x):
        x = max(30, min(W - 70, x))
        if HOLE_X0 - 25 < x < HOLE_X1 + 25:           # que no caigui al forat
            x = HOLE_X0 - 40 if x < W // 2 else HOLE_X1 + 40
        self.pickups.append(Pickup(random.choice(weapons.others_than(self.weapon)), x))

    def _player_vs_mammoth(self, m):
        p = self.player
        if not p.rect.colliderect(m.inflate(-18, -8)):
            return
        if p.vy > 2 and p.rect.bottom <= m.top + 24:
            p.bounce()                                # bot a sobre del mamut
        elif not p.invulnerable and m.stun == 0:
            self.take_hit(m.centerx)

    def _spawn_mammoths(self):
        if self.spawn_gap > 0:
            self.spawn_gap -= 1
            return
        if len(self.mammoths) >= self.mammoth_target:
            return
        new = entities.Mammoth(None, self.level.platforms,
                               random.uniform(0.3, 0.5), from_sky=True)
        self.mammoths.append(new)
        self.poofs.append(Poof(new.centerx, new.centery))
        self.spawn_gap = int(MAMMOTH_SPAWN_GAP * FPS)

    def _update_fruits(self):
        plats = self.level.platforms
        for f in self.fruits:
            f.update(plats)
        boom = self._boomerang_box()
        for f in self.fruits[:]:
            if self.player.rect.colliderect(f) or (boom is not None and boom.colliderect(f)):
                self.fruits.remove(f)
                self.add_points(f.points, f.centerx, f.y)
        if not self.fruits:
            self.fruits = ([entities.Fruit(None, plats) for _ in range(self.level.fruits_ground)]
                           + [entities.Fruit(p, plats) for p in plats])

    def _boomerang_box(self):
        for pr in self.projectiles:
            if isinstance(pr, weapons.Boomerang):
                return pr.hitbox()
        return None

    def _update_gold(self):
        """El 67 surt de tant en tant, es queda una mica i marxa."""
        if self.gold is None:
            self.gold_timer -= 1
            if self.gold_timer <= 0:
                self.gold = entities.Gold67(None, self.level.platforms,
                                            int(GOLD_STAY * FPS))
            return
        self.gold.update(self.level.platforms)
        boom = self._boomerang_box()
        if self.player.rect.colliderect(self.gold) or (boom is not None and boom.colliderect(self.gold)):
            self.add_points(self.gold.points, self.gold.centerx, self.gold.y)
            self.player.celebrate = 120
            self.poofs.append(Poof(self.gold.centerx, self.gold.centery))
            self.gold = None
            self.stage_clear()
            return
        if self.gold.leaving:
            self.poofs.append(Poof(self.gold.centerx, self.gold.centery))
            self.gold = None
            self.gold_timer = _secs(GOLD_AGAIN)

    def _update_pickups(self):
        for pk in self.pickups[:]:
            if not pk.update(self.level.platforms):
                self.pickups.remove(pk)
                continue
            if self.player.rect.colliderect(pk.rect):
                self.weapon = pk.kind
                self.weapon_msg = 100
                for other in self.pickups:            # cap duplicat al terra
                    if other.kind == self.weapon:
                        other.kind = random.choice(weapons.others_than(self.weapon))
                self.projectiles = [p for p in self.projectiles
                                    if not isinstance(p, (weapons.Boomerang, weapons.Swing))]
                self.cooldown = 0
                self.pickups.remove(pk)

    def _update_timers(self):
        if self.combo_t > 0:
            self.combo_t -= 1
            if self.combo_t == 0:
                self.combo_n = 0
        if self.weapon_msg:
            self.weapon_msg -= 1
        if self.penalty_flash:
            self.penalty_flash -= 1
        if self.frames % int(TIME_PENALTY_EVERY * FPS) == 0:
            if self.score > 0:
                self.score -= 1
            self.penalty_flash = 60

    def _update_confetti(self):
        r = self.result
        if not r.celebrating:
            return
        colors = [(255, 70, 70), (70, 120, 255), (255, 220, 50),
                  (80, 220, 120), (255, 120, 220), (255, 255, 255)]
        for _ in range(2):
            r.confetti.append([random.uniform(0, W), -10.0, random.uniform(-1.5, 1.5),
                               random.uniform(2, 5), random.choice(colors), random.uniform(0, 6)])
        for c in r.confetti[:]:
            c[0] += c[2] + math.sin(self.frames * 0.1 + c[5]) * 1.2
            c[1] += c[3]
            if c[1] > H:
                r.confetti.remove(c)

    # ------------------------------------------------------------- dibuix ---
    def draw(self, screen, controls):
        frames = self.frames
        self.scenery.draw_back(screen, frames)
        self.scenery.draw_platforms(screen, self.level.platforms)
        for f in self.fruits:
            f.draw(screen, frames)
        if self.gold is not None:
            self.gold.draw(screen, frames)
        for m in self.mammoths:
            m.draw(screen, frames)
        hud.draw_poofs(screen, self.poofs)
        holding = not any(isinstance(p, (weapons.Boomerang, weapons.Swing))
                          for p in self.projectiles)
        self.player.draw(screen, frames, club=holding)
        if self.weapon == "tiratxines" and self.cooldown > 8:
            img = art.slingshot()
            screen.blit(img, img.get_rect(center=(self.player.centerx + 16 * self.facing,
                                                  self.player.rect.y + 26)))
        for pr in self.projectiles:
            pr.draw(screen, frames)
        self._draw_pickups(screen, frames)
        self._draw_labels(screen)
        self.scenery.draw_front(screen, frames)
        hud.draw_hud(screen, self, frames, controls)
        hud.draw_popups(screen, self.popups)
        controls.draw(screen)
        if self.over:
            self._draw_confetti(screen)
            hud.draw_result(screen, self.result, frames, controls.touch_ui)

    def _draw_pickups(self, screen, frames):
        for pk in self.pickups:
            if pk.blinking:
                continue
            cx, cy = pk.rect.center
            cy += int(3 * math.sin(frames * 0.2))
            weapons.draw_icon(screen, pk.kind, cx, cy)
            frac = pk.life / (PICKUP_LIFE * FPS)
            d.arc(screen, (255, 120, 60), (cx - 26, cy - 26, 52, 52),
                  math.pi / 2, math.pi / 2 + 2 * math.pi * frac, 4)

    def _draw_labels(self, screen):
        p = self.player
        if p.rect.bottom > GROUND + 10:
            hud.centered(screen, "Uiii!", (p.centerx, p.rect.y - 20), (255, 255, 255), hud.BIG)
        if p.hurt > 60:
            hud.centered(screen, "Au!", (p.centerx, p.rect.y - 20), (230, 40, 40), hud.BIG)
        if p.celebrate:
            hud.centered(screen, "67!", (p.centerx, p.rect.y - 40), (255, 220, 40), hud.BIG)
        if self.weapon_msg:
            hud.centered(screen, "Arma nova!", (p.centerx, p.rect.y - 55), (255, 225, 60), hud.BIG)

    def _draw_confetti(self, screen):
        for c in self.result.confetti:
            w_ = 6 + int(4 * abs(math.sin(self.frames * 0.2 + c[5])))
            d.rect(screen, c[4], (int(c[0]), int(c[1]), w_, 10))
