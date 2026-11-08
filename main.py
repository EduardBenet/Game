"""Cavernicola. Punt d'entrada: `./run.sh` o `python main.py`.

Opcions: `--test` (unes passades sense pantalla, per comprovar que va)
         `--touch` (ensenya els botons del mobil a l'ordinador)

`main` s'ha de definir AQUI mateix com a `async def`: pygbag busca
exactament aquesta forma al fitxer principal (abans tambe era aixi).
"""

import asyncio

from game import app


async def main():
    await app.run_app()


if __name__ == "__main__":
    asyncio.run(main())
