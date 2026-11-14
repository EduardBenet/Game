"""Els nivells, com a dades.

Afegir un nivell = una entrada mes a `LEVELS`. Ni el bucle del joc ni el
dibuix no s'han de tocar.
"""

import math
import random
import pygame

from .config import W, GROUND, HOLE_X0, HOLE_X1, WEATHERS


def ground_x(lo=60, hi=None):
    """Un lloc del terra que no caigui dins del forat."""
    hi = W - 90 if hi is None else hi
    for _ in range(40):
        x = random.randint(lo, hi)
        if not (HOLE_X0 - 30 < x < HOLE_X1 + 30):
            return x
    return lo


class Platform:
    """Una plataforma. Si `ax`/`ay` no son zero, es mou sola."""

    __slots__ = ("rect", "x0", "y0", "ax", "ay", "sp", "dx")

    def __init__(self, x, height, ax=0, ay=0, sp=0.0, width=140, thick=18):
        self.x0 = x
        self.y0 = GROUND - height
        self.ax = ax
        self.ay = ay
        self.sp = sp
        self.dx = 0                       # quant s'ha mogut aquest pas
        self.rect = pygame.Rect(x, self.y0, width, thick)

    @property
    def moving(self):
        return self.sp != 0.0 and (self.ax or self.ay)

    def update(self, frames):
        if not self.moving:
            self.dx = 0
            return
        old = self.rect.x
        self.rect.x = self.x0 + int(self.ax * math.sin(frames * self.sp))
        self.rect.y = self.y0 + int(self.ay * math.sin(frames * self.sp))
        self.dx = self.rect.x - old

    def top_at(self, offset):
        return (self.rect.centerx + offset, self.rect.top - 4)


class Level:
    """Un nivell muntat i llest per jugar."""

    def __init__(self, data):
        self.data = data
        self.name = data["nom"]
        self.platforms = [Platform(**p) for p in data["plataformes"]]
        self.fruits_ground = data.get("fruites_terra", 5)
        self.mammoth_start = data.get("mamuts_inici", 2)
        self.mammoth_every = data.get("mamuts_cada", 18.0)
        self.mammoth_max = data.get("mamuts_max", 14)
        self.weathers = data.get("climes", WEATHERS)

    def update(self, frames):
        for p in self.platforms:
            p.update(frames)

    def random_weather(self, avoid=None):
        pool = [w for w in self.weathers if w != avoid] or self.weathers
        return random.choice(pool)


# --- el cataleg de nivells -------------------------------------------------
# `alcada` es l'altura sobre el terra. `ax`/`ay`/`sp` fan que la plataforma
# es mogui (amplitud en pixels i velocitat).

LEVELS = [
    {
        "nom": "La vall dels mamuts",
        "plataformes": [
            {"x": 320, "height": 110, "ay": 40, "sp": 0.03},
            {"x": 650, "height": 190, "ax": 110, "sp": 0.025},
            {"x": 30, "height": 100},
            {"x": 190, "height": 200},
            {"x": 450, "height": 290},
            {"x": 860, "height": 110},
            {"x": 790, "height": 300},
        ],
        "fruites_terra": 5,
        "mamuts_inici": 1,
        "mamuts_cada": 18.0,
        "mamuts_max": 14,
    },
]


def build(index=0):
    return Level(LEVELS[index % len(LEVELS)])
