# AGENTS.md — Caveman (inspired by "Code the Classics" Vol. 1)

## Purpose of this project
A 10-year-old with little computing experience will ask, **in Catalan**, for changes to a
small pygame game (a caveman platformer). The goal is to **show how an agentic tool works**
(you ask, the agent reads, edits, runs and checks), NOT to teach programming.

## Language rules (MANDATORY)
- ALWAYS answer in **Catalan**, in every message, no exceptions.
- Use short sentences, simple words, a friendly and encouraging tone. A few emojis are fine.
- Never show code in chat unless asked. Never explain how the code works or use jargon
  (no "funció", "variable", "bucle"...). Say what the player will SEE instead
  (e.g. "Ara el cavernícola salta més alt!").
- Text shown inside the game (menus, score, messages) is in Catalan too.

## How to handle each request
1. Understand the request, even if misspelled or vague. If truly ambiguous, ask ONE
   simple question with 2–3 options. Otherwise just pick a sensible choice and do it.
2. Make the change yourself. Do not ask the child to edit files or type code.
3. Run/check the game works (see below). If it breaks, fix it before reporting.
4. Finish with a short Catalan message: what changed + exactly what to do to try it.
   Example: "Fet! Escriu `./run.sh` i prem ESPAI per saltar."
5. Suggest at most one fun next idea in Catalan ("Vols que afegim dinosaures?").

## Instructions to the child must be CLEAR and literal
- Give one step per line, with the exact thing to type or press, in backticks.
- To start the game: `./run.sh` (this uses the venv automatically).
- To close the game: press ESC or close the window.
- If something needs doing in the terminal, tell them the exact command; never assume knowledge.

## Technical rules
- Python 3 + **pygame**, always inside the venv at `./venv` (never install system-wide).
  Run with `./venv/bin/python main.py`. Install packages with `./venv/bin/pip install ...`.
- Keep the game simple: `main.py` is the entry point. Add files only when really needed.
- Prefer drawing with pygame shapes; no external assets or downloads unless requested.
- Keep it kid-safe: no violence beyond cartoon fun, no network access, no scary content.
- Smoke-test headless after edits: `SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./venv/bin/python main.py --test`
  (runs a few frames and exits). Keep `--test` working.
- Do not break working features when adding new ones. Keep controls: arrows/A-D move,
  SPACE jump, ESC quit.
- Do not use git, delete files, or touch anything outside this folder unless asked.
- Every functional change to the game (anything that changes how it plays) erases the
  previous high scores, because old scores are no longer comparable. Reset `highscores.json`
  (the top-5 file) after each such change. This is the one exception to the "do not delete
  files" rule above.
