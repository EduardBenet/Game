"""Memoria de dibuixos ja fets.

Al navegador cada crida a `pygame.draw` es cara. La regla del projecte es:
dibuixa una vegada, guarda-ho en una `Surface`, i despres nomes fes `blit`.
Tot el modul `art` passa per aqui.
"""

import pygame

_surfaces = {}
_texts = {}
_fonts = {}
_rotations = {}


def sprite(key, factory):
    """Torna la Surface de `key`, creant-la amb `factory()` nomes el primer cop."""
    surf = _surfaces.get(key)
    if surf is None:
        surf = _surfaces[key] = factory()
    return surf


def new_surface(size):
    return pygame.Surface(size, pygame.SRCALPHA)


def font(size):
    f = _fonts.get(size)
    if f is None:
        f = _fonts[size] = pygame.font.Font(None, size)
    return f


SHADOW = (25, 25, 35)


def text(size, message, color, shadow=True):
    """Text ja renderitzat, amb una ombra fosca a sota perque es llegeixi
    sobre el cel i sobre els nuvols. El HUD en demana el mateix cada
    fotograma, aixi que es fa un sol cop."""
    key = (size, message, color, shadow)
    surf = _texts.get(key)
    if surf is None:
        front = font(size).render(message, True, color)
        if shadow:
            back = font(size).render(message, True, SHADOW)
            w, h = front.get_size()
            surf = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
            surf.blit(back, (2, 2))
            surf.blit(front, (0, 0))
        else:
            surf = front
        if len(_texts) > 600:          # xarxa de seguretat: text amb numeros canviants
            _texts.clear()
        _texts[key] = surf
    return surf


def rotations(key, factory, steps=24):
    """Taula de `steps` girs ja fets. Evita `transform.rotate` cada fotograma."""
    table = _rotations.get(key)
    if table is None:
        base = sprite(key, factory)
        table = _rotations[key] = [pygame.transform.rotate(base, i * 360.0 / steps) for i in range(steps)]
    return table


def rotated(key, factory, degrees, steps=24):
    table = rotations(key, factory, steps)
    return table[int(round(degrees / (360.0 / steps))) % steps]


def steps_of(key, count, factory):
    """Llista de `count` variants d'una animacio (factory(i) -> Surface)."""
    table = _surfaces.get(key)
    if table is None:
        table = _surfaces[key] = [factory(i) for i in range(count)]
    return table


def pick(table, phase):
    return table[int(phase) % len(table)]


def clear():
    """Nomes per a proves: buida tota la memoria de dibuixos."""
    _surfaces.clear()
    _texts.clear()
    _rotations.clear()

