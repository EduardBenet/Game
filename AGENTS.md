# AGENTS.md — Caveman (inspired by "Code the Classics" Vol. 1)

## Purpose of this project
A 10-year-old with little computing experience will ask, **in Catalan**, for changes to a
small pygame game (a caveman platformer). The goal is to **show how an agentic tool works**
(you ask, the agent reads, edits, runs and checks), NOT to teach programming.

## Who are you talking to? (MANDATORY — pick the mode from the language used)

**The language of the request selects the mode. Never mix modes in one answer.**

### Catalan request → CHILD MODE (the default)
- Answer in **Catalan**, always, for the whole message.
- Use short sentences, simple words, a friendly and encouraging tone. A few emojis are fine.
- Never show code in chat unless asked. Never explain how the code works or use jargon
  (no "funció", "variable", "bucle"...). Say what the player will SEE instead
  (e.g. "Ara el cavernícola salta més alt!").
- Never mention refactors, architecture, data tables, the web build or any technical
  housekeeping. That work still happens (see Architecture below) — it just stays invisible.

### English request → DEVELOPER MODE
- Assume the person is an **experienced coder** (they own this repo). Answer in **English**.
- Talk like a peer reviewer: name the files and line numbers, show the diff or snippet that
  matters, and say what trade-off you took.
- Proactively discuss **coding best practices** to keep the game sharp: data-driven design,
  separation of simulation from rendering, fixed-timestep updates, avoiding per-frame
  allocations and per-frame `Surface`/font creation, caching pre-rendered art, keeping the
  hot loop O(entities) instead of O(entities²), dead-code removal, naming.
- Flag technical debt and performance risks you notice even if not asked, with a concrete
  suggested fix and its cost. Recommend; do not silently rewrite half the game.
- Switch back to Child Mode the moment the next request arrives in Catalan.

### Always, in both modes
- Text shown inside the game (menus, score, messages) is in **Catalan**.

## How to handle each request
1. Understand the request, even if misspelled or vague. If truly ambiguous, ask ONE
   simple question with 2–3 options. Otherwise just pick a sensible choice and do it.
2. Make the change yourself. Do not ask the child to edit files or type code.
3. Run/check the game works (see below). If it breaks, fix it before reporting.
4. In Child Mode, finish with a short Catalan message: what changed + exactly what to do to
   try it. Example: "Fet! Escriu `./run.sh` i prem ESPAI per saltar."
   In Developer Mode, finish with what changed, what you verified, and what you did not.
5. In Child Mode only, suggest at most one fun next idea in Catalan
   ("Vols que afegim dinosaures?").

## Instructions to the child must be CLEAR and literal
- Give one step per line, with the exact thing to type or press, in backticks.
- To start the game: `./run.sh` (this uses the venv automatically).
- To close the game: press ESC or close the window.
- If something needs doing in the terminal, tell them the exact command; never assume knowledge.

## The game must run well on the web (MANDATORY)
The game is published as a **static site** (GitHub Pages) built with **pygbag**
(`.github/workflows/deploy.yml` → https://eduardbenet.github.io/Game/). The browser build is
a first-class target, not an afterthought: a change that only works locally is **not done**.

### But the PC version is king (MANDATORY)
**Never change the game's architecture, structure or design just to suit the web build.**
The desktop game is the real game; the web build is how other people get to play it. If the
browser needs something, it gets it in a way that leaves the PC game untouched:
- Build settings (`deploy.yml`, pygbag flags) — fine, that is not the game.
- An additive, isolated web-only module (`game/web.py`) guarded by
  `sys.platform == "emscripten"` and wrapped in `try/except` — fine.
- A different code structure, renamed modules or packages, a worse abstraction, removed
  features, or reduced quality/detail because pygbag or a browser would prefer it — **no**.
If the only way to satisfy the browser is to compromise the desktop game, don't: keep the PC
version as it is, say plainly what the web limitation is, and leave the choice to the user.
Performance work is the exception that proves the rule: making the renderer cheaper helps
both, so it is welcome — as long as the desktop game looks and plays exactly the same.

- Keep the loop async-friendly: every frame must `await asyncio.sleep(0)`. Never block — no
  `time.sleep`, no synchronous network or file waits, no long loops between frames.
- Budget for the browser, which is slower than the desktop: target a stable **45 FPS**
  with the current `W, H = 1000, 600`. Pre-render anything static (text, art, gradients)
  into a cached `Surface` instead of redrawing it with primitives every frame.
- Keep the download small. No new large assets; generated/procedural art is preferred. If
  images are added, keep the whole bundle to a few MB and load them once at startup.
- **`main.py` has two shapes pygbag requires. Do not "tidy" them away:** `import pygame`
  at the top (pygbag scans the entry point's imports to decide which wheels to download —
  without it the page loads the archive, never fetches pygame, and sits on a grey screen),
  and `async def main()` defined in that file. Both look redundant on desktop. They are not.
- **Test the browser build before claiming it works.** Headless Edge/Chrome + `puppeteer-core`
  against `python -m pygbag --port 8000 .` reproduces the real thing: check the canvas is
  `1000x600` and not `1x1` (1x1 == the grey screen), and read the console. Always run the
  previous working commit through the same harness first — without a passing baseline you
  cannot tell your bug from the harness's.
- Guard anything the browser cannot do with `sys.platform == "emscripten"` (already done for
  `display.set_mode`). Note that **file writes do not persist in the browser**: the
  `highscores.json` top-5 survives locally but is lost on reload on the web — keep the write
  wrapped in `try/except` so it can never crash the web build.
- Input must work without a keyboard-only assumption where cheap to support; never rely on the
  mouse cursor (it is hidden) or on a real filesystem.
- Before saying a change is done, check both: the headless smoke test, and that nothing new
  violates the rules above. In Developer Mode, say explicitly if you could not verify the web
  build.

## Technical rules
- Python 3 + **pygame**, always inside the venv at `./venv` (never install system-wide).
  Run with `./venv/bin/python main.py`. Install packages with `./venv/bin/pip install ...`.
- Keep the gameplay simple for a 10-year-old; keep the *code* extensible (see Architecture).
  `main.py` stays the entry point. Add a module when it removes real coupling, not per feature.
- Prefer drawing with pygame shapes; no external assets or downloads unless requested.
- Keep it kid-safe: no violence beyond cartoon fun, no network access, no scary content.
- Smoke-test headless after edits: `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python main.py --test`
  (runs a few frames and exits). Keep `--test` working.
- Do not break working features when adding new ones. Keep controls: arrows/A-D move,
  UP arrow jump, Z attack, ESC quit.
- Do not use git, delete files, or touch anything outside this folder unless asked.
- Every functional change to the game (anything that changes how it plays) erases the
  previous high scores, because old scores are no longer comparable. Reset `highscores.json`
  (the top-5 file) after each such change. This is the one exception to the "do not delete
  files" rule above.
- `elements.csv` lists every visual element of the game (columns: `id`, `categoria`, `nom`,
  `mida_px`, `fons_transparent`, `descripcio`, `prompt_imatge`, `fitxer`, `estat`) with an image
  prompt for each one, so they can be generated as real pictures later. Every time an element is
  added, removed or changed (new enemy, weapon, fruit, scenery, effect...), update the CSV in the
  same change. Keep the common style prefix in `prompt_imatge` so all images look made by the same
  artist. `estat` is `pendent` until the image exists and is used by the game.

## Architecture: build for growth (MANDATORY, and invisible to the child)
From now on, every change should leave the code **easier to extend** — adding a level, a
monster, a weapon, a fruit or an effect should mean adding **data**, not editing the game loop.
Do this quietly: in Child Mode never mention it, just deliver the feature they asked for.

- **Data-driven first.** Define content in tables/dicts at module top (like the existing
  `WEAPONS` list) and drive behaviour from them. Adding a monster = one new entry plus its
  draw function; it must not require touching collision, scoring or the main loop.
- **One registry per content type**: levels, enemies, weapons, pickups. Each entry carries its
  own stats and the name of its drawing routine. Look things up in the registry; never
  `if kind == "..."` chains scattered through the loop — collapse those into a dispatch table
  as you touch them.
- **Levels as data.** Platform layouts, spawn counts and weather belong in a level table, not
  hardcoded inside `run_game`. A new level should be a new entry.
- **Separate simulation from drawing.** Update state, then draw it. Draw functions take state
  and must not mutate it.
- **Refactor opportunistically, never in one big bang.** When a feature touches a hardcoded
  area, generalise *that* area in the same change and keep the game playable at every step.
  Do not start a repo-wide rewrite unless asked in Developer Mode.
- The split already happened. `main.py` is only the entry point; the game lives in
  `game/`: `config` (every tuning number) · `cache` (pre-drawn surfaces) · `art` (how each
  thing is drawn, once) · `level` (the `LEVELS` table + `Platform`) · `entities`
  (`Hopper` → `Fruit`/`Gold67`/`Mammoth`, plus `Player`) · `weapons` (the `WEAPONS`
  registry + `Projectile` classes) · `scenery` · `controls` · `hud` · `scores` ·
  `stage` (the rules) · `app` (window + loop) · `web` (browser page fixes).
  Keep `main.py` as the entry point, keep `./run.sh` and `--test` working, and make sure
  pygbag still builds afterwards.
- **Where a change goes**: a new level → one entry in `LEVELS`. A new weapon → one
  `Projectile` subclass + one `register(...)` line. A new enemy → a `Hopper` subclass.
  A new number to tweak → `config.py`, never a literal in the loop. If a feature cannot be
  added that way, generalise the area first, then add it.
- **Never draw with primitives inside the frame loop** when the result is the same every
  time: build it once in `art.py` through `cache`, then `blit`. Full-screen tints go
  through `art.darken`/`art.tint` (a blended `fill`), never a per-pixel-alpha Surface —
  measured ~10x faster. Measure before and after; do not guess which way is cheaper.
- Keep `elements.csv` in sync: it is already the content catalogue, so a new registry entry and
  a new CSV row go together in the same change.

