"""Els marcadors i els cartells.

Tot el text passa per `cache.text`, aixi que un fotograma no renderitza
lletres: nomes recupera les que ja estan fetes.
"""

import math
import pygame

from . import art, cache, weapons
from .config import (W, H, WHITE, GOLD, RED, BLUE, DBLUE, COMBO_COLORS,
                     STEAKS_PER_LIFE)
from .scores import fmt_time

d = pygame.draw

BIG = 64
MID = 36
HEARTS_SHOWN = 5


def text(screen, message, pos, color=WHITE, size=MID, shadow=True):
    screen.blit(cache.text(size, message, color, shadow), pos)


def centered(screen, message, center, color=WHITE, size=MID, shadow=True):
    img = cache.text(size, message, color, shadow)
    screen.blit(img, img.get_rect(center=center))


def right(screen, message, topright, color=WHITE, size=MID):
    img = cache.text(size, message, color)
    screen.blit(img, img.get_rect(topright=topright))


def draw_hud(screen, state, frames, controls):
    """Marcador de dalt a l'esquerra: menjar, vides, bistecs i arma."""
    text(screen, f"Menjar: {state.score}", (15, 15))

    # vides
    shown = min(state.lives, HEARTS_SHOWN)
    for i in range(HEARTS_SHOWN):
        img = art.heart(i < shown)
        screen.blit(img, (15 + i * 34, 50))
    if state.lives > HEARTS_SHOWN:
        text(screen, f"+{state.lives - HEARTS_SHOWN}", (15 + HEARTS_SHOWN * 34 + 4, 52), GOLD)

    # bistecs cap a la propera vida
    screen.blit(art.steak(), (15, 86))
    text(screen, f"{state.steaks}/{STEAKS_PER_LIFE}", (54, 88))
    bar = pygame.Rect(15, 116, 120, 9)
    d.rect(screen, (0, 0, 0), bar, border_radius=5)
    full = int(118 * state.steaks / STEAKS_PER_LIFE)
    if full:
        d.rect(screen, (255, 150, 70), (16, 117, full, 7), border_radius=4)

    # arma
    weapons.draw_icon(screen, state.weapon, 32, 162, 30)
    text(screen, f"Arma: {weapons.name_of(state.weapon)}  (M)", (58, 152))

    # combo
    if state.combo_n > 0:
        mult = state.multiplier
        col = COMBO_COLORS[mult - 1]
        text(screen, f"Combo x{mult}", (15, 192), col, BIG)
        d.rect(screen, (0, 0, 0), (15, 232, 154, 12), border_radius=6)
        d.rect(screen, col, (17, 234, int(150 * state.combo_frac), 8), border_radius=4)

    if state.penalty_flash > 0:
        text(screen, "-1 punt (temps!)", (190, 15), (255, 90, 90))

    # amb els dits, a baix hi ha els botons: l'ajuda va a dalt a la dreta
    if controls.touch_ui:
        right(screen, controls.help_text(), (W - 15, 15))
    else:
        text(screen, controls.help_text(), (15, H - 35))


def draw_popups(screen, popups):
    for pu in popups:
        centered(screen, pu.label, (int(pu.x), int(pu.y)), COMBO_COLORS[pu.mult - 1])


def _panel(screen, height=440):
    """La caixa dels cartells, sempre al mig."""
    art.darken(screen, 110)
    r = pygame.Rect(0, 0, 560, height)
    r.center = (W // 2, H // 2)
    d.rect(screen, RED, r.inflate(12, 12), border_radius=22)
    d.rect(screen, BLUE, r, border_radius=18)
    d.rect(screen, RED, (r.x, r.y, r.w, 8), border_top_left_radius=18, border_top_right_radius=18)
    d.rect(screen, RED, (r.x, r.bottom - 8, r.w, 8),
           border_bottom_left_radius=18, border_bottom_right_radius=18)
    return r


def _top_box(screen, r, top, rank, title="Les 5 millors"):
    box = pygame.Rect(r.x + 40, r.y + 200, r.w - 80, 210)
    d.rect(screen, DBLUE, box, border_radius=12)
    d.rect(screen, RED, box, 4, border_radius=12)
    centered(screen, title, (box.centerx, box.y + 24), GOLD)
    for i, (nm, sc, tm) in enumerate(top):
        me = i == rank
        col = GOLD if me else WHITE
        y = box.y + 55 + i * 30
        if me:
            d.rect(screen, RED, (box.x + 12, y - 13, box.w - 24, 27), border_radius=8)
        text(screen, f"{i + 1}. {nm}", (box.x + 24, y - 10), col)
        img = cache.text(MID, f"{sc} punts", col)
        screen.blit(img, img.get_rect(topleft=(box.x + 200, y - 10)))
        img = cache.text(MID, fmt_time(tm), col)
        screen.blit(img, img.get_rect(topright=(box.right - 24, y - 10)))
    return box


def _name_box(screen, r, name, frames):
    box = pygame.Rect(r.x + 40, r.y + 200, r.w - 80, 210)
    d.rect(screen, DBLUE, box, border_radius=12)
    d.rect(screen, RED, box, 4, border_radius=12)
    centered(screen, "Escriu el teu nom:", (box.centerx, box.y + 45), GOLD)
    inp = pygame.Rect(box.x + 40, box.y + 80, box.w - 80, 50)
    d.rect(screen, WHITE, inp, border_radius=10)
    d.rect(screen, RED, inp, 3, border_radius=10)
    cur = "|" if (frames // 20) % 2 == 0 else ""
    centered(screen, name + cur, inp.center, DBLUE, BIG, shadow=False)
    centered(screen, "Després prem INTRO", (box.centerx, box.y + 170))


def draw_result(screen, result, frames, touch):
    """Cartell de final de nivell o de partida acabada."""
    r = _panel(screen)
    heading = "Has guanyat!!!" if result.won else "Fi del joc"
    centered(screen, heading, (r.centerx, r.y + 55), GOLD if result.won else (255, 140, 140), BIG)
    centered(screen, f"Puntuació: {result.score}", (r.centerx, r.y + 105), WHITE, BIG)
    if result.won:
        centered(screen, f"Punts {result.base}  +  Bonus rapidesa {result.bonus}",
                 (r.centerx, r.y + 145), GOLD)
        extra = f"  (inclou +{int(result.penalty)}s per cops)" if result.penalty else ""
        centered(screen, f"Temps: {fmt_time(result.secs)}{extra}", (r.centerx, r.y + 177))
    else:
        centered(screen, "T'has quedat sense vides!", (r.centerx, r.y + 145), (255, 180, 180))
        centered(screen, f"Temps: {fmt_time(result.secs)}", (r.centerx, r.y + 177))
    if result.name is not None:
        _name_box(screen, r, result.name, frames)
        return
    _top_box(screen, r, result.top, result.rank)
    again = "Toca la pantalla per tornar a jugar" if touch else "Prem INTRO per tornar a jugar"
    centered(screen, again, (r.centerx, r.bottom - 24))


def draw_rotate_hint(screen):
    """Al mobil en vertical: demana girar-lo."""
    art.darken(screen, 150)
    centered(screen, "Gira el mòbil!", (W // 2, H // 2 - 30), GOLD, BIG)
    centered(screen, "El joc es veu molt millor de costat", (W // 2, H // 2 + 20))


def draw_poofs(screen, poofs):
    """El nuvolet de fum quan un mamut desapareix."""
    for pf in poofs:
        k = pf.progress
        for i in range(6):
            a = i * 1.047 + k
            cx = pf.x + math.cos(a) * 40 * k
            cy = pf.y + math.sin(a) * 30 * k
            d.circle(screen, (245, 245, 245), (int(cx), int(cy)), int(18 * (1 - k)) + 3)
            art.draw_star(screen, (int(pf.x + math.cos(a + 0.5) * 55 * k),
                                   int(pf.y + math.sin(a + 0.5) * 45 * k)), 7, pf.color)
