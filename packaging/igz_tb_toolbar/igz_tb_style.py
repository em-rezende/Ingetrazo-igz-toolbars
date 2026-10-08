# =========================================================================
# Copyright (C) 2026 IngeTrazo Contributors / Ezequiel M. Rezende
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# =========================================================================
# Extension: igz_tb_style (Com suporte a ícones temáticos)
# Author: Ezequiel M. Rezende
# Version: 1.5.2
# Date: 2026-10-08
# License: GPL-3.0-or-later (same as IngeTrazo)
#
# IngeTrazo — "Styles" Toolbar
# Location: <plugins>/igz_tb_toolbar/igz_tb_style.py
#
# Mirrors the commands of the native Camera ▸ Style menu.
# Instead of reimplementing the logic, it locates the native QAction and
# calls trigger() — exactly what the user would do by clicking.
# =========================================================================
from __future__ import annotations

import os
import sys
import traceback

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QPalette
from PySide6.QtWidgets import QToolBar, QMessageBox, QSizePolicy, QFrame

DEBUG = True

def _log(msg: str) -> None:
    if DEBUG:
        print(f"[igz_tb_style] {msg}", file=sys.stderr, flush=True)


# --- Internationalization --------------------------------------------------
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


# --- Themed icon helper ----------------------------------------------------
def _load_themed_icon(base_name: str, main_window) -> QIcon:
    """
    Verifica se o tema da interface é claro ou escuro através da paleta
    e carrega o ícone correspondente (_light.svg para temas claros).
    """
    if not _ICONS_DIR:
        return QIcon()

    is_dark = True
    try:
        if main_window is not None:
            palette = main_window.palette()
            bg_color = palette.color(QPalette.Window)
            is_dark = bg_color.lightness() < 128
    except Exception:
        pass

    if not is_dark:
        light_path = os.path.join(_ICONS_DIR, f"{base_name}_light.svg")
        if os.path.isfile(light_path):
            return QIcon(light_path)

    default_path = os.path.join(_ICONS_DIR, f"{base_name}.svg")
    if os.path.isfile(default_path):
        return QIcon(default_path)

    return QIcon()


# --- Map: English source label -> base icon name --------------------------
MENU_ACTIONS = [
    ("Default",         "tb_default"),
    ("Architectural",   "tb_architectural"),
    ("Shaded",          "tb_shaded"),
    ("Hidden line",     "tb_hiddenline"),
    ("Monochrome",      "tb_monochrome"),
    ("Wireframe",       "tb_wireframe"),
    ("X-ray",           "tb_xray"),
    # ─── separator #1 (before the display toggles) ───
    ("Toggle X-ray",    "tb_xraytoggle"),
    ("Edges",           "tb_edges"),
    ("Profiles",        "tb_profiles"),
    ("Back edges",      "tb_backedges"),
    # ─── separator #2 (before the visibility toggles) ───
    ("Hidden Objects",  "tb_hiddenobjects"),
    ("Hidden Geometry", "tb_hiddengeometry"),
]


# --- Finds and triggers the native QAction ---------------------------------
def _find_action(main_window, english: str):
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
_LABELED_ACTIONS: list = []
_TOOLBARS: list = []
_LAST_LANG = None
_LANG_TIMER = None


def _retranslate() -> None:
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
    global _LANG_TIMER, _LAST_LANG
    if _LANG_TIMER is not None:
        return
    _LAST_LANG = _it_language()
    timer = QTimer()
    timer.setInterval(1000)
    timer.timeout.connect(_poll_language)
    timer.start()
    _LANG_TIMER = timer


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
            f = QFrame(tb)
            f.setFrameShape(QFrame.VLine)
            f.setFrameShadow(QFrame.Plain)
            f.setFixedWidth(1)
            f.setContentsMargins(6, 4, 6, 4)
            f.setStyleSheet(
                "QFrame { background-color: rgba(160, 160, 160, 0.9); "
                "border: none; }"
            )
            tb.addWidget(f)

        for i, (english, base_name) in enumerate(MENU_ACTIONS):
            if i in (7, 11):
                _add_separator()

            icon = _load_themed_icon(base_name, main_window)

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