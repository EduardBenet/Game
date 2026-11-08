"""Les 5 millors puntuacions.

A l'ordinador es guarden en un fitxer. Al navegador el sistema de fitxers es
de mentida i es perd en recarregar, aixi que fem servir el `localStorage` de
la pagina. Si res funciona, el joc tira igual amb la llista buida.
"""

import json
import os
import sys

TOP_N = 5
STORAGE_KEY = "cavernicola.highscores"
FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "highscores.json")


def on_web():
    return sys.platform == "emscripten"


def _read_text():
    if on_web():
        try:
            import platform
            return platform.window.localStorage.getItem(STORAGE_KEY)
        except Exception:
            return None
    try:
        with open(FILE, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def _write_text(text):
    if on_web():
        try:
            import platform
            platform.window.localStorage.setItem(STORAGE_KEY, text)
        except Exception:
            pass
        return
    try:
        with open(FILE, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception:
        pass


def load():
    """Llista de (nom, punts, segons), de la millor a la pitjor."""
    raw = _read_text()
    if not raw:
        return []
    try:
        rows = json.loads(raw)
        return [(str(e.get("name", "???")), int(e["score"]), float(e["time"]))
                for e in rows][:TOP_N]
    except Exception:
        return []


def save(name, score, secs):
    """Guarda i es queda amb les 5 millors. Torna la posicio (0-4) o -1."""
    entry = (name, score, round(secs, 1))
    rows = sorted(load() + [entry], key=lambda e: (-e[1], e[2]))[:TOP_N]
    _write_text(json.dumps([{"name": n, "score": a, "time": b} for n, a, b in rows]))
    return rows.index(entry) if entry in rows else -1


def would_enter(score, secs):
    """Aquesta puntuacio entraria a les 5 millors?"""
    entry = ("", score, round(secs, 1))
    rows = sorted(load() + [entry], key=lambda e: (-e[1], e[2]))
    return entry in rows[:TOP_N]


def reset():
    _write_text("[]")


def fmt_time(secs):
    return f"{int(secs) // 60}:{int(secs) % 60:02d}"
