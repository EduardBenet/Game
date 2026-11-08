"""Arrencada i bucle principal.

La simulacio va a pas fix (`FPS` passos per segon) i el dibuix va tan rapid
com pugui la maquina. Aixi el joc es mou igual a l'ordinador i al mobil, i al
navegador no es queda esperant mai.
"""

import asyncio
import sys
import pygame

from . import controls as controls_mod, hud, stage as stage_mod, web
from .config import W, H, FPS

STEP = 1.0 / FPS
MAX_CATCH_UP = 3          # passos maxims per fotograma si la maquina va justa
TEST_FRAMES = 150


on_web = web.on_web


def open_window():
    """Pantalla del joc. Al navegador la pagina ja fa de finestra."""
    flags = pygame.SCALED | pygame.RESIZABLE
    if not on_web():
        try:
            return pygame.display.set_mode((W, H), pygame.SCALED | pygame.FULLSCREEN)
        except pygame.error:
            pass
    return pygame.display.set_mode((W, H), flags)


def portrait():
    """El mobil esta de dret? Si no es pot saber, fem com si no."""
    try:
        win_w, win_h = pygame.display.get_window_size()
    except Exception:
        return False
    return win_h > win_w * 1.15


class App:
    def __init__(self, test=False, force_touch=False):
        self.test = test
        pygame.init()
        self.screen = open_window()
        if on_web():
            web.setup_page()          # al navegador, els tocs son del joc
        pygame.display.set_caption("Cavernícola")
        if not on_web():
            pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        touch = force_touch or (on_web() and web.is_touch_device())
        self.controls = controls_mod.Controls(force_touch=touch)
        self.stage = stage_mod.Stage()
        self.running = True
        self.frames = 0
        self._acc = 0.0
        self._portrait = False
        self._last = pygame.time.get_ticks() / 1000.0

    # ------------------------------------------------------------- events ---
    def pump(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False
                elif self.stage.handle_key(e) == "again":
                    self.restart()
            else:
                self.controls.handle(e)

    def restart(self):
        self.stage = stage_mod.Stage()

    # --------------------------------------------------------------- bucle --
    def steps_due(self):
        """Quants passos de simulacio toquen ara."""
        if self.test:
            return 1
        now = pygame.time.get_ticks() / 1000.0
        self._acc += min(now - self._last, 0.25)
        self._last = now
        steps = 0
        while self._acc >= STEP and steps < MAX_CATCH_UP:
            self._acc -= STEP
            steps += 1
        return steps

    def tick(self):
        self.controls.begin_frame()
        self.pump()
        if not self.running:
            return
        if self.stage.handle_touch(self.controls) == "again":
            self.restart()
        for _ in range(self.steps_due()):
            self.stage.update(self.controls)
        self.stage.draw(self.screen, self.controls)
        if self.controls.touch_ui:
            if self.frames % 15 == 0:
                self._portrait = portrait()
            if self._portrait:
                hud.draw_rotate_hint(self.screen)
        pygame.display.flip()
        self.frames += 1

    async def run(self):
        while self.running:
            self.tick()
            self.clock.tick(60)          # cedeix el control a la pagina
            await asyncio.sleep(0)       # imprescindible per al navegador
            if self.test and self.frames >= TEST_FRAMES:
                break
        pygame.quit()


async def run_app(argv=None):
    """Arrenca el joc. Si peta, ho ensenya a la pantalla i a la consola en
    comptes de deixar la pagina en gris."""
    argv = sys.argv if argv is None else argv
    try:
        app = App(test="--test" in argv, force_touch="--touch" in argv)
        await app.run()
    except Exception:
        import traceback
        report = traceback.format_exc()
        print(report)                     # va a la consola del navegador
        if "--test" in argv:
            raise
        await show_error(report)


async def show_error(report):
    """Pantalla d'error llegible (val mes que un rectangle gris)."""
    try:
        screen = pygame.display.get_surface() or pygame.display.set_mode((W, H))
        font = pygame.font.Font(None, 24)
        lines = report.strip().splitlines()[-18:]
        for _ in range(600):
            screen.fill((25, 20, 40))
            title = pygame.font.Font(None, 44).render("Ep! El joc no ha pogut arrencar",
                                                      True, (255, 120, 120))
            screen.blit(title, (20, 20))
            for i, line in enumerate(lines):
                screen.blit(font.render(line[:120], True, (230, 230, 230)), (20, 70 + i * 26))
            pygame.display.flip()
            await asyncio.sleep(0.1)
    except Exception:
        pass
