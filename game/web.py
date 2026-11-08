"""Arreglos per al navegador.

La pagina que genera pygbag no diu `touch-action: none`, i per aixo al mobil
el navegador es queda els gestos (desplacar, fer zoom) i el joc no rep els
tocs. Ho adobem des d'aqui, sense dependre de la plantilla de pygbag.

Tot va dins de `try/except`: si alguna cosa no existeix, el joc tira igual.
"""

import sys

PAGE_FIX = """
(function () {
  var css = document.createElement('style');
  css.textContent = [
    'html, body { overscroll-behavior:none; touch-action:none;',
    '  -webkit-user-select:none; user-select:none;',
    '  -webkit-tap-highlight-color:transparent; }',
    'canvas { touch-action:none !important; }'
  ].join('');
  document.head.appendChild(css);

  var vp = document.querySelector('meta[name=viewport]');
  if (!vp) { vp = document.createElement('meta'); vp.name = 'viewport';
             document.head.appendChild(vp); }
  vp.setAttribute('content',
    'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no');

  // que un gest de pessigar no faci zoom per sobre del joc
  ['gesturestart', 'gesturechange', 'dblclick'].forEach(function (name) {
    document.addEventListener(name, function (e) { e.preventDefault(); },
                              { passive: false });
  });
  document.addEventListener('touchmove', function (e) {
    if (e.touches.length > 1) { e.preventDefault(); }
  }, { passive: false });
})();
"""


def on_web():
    return sys.platform == "emscripten"


def _window():
    if not on_web():
        return None
    try:
        import platform
        return platform.window
    except Exception:
        return None


def setup_page():
    """Diu al navegador que els tocs son del joc, no de la pagina."""
    win = _window()
    if win is None:
        return False
    try:
        win.eval(PAGE_FIX)
        return True
    except Exception:
        pass
    try:                                     # pla B, sense `eval`
        win.document.head.insertAdjacentHTML(
            "beforeend",
            "<style>html,body{overscroll-behavior:none;touch-action:none;"
            "user-select:none;-webkit-user-select:none}"
            "canvas{touch-action:none !important}</style>")
        return True
    except Exception:
        return False


def is_touch_device():
    """Hi ha pantalla tactil? Al mobil si, a l'ordinador normalment no."""
    win = _window()
    if win is None:
        return False
    try:
        if int(win.navigator.maxTouchPoints or 0) > 0:
            return True
    except Exception:
        pass
    try:
        return bool(win.matchMedia("(pointer: coarse)").matches)
    except Exception:
        return False
