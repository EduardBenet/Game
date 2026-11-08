"""El decorat: cel, nuvols, terra, plataformes i el clima.

Tot surt de `art`, que ja el te dibuixat. Aqui nomes diem on va cada cosa,
de manera que un fotograma son unes poques desenes de `blit`.
"""

import random

from . import art
from .config import W, GROUND, FPS, SKY_OF, CLOUDS, WEATHER_CHANGE


class Scenery:
    """Fons i clima. El clima canvia sol cada mitja minuteta."""

    def __init__(self, level):
        self.level = level
        self.weather = level.random_weather()
        self.sky = SKY_OF[self.weather]
        self.next_change = random.randint(*WEATHER_CHANGE) * FPS
        self.clock = 0

    def update(self):
        self.clock += 1
        if self.clock >= self.next_change:
            self.weather = self.level.random_weather(avoid=self.weather)
            self.next_change = self.clock + random.randint(*WEATHER_CHANGE) * FPS
        self.sky = art.lerp_color(self.sky, SKY_OF[self.weather], 0.03)

    # --- darrere de tot ---
    def draw_back(self, screen, frames):
        screen.fill(self.sky)
        if self.weather == "sol":
            img = art.sun(frames // 52)
            screen.blit(img, img.get_rect(center=(W - 130, 95)))
        elif self.weather == "nit":
            screen.blit(art.night_sky(frames // 14), (0, 0))
        for cx, cy, k, sp in CLOUDS:
            img = art.cloud(self.weather, k)
            x = (cx + frames * sp) % (W + 300) - 150
            screen.blit(img, img.get_rect(center=(int(x), int(cy))))
        screen.blit(art.ground_layer(), (0, GROUND))

    def draw_platforms(self, screen, platforms):
        img = art.platform()
        for p in platforms:
            screen.blit(img, art.platform_origin(p.rect))

    # --- davant de tot ---
    def draw_front(self, screen, frames):
        if self.weather == "pluja":
            art.draw_rain(screen, frames)
            art.tint(screen, (223, 225, 232))
        elif self.weather == "neu":
            art.draw_snow(screen, frames)
        elif self.weather == "nit":
            art.tint(screen, (165, 168, 190))
