# Cavernícola 🦣

Joc de plataformes fet amb pygame. Juga-hi al navegador:
https://eduardbenet.github.io/Game/

## Com es juga

Atrapa fruites, fes fora els mamuts i busca el **67 daurat**: quan l'agafis, nivell acabat.

- Comences amb **3 vides** ❤️❤️❤️. Si un mamut et toca, perds una vida.
- Cada mamut que fas fora et dona un **bistec** 🥩. Amb **10 bistecs** guanyes una vida.
- Sense vides, fi del joc.
- Els mamuts **no s'acaben mai**, i com més estona passa, més n'hi ha.
- El **67** és molt rar: surt de tant en tant, es queda una mica i marxa. Si el pesques, guanyes.

## Controls

**Ordinador** · Fletxes (o A/D): moure · Espai: saltar (doble salt a l'aire) · M: usar l'arma · Esc: sortir

**Mòbil i tauleta** · Botons a la pantalla: `<` `>` per moure, `^` per saltar, `M` per l'arma.
Millor amb el mòbil de costat (el joc t'ho recorda si el tens dret).

## Jugar en local

    ./run.sh

La primera vegada, crea l'entorn:

    python -m venv venv
    ./venv/bin/pip install pygame-ce      # a Windows: ./venv/Scripts/pip install pygame-ce

Comprovació ràpida sense pantalla (unes passades i surt):

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy ./run.sh --test

Per veure els botons del mòbil a l'ordinador: `./run.sh --touch`

## Web

Cada `push` a `main` comprova que el joc arrenca, el construeix amb
[pygbag](https://github.com/pygame-web/pygbag) i el publica a GitHub Pages
(vegeu `.github/workflows/deploy.yml`).

## Com està organitzat el codi

`main.py` només arrenca el joc. Tot és dins de `game/`:

| fitxer | de què s'encarrega |
| --- | --- |
| `config.py` | tots els números d'ajust (mida, gravetat, vides, bistecs, el 67) |
| `cache.py` | memòria de dibuixos ja fets — la clau de la velocitat |
| `art.py` | com es dibuixa cada cosa, una sola vegada |
| `level.py` | el catàleg de nivells (`LEVELS`) i les plataformes |
| `entities.py` | fruites, el 67, mamuts i el cavernícola |
| `weapons.py` | el catàleg d'armes (`WEAPONS`) i els projectils |
| `scenery.py` | cel, núvols, terra i clima |
| `controls.py` | teclat i botons del mòbil |
| `hud.py` | marcadors i cartells |
| `scores.py` | les 5 millors (fitxer a l'ordinador, `localStorage` al web) |
| `stage.py` | les regles del nivell |
| `app.py` | finestra i bucle principal |
| `web.py` | arreglos de la pàgina per al mòbil |

Per afegir coses noves n'hi ha prou amb una entrada més a una taula:
un **nivell** a `LEVELS` (`level.py`), una **arma** a `register(...)` (`weapons.py`),
un **enemic** heretant de `Hopper` (`entities.py`).
