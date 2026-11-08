"""Cavernicola. Punt d'entrada: `./run.sh` o `python main.py`.

Opcions: `--test` (unes passades sense pantalla, per comprovar que va)
         `--touch` (ensenya els botons del mobil a l'ordinador)

Dues coses d'aquest fitxer son IMPRESCINDIBLES per al navegador, encara que
a l'ordinador sembli que no calguin. No les treguis:
  * `import pygame` aqui: pygbag mira els imports del fitxer principal per
    decidir quins paquets ha de baixar. Sense aquesta linia no baixa pygame i
    la pagina es queda en gris.
  * `main` definit aqui mateix com a `async def`.
"""

import asyncio

import pygame  # noqa: F401  (el necessita pygbag, vegeu el comentari de dalt)

from game import app


async def main():
    await app.run_app()


if __name__ == "__main__":
    asyncio.run(main())
