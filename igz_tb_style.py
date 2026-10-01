# =========================================================================
# Extension: igz_tb_style
# Author: Ezequiel M. Rezende
# Version: 1.3.0
# Date: 2026-10-01
# License: GPL-3.0-or-later (same as IngeTrazo)
#
# IngeTrazo — "Styles" Toolbar
# Location: <plugins>/igz_tb_style.py
#
# Mirrors the commands of the native Camera ▸ Style menu.
# Instead of reimplementing the logic, it locates the native QAction and
# calls trigger() — exactly what the user would do by clicking.
#
# Internationalization: IngeTrazo ships a lightweight JSON catalog
# (core/i18n.py, English source strings). This toolbar reuses those same
# English sources, so its labels and the actions it triggers follow the
# IngeTrazo language (Window ▸ Language) instead of being hard-coded in
# one language. Strings of our own that are not in IngeTrazo's catalog
# fall back to the small local table below.
# =========================================================================
from __future__ import annotations

import os
import sys
import traceback

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QToolBar, QMessageBox, QSizePolicy, QFrame

DEBUG = True

def _log(msg: str) -> None:
    if DEBUG:
        print(f"[igz_tb_style] {msg}", file=sys.stderr, flush=True)


# --- Internationalization --------------------------------------------------
# IngeTrazo's JSON i18n (core/i18n.py): English is the source language and
# tr() looks a string up in the active catalog. The native menu entries we
# mirror use those exact English sources, so tr() returns whatever the
# Camera ▸ Style menu currently shows — in any of the shipped languages.
# older IngeTrazo without core.i18n: each name falls back on its own, so a
# missing helper never disables the ones that do exist.
try:
    from core.i18n import tr as _it_tr
except Exception:
    def _it_tr(text, **kwargs):
        return text

try:
    from core.i18n import current_language as _it_language
except Exception:
    def _it_language():
        return "en"

try:
    from core.i18n import source_of as _it_source
except Exception:
    def _it_source(text):
        return text


# Our own strings live only in this plugin, so IngeTrazo's catalog does not
# carry them; translate them here (English — the source — needs no entry).
_LOCAL = {
    "es": {
        "Could not locate the main window.":
            "No se pudo localizar la ventana principal.",
    },
    "id": {
        "Could not locate the main window.":
            "Tidak dapat menemukan jendela utama.",
    },
    "it": {
        "Could not locate the main window.":
            "Impossibile trovare la finestra principale.",
    },
    "pt-BR": {
        "Could not locate the main window.":
            "Não foi possível localizar a janela principal.",
    },
}


def _t(text: str) -> str:
    """`text` (an English source string) in the active IngeTrazo language."""
    out = _it_tr(text)
    if out != text:
        return out
    return _LOCAL.get(_it_language(), {}).get(text, text)


# --- Locating the icons folder --------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))

def _find_icons_folder():
    c = os.path.join(_HERE, "icons")
    return c if os.path.isdir(c) else None

_ICONS_DIR = _find_icons_folder()


# --- MainWindow discovery --------------------------------------------------
def _discover_main_window():
    try:
        from PySide6.QtWidgets import QApplication
        qapp = QApplication.instance()
        if qapp is None:
            return None
        for w in qapp.topLevelWidgets():
            if type(w).__name__ == "MainWindow":
                return w
        for w in qapp.topLevelWidgets():
            if hasattr(w, "addToolBar"):
                return w
    except Exception:
        traceback.print_exc()
    return None


# --- Map: English source label -> icon file -------------------------------
# The labels are IngeTrazo's SOURCE (English) strings — the same keys its
# own Camera ▸ Style menu hands to tr(). Matching by source keeps the
# toolbar working in every language: the menu shows a translation, and we
# still find the action behind it.
# Order identical to the native Camera ▸ Style menu.
MENU_ACTIONS = [
    ("Default",         "tb_default.svg"),
    ("Architectural",   "tb_architectural.svg"),
    ("Shaded",          "tb_shaded.svg"),
    ("Hidden line",     "tb_hiddenline.svg"),
    ("Monochrome",      "tb_monochrome.svg"),
    ("Wireframe",       "tb_wireframe.svg"),
    ("X-ray",           "tb_xray.svg"),
    # ─── separator #1 (before the display toggles) ───
    ("Toggle X-ray",    "tb_xraytoggle.svg"),
    ("Edges",           "tb_edges.svg"),
    ("Profiles",        "tb_profiles.svg"),
    ("Back edges",      "tb_backedges.svg"),
    # ─── separator #2 (before the visibility toggles) ───
    ("Hidden Objects",  "tb_hiddenobjects.svg"),
    ("Hidden Geometry", "tb_hiddengeometry.svg"),
]


# --- Finds and triggers the native QAction ---------------------------------
# Our own actions (kept in _LABELED_ACTIONS) are skipped so a click can
# never re-trigger ourselves.
def _find_action(main_window, english: str):
    """The native QAction labelled `english`, in whatever UI language."""
    own = {id(a) for a, _ in _LABELED_ACTIONS}
    roots = []
    menubar = getattr(main_window, "menuBar", None)
    if callable(menubar):
        bar = menubar()
        if bar is not None:
            roots.append(bar)
    roots.append(main_window)
    for root in roots:
        for a in root.findChildren(QAction):
            if id(a) in own:
                continue
            text = a.text()
            if text == english or _it_source(text) == english or text == _t(english):
                return a
    return None


def _trigger_action(main_window, english: str) -> bool:
    """
    Finds the native QAction for the English source label and calls
    trigger() — exactly as the native menu would.
    """
    try:
        a = _find_action(main_window, english)
        if a is not None:
            a.trigger()
            _log(f"trigger: '{english}'")
            return True
        _log(f"QAction '{english}' not found in the menu")
        return False
    except Exception:
        traceback.print_exc()
        return False



# --- Following the app language --------------------------------------------
_LABELED_ACTIONS: list = []      # [(QAction, english source), ...]
_TOOLBARS: list = []             # [QToolBar, ...]
_LAST_LANG = None
_LANG_TIMER = None


def _retranslate() -> None:
    """Re-apply the active language to every label this plugin owns."""
    title = _t("Styles")
    for tb in _TOOLBARS:
        tb.setWindowTitle(title)
    for action, english in _LABELED_ACTIONS:
        label = _t(english)
        action.setText(label)
        action.setToolTip(label)
        action.setStatusTip(label)


def _poll_language() -> None:
    global _LAST_LANG
    code = _it_language()
    if code != _LAST_LANG:
        _LAST_LANG = code
        _retranslate()
        _log(f"language changed -> {code}")


def _install_language_watcher() -> None:
    """Follow Window ▸ Language.

    IngeTrazo applies a new language on the next start, but it also swaps
    the active catalog at once; this cheap timer keeps our toolbar in step
    without touching the rest of the UI.
    """
    global _LANG_TIMER, _LAST_LANG
    if _LANG_TIMER is not None:
        return
    _LAST_LANG = _it_language()
    timer = QTimer()
    timer.setInterval(1000)
    timer.timeout.connect(_poll_language)
    timer.start()
    _LANG_TIMER = timer      # module-level ref keeps the QTimer alive


# --- Toolbar creation ------------------------------------------------------
_TOOLBAR_CREATED = False

def _create_style_toolbar(main_window) -> None:
    global _TOOLBAR_CREATED
    if _TOOLBAR_CREATED:
        return
    if main_window is None or not hasattr(main_window, "addToolBar"):
        _log("MainWindow unavailable")
        return

    try:
        tb = QToolBar(_t("Styles"), main_window)
        tb.setObjectName("igz_tb_style")
        tb.setWindowTitle(_t("Styles"))
        main_window.addToolBar(Qt.TopToolBarArea, tb)
        _TOOLBARS.append(tb)

        def _add_separator():
            """Vertical line with a forced color — visible on the dark background."""
            f = QFrame(tb)
            f.setFrameShape(QFrame.VLine)
            f.setFrameShadow(QFrame.Plain)          # ← Plain, not Sunken
            f.setFixedWidth(1)
            f.setContentsMargins(6, 4, 6, 4)
            f.setStyleSheet(
                "QFrame { background-color: rgba(160, 160, 160, 0.9); "
                "border: none; }"
            )
            tb.addWidget(f)

        for i, (english, filename) in enumerate(MENU_ACTIONS):
            # Separator #1 — before the display toggles (index 7)
            # Separator #2 — before the visibility toggles (index 11)
            if i in (7, 11):
                _add_separator()

            icon = QIcon()
            if _ICONS_DIR:
                p = os.path.join(_ICONS_DIR, filename)
                if os.path.isfile(p):
                    icon = QIcon(p)

            label = _t(english)
            a = QAction(icon, label, main_window)
            a.setToolTip(label)
            a.setStatusTip(label)
            a.triggered.connect(
                lambda _=False, e=english:
                    _trigger_action(main_window, e)
            )
            tb.addAction(a)
            _LABELED_ACTIONS.append((a, english))

        # Make the docked toolbar respect the content size.
        # No +40 margin — the sizeHint already includes the separator.
        tb.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        tb.setMaximumWidth(tb.sizeHint().width())

        _TOOLBAR_CREATED = True
        _install_language_watcher()
        _log("'Styles' toolbar created (mirroring the native menu)")
    except Exception:
        traceback.print_exc()


# --- setup() ---------------------------------------------------------------
def setup(app):
    print(f"[igz_tb_style] setup(app) — PID={os.getpid()}",
          file=sys.stderr, flush=True)
    try:
        mw = _discover_main_window() \
             or getattr(app, "main_window", None) \
             or getattr(app, "window", None)
        if mw is None:
            QMessageBox.warning(
                None, _t("Styles"),
                _t("Could not locate the main window.")
            )
            return
        _create_style_toolbar(mw)
    except Exception:
        traceback.print_exc()

