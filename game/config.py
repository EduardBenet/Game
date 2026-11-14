"""Totes les constants del joc en un sol lloc.

Si vols canviar com se sent el joc, canvia-ho aqui: cap altre modul porta numeros
d'ajust a dins.
"""

# --- pantalla -------------------------------------------------------------
W, H = 1000, 600
FPS = 45                     # passos de simulacio per segon (ritme fix)
GROUND = H - 60
HOLE_X0, HOLE_X1 = W // 2 - 70, W // 2 + 70

# --- fisica del jugador ---------------------------------------------------
GRAVITY = 0.6
JUMP_V = -13.0
MOVE_V = 5.0
AIR_JUMPS = 1                # salts extra a l'aire (doble salt)
HURT_FRAMES = 100            # invulnerabilitat despres d'un cop

# --- vides i bistecs ------------------------------------------------------
LIVES_START = 3
STEAKS_PER_LIFE = 10
LIVES_MAX = 9

# --- mamuts: no s'acaben mai, cada cop n'hi ha mes ------------------------
MAMMOTH_START = 1            # quants n'hi ha al comencar
MAMMOTH_EVERY = 18.0         # escala de temps: a X segons n'hi ha 1 mes, despres puja cada cop mes rapid
MAMMOTH_RAMP = 1.6           # >1 = cada cop mes rapid (1 = ritme constant)
MAMMOTH_MAX = 14
MAMMOTH_SPAWN_GAP = 1.6      # segons entre aparicions al principi
MAMMOTH_SPAWN_GAP_MIN = 0.5  # i al final (van sortint mes depressa)
MAMMOTH_GAP_SHRINK = 60.0    # segons fins arribar al minim

# --- el 67: molt rar, i et passa de nivell --------------------------------
GOLD_FIRST = (45.0, 75.0)    # quan pot sortir el primer 67 (segons)
GOLD_AGAIN = (40.0, 70.0)    # si marxa, quan torna
GOLD_DANCE = 2.0             # segons de ball del 67 abans del final
GOLD_STAY = 8.0              # quant es queda a la pantalla

# --- puntuacio ------------------------------------------------------------
COMBO_SECONDS = 3.0
COMBO_MAX = 5
POINTS_FRUIT = 1
POINTS_MAMMOTH = 5
POINTS_GOLD = 10
TIME_PENALTY_EVERY = 10.0    # cada X segons perds 1 punt
HIT_TIME_PENALTY = 5.0       # segons afegits al temps per cada cop rebut

PICKUP_LIFE = 7.0            # segons que dura una arma al terra

# --- colors ---------------------------------------------------------------
GRASS = (70, 150, 70)
DIRT = (110, 80, 50)
SKIN = (235, 190, 150)
FUR = (150, 100, 50)
WHITE = (255, 255, 255)
GOLD = (255, 225, 60)
RED = (200, 40, 40)
BLUE = (40, 80, 200)
DBLUE = (20, 45, 130)

COMBO_COLORS = [(255, 255, 255), (255, 235, 120), (255, 190, 60), (255, 130, 50), (255, 70, 70)]

# --- clima ----------------------------------------------------------------
WEATHERS = ["sol", "pluja", "nit", "neu"]
SKY_OF = {"sol": (120, 190, 235), "pluja": (105, 120, 145), "nit": (20, 25, 62), "neu": (185, 202, 220)}
CLOUD_OF = {"sol": (255, 255, 255), "pluja": (150, 155, 168), "nit": (70, 80, 115), "neu": (238, 242, 248)}
WEATHER_CHANGE = (25, 45)    # segons entre canvis de clima

CLOUDS = [(80, 70, 1.0, 0.25), (380, 120, 1.4, 0.15), (620, 55, 0.9, 0.3),
          (850, 150, 1.2, 0.2), (200, 190, 0.8, 0.18)]
