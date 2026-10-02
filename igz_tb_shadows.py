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
# Extension: igz_tb_shadows (Com suporte a ícones temáticos)
# Author: Ezequiel M. Rezende
# Version: 1.2.0
# Date: 2026-10-01
# License: GPL-3.0-or-later (same as IngeTrazo)
#
# IngeTrazo — "Shadows" Toolbar
# Location: <plugins>/igz_tb_shadows.py
#
# ⚠️  FRAGILE API WARNING
# -------------------------------------------------------------------------
# IngeTrazo's `docs/plugins.md` states:
#     "The plugin API is not stable yet — expect breaking changes during
#      the 0.x series."
#
# This plugin uses points that are NOT documented as public extension API:
#
#   • viewport.scene.shadows          (scene via viewport, not app.scene)
#   • ShadowSettings.*                (fields: month/day/hour/minute/...)
#   • QToolBar created directly via PySide, without the `app.add_*` API
#
# All fragile points are marked with "⚠️ FRAGILE" below.
# The code is fault-tolerant: if `shadows` does not exist, it just
# logs and returns, without breaking IngeTrazo.
#
# Internationalization: the labels follow IngeTrazo's language through its
# JSON catalog (core/i18n.py, English source strings). The few strings that
# are ours alone carry a small local table below — same scheme as
# igz_tb_style.py.
# =========================================================================
from __future__ import annotations

import os
import sys
import traceback

from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QAction, QIcon, QPalette
from PySide6.QtWidgets import (
    QToolBar, QMessageBox, QSlider, QLabel, QWidget, QHBoxLayout, QSizePolicy
)

DEBUG = True

def _log(msg: str) -> None:
    if DEBUG:
        print(f"[igz_tb_shadows] {msg}", file=sys.stderr, flush=True)


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


#: Month abbreviations for the Date slider, per language.
_LOCAL_MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "es": ["ene", "feb", "mar", "abr", "may", "jun",
           "jul", "ago", "sep", "oct", "nov", "dic"],
    "id": ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
           "Jul", "Agu", "Sep", "Okt", "Nov", "Des"],
    "it": ["gen", "feb", "mar", "apr", "mag", "giu",
           "lug", "ago", "set", "ott", "nov", "dic"],
    "pt-BR": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
              "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
}

_LOCAL = {
    "es": {
        "Date": "Fecha",
        "Time": "Hora",
        "Int.": "Int.",
        "Toggle shadows on/off": "Activar/desactivar sombras",
        "Could not locate the IngeTrazo main window.":
            "No se pudo localizar la ventana principal de IngeTrazo.",
    },
    "id": {
        "Date": "Tanggal",
        "Time": "Waktu",
        "Int.": "Int.",
        "Toggle shadows on/off": "Nyalakan/matikan bayangan",
        "Could not locate the IngeTrazo main window.":
            "Tidak dapat menemukan jendela utama IngeTrazo.",
    },
    "it": {
        "Date": "Data",
        "Time": "Ora",
        "Int.": "Int.",
        "Toggle shadows on/off": "Attiva/disattiva ombre",
        "Could not locate the IngeTrazo main window.":
            "Impossibile trovare la finestra principale di IngeTrazo.",
    },
    "pt-BR": {
        "Date": "Data",
        "Time": "Hora",
        "Int.": "Int.",
        "Toggle shadows on/off": "Ligar/desligar sombras",
        "Could not locate the IngeTrazo main window.":
            "Não foi possível localizar a janela principal do IngeTrazo.",
    },
}


def _t(text: str) -> str:
    out = _it_tr(text)
    if out != text:
        return out
    return _LOCAL.get(_it_language(), {}).get(text, text)


def _months():
    return _LOCAL_MONTHS.get(_it_language(), _LOCAL_MONTHS["en"])


# --- Locating the icons folder --------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))


def _find_icons_folder():
    c = os.path.join(_HERE, "icons")
    return c if os.path.isdir(c) else None

_ICONS_DIR = _find_icons_folder()
_log(f"icons folder: {_ICONS_DIR}")


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


# --- Access to the scene and the viewport ----------------------------------
def _get_scene_shadows(main_window):
    vp = getattr(main_window, "viewport", None)
    if vp is None:
        return None
    scene = getattr(vp, "scene", None)
    if scene is None:
        return None
    return getattr(scene, "shadows", None)


def _repaint(main_window) -> None:
    vp = getattr(main_window, "viewport", None)
    if vp is not None and hasattr(vp, "update"):
        vp.update()


# --- Actions (only change scene.shadows + repaint) ------------------------
def _toggle_shadows(main_window, checked: bool) -> None:
    sh = _get_scene_shadows(main_window)
    if sh is None:
        return
    sh.enabled = bool(checked)
    _repaint(main_window)


def _change_date(main_window, day_of_year: int) -> None:
    sh = _get_scene_shadows(main_window)
    if sh is None:
        return
    d = QDate(2026, 1, 1).addDays(day_of_year - 1)
    sh.month = d.month()
    sh.day   = d.day()
    sh.enabled = True
    _repaint(main_window)


def _change_time(main_window, minutes: int) -> None:
    sh = _get_scene_shadows(main_window)
    if sh is None:
        return
    sh.hour   = minutes // 60
    sh.minute = minutes % 60
    sh.enabled = True
    _repaint(main_window)


def _change_intensity(main_window, value_0_100: int) -> None:
    sh = _get_scene_shadows(main_window)
    if sh is None:
        return
    sh.darkness = value_0_100 / 100.0
    _repaint(main_window)


# --- Dynamic labels --------------------------------------------------------
def _day_of_year_to_text(day_of_year: int) -> str:
    d = QDate(2026, 1, 1).addDays(day_of_year - 1)
    months = _months()
    return f"{d.day():02d} {months[d.month()-1]}"


def _minutes_to_text(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


# --- Finds the native "Shadows" QAction ------------------------------------
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



# --- Widgets ---------------------------------------------------------------
_LABEL_WIDGETS: list = []
_REFRESH_HOOKS: list = []


def _make_date_slider(main_window) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(4, 0, 4, 0)
    lay.setSpacing(6)

    caption = QLabel(_t("Date"))
    _LABEL_WIDGETS.append((caption, "Date"))

    lbl = QLabel()
    lbl.setMinimumWidth(60)
    lbl.setAlignment(Qt.AlignCenter)

    s = QSlider(Qt.Horizontal)
    s.setRange(1, 365)
    s.setFixedWidth(120)

    sh = _get_scene_shadows(main_window)
    if sh is not None:
        s.setValue(QDate(2026, sh.month, sh.day).dayOfYear())
    else:
        s.setValue(80)
    lbl.setText(_day_of_year_to_text(s.value()))

    def _on_change(v):
        lbl.setText(_day_of_year_to_text(v))
        _change_date(main_window, v)

    s.valueChanged.connect(_on_change)
    _REFRESH_HOOKS.append(lambda: lbl.setText(_day_of_year_to_text(s.value())))

    lay.addWidget(caption)
    lay.addWidget(s)
    lay.addWidget(lbl)
    return w


def _make_time_slider(main_window) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(4, 0, 4, 0)
    lay.setSpacing(6)

    caption = QLabel(_t("Time"))
    _LABEL_WIDGETS.append((caption, "Time"))

    lbl = QLabel()
    lbl.setMinimumWidth(50)
    lbl.setAlignment(Qt.AlignCenter)

    s = QSlider(Qt.Horizontal)
    s.setRange(0, 1439)
    s.setFixedWidth(120)

    sh = _get_scene_shadows(main_window)
    if sh is not None:
        s.setValue(sh.hour * 60 + sh.minute)
    else:
        s.setValue(12 * 60)
    lbl.setText(_minutes_to_text(s.value()))

    def _on_change(v):
        lbl.setText(_minutes_to_text(v))
        _change_time(main_window, v)

    s.valueChanged.connect(_on_change)

    lay.addWidget(caption)
    lay.addWidget(s)
    lay.addWidget(lbl)
    return w


def _make_intensity_slider(main_window) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(4, 0, 4, 0)
    lay.setSpacing(6)

    caption = QLabel(_t("Int."))
    _LABEL_WIDGETS.append((caption, "Int."))

    s = QSlider(Qt.Horizontal)
    s.setRange(0, 100)
    s.setFixedWidth(60)

    sh = _get_scene_shadows(main_window)
    s.setValue(int((sh.darkness if sh else 0.55) * 100))

    s.valueChanged.connect(
        lambda v: _change_intensity(main_window, v)
    )

    lay.addWidget(caption)
    lay.addWidget(s)
    return w



# --- Following the app language --------------------------------------------
_LABELED_ACTIONS: list = []
_TOOLBARS: list = []
_LAST_LANG = None
_LANG_TIMER = None


def _retranslate() -> None:
    title = _t("Shadows")
    for tb in _TOOLBARS:
        tb.setWindowTitle(title)
    for action, english in _LABELED_ACTIONS:
        action.setText(_t(english))
        action.setToolTip(_t("Toggle shadows on/off"))
        action.setStatusTip(_t("Toggle shadows on/off"))
    for widget, key in _LABEL_WIDGETS:
        widget.setText(_t(key))
    for hook in _REFRESH_HOOKS:
        hook()


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

def _create_shadows_toolbar(main_window) -> None:
    global _TOOLBAR_CREATED
    if _TOOLBAR_CREATED:
        _log("toolbar already created")
        return
    if main_window is None or not hasattr(main_window, "addToolBar"):
        _log("MainWindow unavailable")
        return

    try:
        tb = QToolBar(_t("Shadows"), main_window)
        tb.setObjectName("igz_tb_shadows")
        tb.setWindowTitle(_t("Shadows"))
        main_window.addToolBar(Qt.TopToolBarArea, tb)
        _TOOLBARS.append(tb)

        # Toggle button com suporte a ícones temáticos
        icon = _load_themed_icon("tb_shadowtoggle", main_window)

        act = QAction(icon, _t("Shadows"), main_window)
        act.setToolTip(_t("Toggle shadows on/off"))
        act.setStatusTip(_t("Toggle shadows on/off"))
        act.setCheckable(True)
        _LABELED_ACTIONS.append((act, "Shadows"))

        sh = _get_scene_shadows(main_window)
        if sh is not None:
            act.setChecked(bool(sh.enabled))

        def _on_toggle(checked):
            _toggle_shadows(main_window, checked)
            try:
                native = _find_action(main_window, "Shadows")
                if native is not None and native.isCheckable() and native is not act:
                    if native.isChecked() != checked:
                        native.setChecked(checked)
            except Exception:
                pass

        act.toggled.connect(_on_toggle)
        tb.addAction(act)

        # Sliders
        tb.addSeparator()
        tb.addWidget(_make_date_slider(main_window))
        tb.addSeparator()
        tb.addWidget(_make_time_slider(main_window))
        tb.addSeparator()
        tb.addWidget(_make_intensity_slider(main_window))

        tb.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        tb.setMaximumWidth(tb.sizeHint().width())

        _TOOLBAR_CREATED = True
        _install_language_watcher()
        _log("'Shadows' toolbar created")
    except Exception:
        traceback.print_exc()


# --- setup() ---------------------------------------------------------------
def setup(app):
    print(f"[igz_tb_shadows] setup(app) — PID={os.getpid()}",
          file=sys.stderr, flush=True)
    _log(f"app: {type(app).__module__}.{type(app).__name__}")

    try:
        mw = _discover_main_window() \
             or getattr(app, "main_window", None) \
             or getattr(app, "window", None)

        if mw is None:
            QMessageBox.warning(
                None, _t("Shadows"),
                _t("Could not locate the IngeTrazo main window.")
            )
            return

        _create_shadows_toolbar(mw)
    except Exception:
        traceback.print_exc()
