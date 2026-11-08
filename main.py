"""Cavernicola. Punt d'entrada: `./run.sh` o `python main.py`.

Opcions: `--test` (unes passades sense pantalla, per comprovar que va)
         `--touch` (ensenya els botons del mobil a l'ordinador)
"""

import asyncio

from game.app import main

if __name__ == "__main__":
    asyncio.run(main())
