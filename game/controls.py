"""Comandaments: teclat a l'ordinador i botons a la pantalla al mobil.

El joc nomes pregunta "vas a l'esquerra?", "has saltat?". D'on ve l'ordre
(tecla, dit o ratoli) no li importa.
"""

import pygame

from . import cache
from .config import W, H

d = pygame.draw

# Botons a la pantalla, en coordenades del joc (1000 x 600).
BUTTONS = [
    ("left",    88, H - 78, 50, "<"),
    ("right",  200, H - 78, 50, ">"),
    ("attack", W - 210, H - 152, 46, "M"),
    ("jump",   W - 92, H - 78, 58, "^"),
]


def _button_sprite(radius, label, pressed):
    """Botons rodons ja dibuixats (normal i premut)."""
    def build():
        side = radius * 2 + 8
        surf = cache.new_surface((side, side))
        c = side // 2
        base = (255, 255, 255, 140) if pressed else (255, 255, 255, 55)
        ring = (255, 235, 120, 230) if pressed else (255, 255, 255, 125)
        d.circle(surf, base, (c, c), radius)
        d.circle(surf, ring, (c, c), radius, 4)
        glyph = cache.font(int(radius * 1.5)).render(label, True, (30, 30, 40))
        surf.blit(glyph, glyph.get_rect(center=(c, c)))
        return surf
    return cache.sprite(("button", radius, label, pressed), build)


class Controls:
    """Ajunta el teclat i els botons tactils en una sola resposta."""

    def __init__(self, force_touch=False):
        self.touch_ui = force_touch
        self._held = set()          # botons tactils aguantats
        self._pressed = set()       # botons tactils acabats de premer
        self._fingers = {}          # id del dit -> nom del boto
        self._mouse = None
        self._tapped_screen = False
        self._rects = {name: pygame.Rect(x - r, y - r, r * 2, r * 2)
                       for name, x, y, r, _ in BUTTONS}

    # ------------------------------------------------------------- events --
    def handle(self, event):
        """Torna True si l'event era per als botons de la pantalla."""
        if event.type in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            self.touch_ui = True
            pos = self._finger_pos(event)
            if event.type == pygame.FINGERUP:
                self._release(("f", event.finger_id))
            else:
                if event.type == pygame.FINGERDOWN:
                    self._tapped_screen = True
                self._press(("f", event.finger_id), pos)
            return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._tapped_screen = True
            self._press(("m",), event.pos)
            return self._mouse is not None
        if event.type == pygame.MOUSEMOTION and self._mouse is not None:
            self._press(("m",), event.pos)
            return True
        if event.type == pygame.MOUSEBUTTONUP:
            was = self._mouse is not None
            self._release(("m",))
            return was
        return False

    @staticmethod
    def _finger_pos(event):
        """Passa les coordenades 0..1 del dit a coordenades del joc."""
        win_w, win_h = pygame.display.get_window_size()
        if not win_w or not win_h:
            return (0, 0)
        scale = min(win_w / W, win_h / H) or 1
        ox = (win_w - W * scale) / 2
        oy = (win_h - H * scale) / 2
        return ((event.x * win_w - ox) / scale, (event.y * win_h - oy) / scale)

    def _button_at(self, pos):
        for name, rect in self._rects.items():
            if rect.collidepoint(pos):
                return name
        return None

    def _press(self, token, pos):
        name = self._button_at(pos)
        slot = self._fingers if token[0] == "f" else None
        before = self._fingers.get(token) if slot is not None else self._mouse
        if before == name:
            return
        if slot is not None:
            self._fingers[token] = name
        else:
            self._mouse = name
        if name and name not in self._held:
            self._pressed.add(name)
        self._recount()

    def _release(self, token):
        if token[0] == "f":
            self._fingers.pop(token, None)
        else:
            self._mouse = None
        self._recount()

    def _recount(self):
        self._held = {n for n in self._fingers.values() if n}
        if self._mouse:
            self._held.add(self._mouse)

    # ------------------------------------------------------------ consulta --
    def begin_frame(self):
        self._pressed.clear()
        self._tapped_screen = False

    @property
    def left(self):
        keys = pygame.key.get_pressed()
        return keys[pygame.K_LEFT] or keys[pygame.K_a] or "left" in self._held

    @property
    def right(self):
        keys = pygame.key.get_pressed()
        return keys[pygame.K_RIGHT] or keys[pygame.K_d] or "right" in self._held

    def tapped(self, name):
        """El boto s'acaba de premer (nomes aquest fotograma)."""
        return name in self._pressed

    @property
    def any_tap(self):
        """S'ha tocat la pantalla en qualsevol lloc."""
        return self._tapped_screen

    # -------------------------------------------------------------- dibuix --
    def draw(self, screen):
        if not self.touch_ui:
            return
        for name, x, y, r, label in BUTTONS:
            img = _button_sprite(r, label, name in self._held)
            screen.blit(img, img.get_rect(center=(x, y)))

    def help_text(self):
        if self.touch_ui:
            return "Toca < > per moure't  ·  ^ per saltar  ·  M per l'arma"
        return "Fletxes: moure  ·  Espai: saltar  ·  M: usar l'arma  ·  Esc: sortir"
