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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# =========================================================================
# =========================================================================
# Extension: igz_tb_shadows
# Author: Ezequiel M. Rezende
# Version: 3.3.0
# Date: 2026-10-05
# License: GPL-3.0-or-later (same as IngeTrazo)
#
# IngeTrazo — "Shadows" Toolbar
# Location: <plugins>/igz_tb_toolbar/igz_tb_shadows.py
#
# v3.3.0 — Sliders coloridos (data sazonal e hora dia/noite) com marcas
#          abaixo; nascer/pôr do sol calculados por algoritmo solar
#          interno (sem dependências), usando utc_offset da cena.
# =========================================================================

from __future__ import annotations

import math
import os
import sys
import traceback
from datetime import date, datetime, time as dtime, timedelta

from PySide6.QtCore import Qt, QDate, QTime, QTimer
from PySide6.QtGui import QAction, QIcon, QPalette
from PySide6.QtWidgets import (
    QToolBar, QMessageBox, QSlider, QLabel, QWidget, QHBoxLayout, QSizePolicy,
    QDialog, QDialogButtonBox, QVBoxLayout, QPushButton, QLineEdit,
    QCalendarWidget, QTimeEdit, QApplication, QComboBox, QCheckBox,
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


_LOCAL_MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "es": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
    "id": ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"],
    "it": ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"],
    "pt-BR": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"],
}

_LOCAL_MONTH_LETTERS = {
    "en": ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"],
    "es": ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"],
    "id": ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"],
    "it": ["G", "F", "M", "A", "M", "G", "L", "A", "S", "O", "N", "D"],
    "pt-BR": ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"],
}

_LOCAL = {
    "en": {
        "Date": "Date", "Time": "Time", "Int.": "Int.",
        "Location": "Location", "Select Location": "Select Location",
        "Calendar": "Calendar", "Toggle shadows on/off": "Toggle shadows on/off",
        "Source": "Source",
        "Load map": "Load map",
        "Noon": "Noon",
        "Could not locate the IngeTrazo main window.": "Could not locate the IngeTrazo main window.",
    },
    "es": {
        "Date": "Fecha", "Time": "Hora", "Int.": "Int.",
        "Location": "Ubicación", "Select Location": "Definir localización del proyecto",
        "Calendar": "Calendario", "Toggle shadows on/off": "Activar/desactivar sombras",
        "Source": "Fuente",
        "Load map": "Cargar mapa",
        "Noon": "Mediodía",
        "Could not locate the IngeTrazo main window.": "No se pudo localizar la ventana principal de IngeTrazo.",
    },
    "id": {
        "Date": "Tanggal", "Time": "Waktu", "Int.": "Int.",
        "Location": "Lokasi", "Select Location": "Definisikan lokasi proyek",
        "Calendar": "Kalender", "Toggle shadows on/off": "Nyalakan/matikan bayangan",
        "Source": "Sumber",
        "Load map": "Muat peta",
        "Noon": "Tengah hari",
        "Could not locate the IngeTrazo main window.": "Tidak dapat menemukan jendela utama IngeTrazo.",
    },
    "it": {
        "Date": "Data", "Time": "Ora", "Int.": "Int.",
        "Location": "Posizione", "Select Location": "Definisci posizione del progetto",
        "Calendar": "Calendario", "Toggle shadows on/off": "Attiva/disattiva ombre",
        "Source": "Sorgente",
        "Load map": "Carica mappa",
        "Noon": "Mezzogiorno",
        "Could not locate the IngeTrazo main window.": "Impossibile trovare la finestra principale di IngeTrazo.",
    },
    "pt-BR": {
        "Date": "Data", "Time": "Hora", "Int.": "Int.",
        "Location": "Localização", "Select Location": "Definir localização do projeto",
        "Calendar": "Calendário", "Toggle shadows on/off": "Ligar/desligar sombras",
        "Source": "Fonte",
        "Load map": "Carregar mapa",
        "Noon": "Meio-dia",
        "Could not locate the IngeTrazo main window.": "Não foi possível localizar a janela principal do IngeTrazo.",
    },
}


def _t(text: str) -> str:
    out = _it_tr(text)
    if out != text:
        return out
    return _LOCAL.get(_it_language(), {}).get(text, text)


def _months():
    return _LOCAL_MONTHS.get(_it_language(), _LOCAL_MONTHS["en"])


def _month_letters():
    return _LOCAL_MONTH_LETTERS.get(_it_language(), _LOCAL_MONTH_LETTERS["en"])


# --- Locating the icons folder --------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))


def _find_icons_folder():
    c = os.path.join(_HERE, "icons")
    return c if os.path.isdir(c) else None

_ICONS_DIR = _find_icons_folder()


def _discover_main_window():
    try:
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


def _load_themed_icon(base_name: str, main_window) -> QIcon:
    if not _ICONS_DIR:
        return QIcon()
    is_dark = True
    try:
        if main_window is not None:
            bg_color = main_window.palette().color(QPalette.Window)
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


# ==========================================================================
# CÁLCULO SOLAR (sem dependências) — Almanac for Computers, NOAA
# ==========================================================================
def _sun_times(lat: float, lon: float, d: date,
               utc_offset_hours: float) -> tuple[dtime, dtime]:
    n = d.timetuple().tm_yday
    lat_r = math.radians(lat)

    lng_sun = (280.460 + 0.9856474 * n) % 360.0
    g = math.radians((357.528 + 0.9856003 * n) % 360.0)
    lam = math.radians(lng_sun + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    eps = math.radians(23.439 - 0.0000004 * n)

    decl = math.asin(math.sin(eps) * math.sin(lam))

    y = math.tan(eps / 2.0) ** 2
    eot = (
        y * math.sin(2 * lam)
        - 2 * 0.0167 * math.sin(g)
        + 4 * 0.0167 * y * math.sin(g) * math.cos(2 * lam)
        - 0.5 * y * y * math.sin(4 * lam)
        - 1.25 * 0.0167 * 0.0167 * math.sin(2 * g)
    )
    eot_min = math.degrees(eot) * 4.0

    cos_h = (
        math.cos(math.radians(90.833))
        - math.sin(lat_r) * math.sin(decl)
    ) / (math.cos(lat_r) * math.cos(decl))
    cos_h = max(-1.0, min(1.0, cos_h))
    h_deg = math.degrees(math.acos(cos_h))

    fuso_central = 15.0 * utc_offset_hours
    lon_corr_min = 4.0 * (lon - fuso_central)

    noon_min = 12 * 60 - eot_min - lon_corr_min

    sunrise_min = noon_min - h_deg * 4.0
    sunset_min  = noon_min + h_deg * 4.0

    sunrise_min = int(round(sunrise_min)) % (24 * 60)
    sunset_min  = int(round(sunset_min))  % (24 * 60)

    return (
        dtime(sunrise_min // 60, sunrise_min % 60),
        dtime(sunset_min  // 60, sunset_min  % 60),
    )


def _get_utc_offset(main_window) -> float:
    sh = _get_scene_shadows(main_window)
    if sh is not None:
        try:
            off = getattr(sh, "utc_offset", None)
            if off is not None:
                return float(off)
        except Exception:
            pass
    return -3.0


def _get_lat_lon(main_window) -> tuple[float, float]:
    sh = _get_scene_shadows(main_window)
    if sh is not None:
        lat = getattr(sh, "latitude", None)
        lon = getattr(sh, "longitude", None)
        if lat is not None and lon is not None:
            return float(lat), float(lon)
    return -19.9167, -43.9345


def _fmt_hhmm(t: dtime) -> str:
    return f"{t.hour:02d}:{t.minute:02d}"


# --- Diálogo do Calendário -------------------------------------------------
class ShadowsCalendarDialog(QDialog):
    def __init__(self, parent=None, initial_date=None, initial_time=None):
        super().__init__(parent)
        self.setWindowTitle(_t("Calendar"))
        self.resize(320, 360)

        layout = QVBoxLayout(self)

        self.calendar = QCalendarWidget(self)
        if initial_date:
            self.calendar.setSelectedDate(initial_date)
        layout.addWidget(self.calendar)

        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel(_t("Time") + ":"))
        self.time_edit = QTimeEdit(self)
        self.time_edit.setDisplayFormat("HH:mm")
        if initial_time:
            self.time_edit.setTime(initial_time)
        time_layout.addWidget(self.time_edit)
        layout.addLayout(time_layout)

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def get_date_time(self) -> tuple[QDate, QTime]:
        return self.calendar.selectedDate(), self.time_edit.time()


# ==========================================================================
# INTEGRAÇÃO COM O PAINEL TERRENO (BaseMapPanel)
# ==========================================================================
_MAP_SOURCES = [
    ("Esri World Imagery (satélite)", "esri_imagery"),
    ("Sentinel-2 sem nuvens (EOX)",  "s2cloudless"),
    ("OpenStreetMap",         "osm"),
]

_SELECTED_MAP_SID = "esri_imagery"
_LOAD_MAP_TOO = False


def _find_base_map_panel(main_window) -> QWidget | None:
    for w in main_window.findChildren(QWidget):
        if type(w).__name__ == "BaseMapPanel":
            return w
    return None


def _apply_selected_map_source(base_panel) -> None:
    if base_panel is None:
        return
    src = getattr(base_panel, "_source", None)
    if src is None:
        return
    target_sid = _SELECTED_MAP_SID
    for i in range(src.count()):
        if src.itemData(i) == target_sid:
            src.setCurrentIndex(i)
            try:
                base_panel._last_sid = target_sid
            except Exception:
                pass
            _log(f"fonte de mapa definida: {src.itemText(i)!r} ({target_sid})")
            return


def _open_native_georef_dialog(main_window) -> tuple[float, float] | None:
    _log(">>> _open_native_georef_dialog called")

    base_panel = _find_base_map_panel(main_window)
    if base_panel is None:
        _log("BaseMapPanel (painel Terreno) não encontrado")
        return None

    _apply_selected_map_source(base_panel)

    find_btn = getattr(base_panel, "_find", None)
    lat_box  = getattr(base_panel, "_lat", None)
    lon_box  = getattr(base_panel, "_lon", None)
    if find_btn is None:
        _log("botão '_find' não encontrado")
        return None

    vp = getattr(main_window, "viewport", None)
    scene = getattr(vp, "scene", None) if vp else None
    snapshot = None
    if scene is not None:
        snapshot = {
            "tile_layer": getattr(scene, "tile_layer", None),
            "terrain":    getattr(scene, "terrain", None),
            "photo_mesh": getattr(scene, "photo_mesh", None),
        }

    _log("disparando 'Buscar localização…' no painel Terreno")
    try:
        find_btn.click()
    except Exception as e:
        _log(f"erro ao clicar em '_find': {e}")
        traceback.print_exc()
        return None

    if lat_box is None or lon_box is None:
        return None

    try:
        lat = float(lat_box.value())
        lon = float(lon_box.value())
    except Exception:
        return None

    _log(f"coords depois do diálogo: ({lat}, {lon})")

    if not _LOAD_MAP_TOO and scene is not None and snapshot is not None:
        try:
            scene.tile_layer = snapshot["tile_layer"]
            scene.terrain    = snapshot["terrain"]
            scene.photo_mesh = snapshot["photo_mesh"]
        except Exception as e:
            _log(f"erro ao restaurar tile_layer: {e}")
        if vp is not None:
            try:
                vp.update()
            except Exception:
                pass

    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return None

    return lat, lon


# --- Acesso e Atualização de Sombras e Cena --------------------------------
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
    sh.day = d.day()
    sh.enabled = True
    _repaint(main_window)


def _change_time(main_window, minutes: int) -> None:
    sh = _get_scene_shadows(main_window)
    if sh is None:
        return
    sh.hour = minutes // 60
    sh.minute = minutes % 60
    sh.enabled = True
    _repaint(main_window)


def _change_intensity(main_window, value_0_100: int) -> None:
    sh = _get_scene_shadows(main_window)
    if sh is None:
        return
    sh.darkness = value_0_100 / 100.0
    _repaint(main_window)


def _change_location(main_window, lat: float, lng: float) -> None:
    sh = _get_scene_shadows(main_window)
    if sh is not None:
        if hasattr(sh, "latitude"):
            sh.latitude = lat
        if hasattr(sh, "longitude"):
            sh.longitude = lng

    vp = getattr(main_window, "viewport", None)
    if vp is not None:
        scene = getattr(vp, "scene", None)
        if scene is not None:
            for attr in ("geo_location", "location"):
                if hasattr(scene, attr):
                    try:
                        setattr(scene, attr, (lat, lng))
                    except Exception:
                        pass
        if hasattr(vp, "set_geo_location"):
            try:
                vp.set_geo_location(lat, lng)
            except Exception:
                pass
    _repaint(main_window)


def _day_of_year_to_text(day_of_year: int) -> str:
    d = QDate(2026, 1, 1).addDays(day_of_year - 1)
    months = _months()
    return f"{d.day():02d} {months[d.month()-1]}"


def _minutes_to_text(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


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


# --- Construção da Barra de Ferramentas ------------------------------------
_LABEL_WIDGETS: list = []
_REFRESH_HOOKS: list = []
_DATE_SLIDER: QSlider | None = None
_TIME_SLIDER: QSlider | None = None


def _slider_qss(gradient_qss: str, height: int = 4) -> str:
    return f"""
    QSlider::groove:horizontal {{
        height: {height}px;
        background: {gradient_qss};
        border: 1px solid rgba(0,0,0,60);
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: #f7f7f7;
        border: 1px solid #555;
        width: 12px;
        margin: -3px 0;
        border-radius: 3px;
    }}
    QSlider::handle:horizontal:hover {{
        background: #ffffff;
    }}
    QSlider::sub-page:horizontal, QSlider::add-page:horizontal {{
        background: transparent;
    }}
    """


_SEASONAL_QSS = (
    "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
    "stop:0.00 #c8171a, "
    "stop:0.09 #d53825, "
    "stop:0.18 #e07a2c, "
    "stop:0.27 #ecb13a, "
    "stop:0.36 #f2d160, "
    "stop:0.45 #f4e39a, "
    "stop:0.54 #f7edb4, "
    "stop:0.63 #f4e096, "
    "stop:0.72 #eec24c, "
    "stop:0.81 #e88a2e, "
    "stop:0.90 #dd4a24, "
    "stop:1.00 #c8171a)"
)

_DAYNIGHT_QSS = (
    "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
    "stop:0.00 #0b2340, "
    "stop:0.18 #163a63, "
    "stop:0.25 #a8c8e6, "
    "stop:0.33 #eef4fb, "
    "stop:0.50 #ffffff, "
    "stop:0.67 #eef4fb, "
    "stop:0.75 #a8c8e6, "
    "stop:0.82 #163a63, "
    "stop:1.00 #0b2340)"
)


# ==========================================================================
# Slider de DATA
# ==========================================================================
def _make_date_slider(main_window) -> QWidget:
    global _DATE_SLIDER
    container = QWidget()
    container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

    outer = QVBoxLayout(container)
    outer.setContentsMargins(4, 0, 4, 0)
    outer.setSpacing(0)

    row = QWidget()
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(6)

    caption = QLabel(_t("Date"))
    _LABEL_WIDGETS.append((caption, "Date"))

    s = QSlider(Qt.Horizontal)
    s.setRange(1, 365)
    s.setFixedWidth(140)
    s.setFixedHeight(10)
    s.setStyleSheet(_slider_qss(_SEASONAL_QSS))
    _DATE_SLIDER = s

    sh = _get_scene_shadows(main_window)
    if sh is not None:
        try:
            init_day = QDate(2026, int(sh.month), int(sh.day)).dayOfYear()
        except Exception:
            init_day = 80
        s.setValue(init_day)
    else:
        s.setValue(80)

    lbl_val = QLabel(_day_of_year_to_text(s.value()))
    lbl_val.setMinimumWidth(60)
    lbl_val.setAlignment(Qt.AlignCenter)

    lay.addWidget(caption)
    lay.addWidget(s)
    lay.addWidget(lbl_val)

    months_row = QWidget()
    m_lay = QHBoxLayout(months_row)
    m_lay.setContentsMargins(0, 0, 0, 0)
    m_lay.setSpacing(0)

    left_pad = QLabel()
    left_pad.setFixedWidth(caption.sizeHint().width() + 6)
    m_lay.addWidget(left_pad)

    letters = _month_letters()
    months_box = QWidget()
    months_box.setFixedWidth(140)
    m_inner = QHBoxLayout(months_box)
    m_inner.setContentsMargins(0, 0, 0, 0)
    m_inner.setSpacing(0)
    for letter in letters:
        col = QLabel(letter)
        col.setAlignment(Qt.AlignCenter)
        col.setStyleSheet("color: #444; font-size: 10px;")
        m_inner.addWidget(col, 1)
    m_lay.addWidget(months_box)

    right_pad = QLabel()
    right_pad.setFixedWidth(lbl_val.minimumWidth() + 6)
    m_lay.addWidget(right_pad)

    outer.addWidget(row)
    outer.addWidget(months_row)

    def _on_date_changed(v: int) -> None:
        lbl_val.setText(_day_of_year_to_text(v))
        _change_date(main_window, v)
        _refresh_sun_marks()

    s.valueChanged.connect(_on_date_changed)
    _REFRESH_HOOKS.append(lambda: lbl_val.setText(_day_of_year_to_text(s.value())))

    return container


# ==========================================================================
# Slider de HORA
# ==========================================================================
def _make_time_slider(main_window) -> QWidget:
    global _TIME_SLIDER
    container = QWidget()
    container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

    outer = QVBoxLayout(container)
    outer.setContentsMargins(4, 0, 4, 0)
    outer.setSpacing(0)

    row = QWidget()
    lay = QHBoxLayout(row)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(6)

    caption = QLabel(_t("Time"))
    _LABEL_WIDGETS.append((caption, "Time"))

    s = QSlider(Qt.Horizontal)
    s.setRange(0, 1439)
    s.setFixedWidth(140)
    s.setFixedHeight(10)
    s.setStyleSheet(_slider_qss(_DAYNIGHT_QSS))
    _TIME_SLIDER = s

    sh = _get_scene_shadows(main_window)
    if sh is not None:
        try:
            init_min = int(sh.hour) * 60 + int(sh.minute)
        except Exception:
            init_min = 12 * 60
        s.setValue(init_min)
    else:
        s.setValue(12 * 60)

    lbl_val = QLabel(_minutes_to_text(s.value()))
    lbl_val.setMinimumWidth(50)
    lbl_val.setAlignment(Qt.AlignCenter)

    lay.addWidget(caption)
    lay.addWidget(s)
    lay.addWidget(lbl_val)

    sun_row = QWidget()
    sun_lay = QHBoxLayout(sun_row)
    sun_lay.setContentsMargins(0, 0, 0, 0)
    sun_lay.setSpacing(0)

    left_pad = QLabel()
    left_pad.setFixedWidth(caption.sizeHint().width() + 6)
    sun_lay.addWidget(left_pad)

    sun_box = QWidget()
    sun_box.setFixedWidth(140)
    sun_inner = QHBoxLayout(sun_box)
    sun_inner.setContentsMargins(0, 0, 0, 0)
    sun_inner.setSpacing(0)

    lbl_sunrise = QLabel("--:--")
    lbl_sunrise.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    lbl_sunrise.setStyleSheet("color: #444; font-size: 10px;")

    lbl_noon = QLabel(_t("Noon"))
    lbl_noon.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
    lbl_noon.setStyleSheet("color: #444; font-size: 10px;")

    lbl_sunset = QLabel("--:--")
    lbl_sunset.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    lbl_sunset.setStyleSheet("color: #444; font-size: 10px;")

    sun_inner.addWidget(lbl_sunrise, 0, Qt.AlignLeft)
    sun_inner.addStretch(1)
    sun_inner.addWidget(lbl_noon, 0, Qt.AlignHCenter)
    sun_inner.addStretch(1)
    sun_inner.addWidget(lbl_sunset, 0, Qt.AlignRight)

    sun_lay.addWidget(sun_box)

    right_pad = QLabel()
    right_pad.setFixedWidth(lbl_val.minimumWidth() + 6)
    sun_lay.addWidget(right_pad)

    outer.addWidget(row)
    outer.addWidget(sun_row)

    def _recalc_sun_marks() -> None:
        try:
            day_of_year = _DATE_SLIDER.value() if _DATE_SLIDER is not None else 80
        except Exception:
            day_of_year = 80
        try:
            d = QDate(2026, 1, 1).addDays(day_of_year - 1)
            py_date = date(d.year(), d.month(), d.day())
        except Exception:
            py_date = date.today()
        try:
            lat, lon = _get_lat_lon(main_window)
            off = _get_utc_offset(main_window)
            sunrise, sunset = _sun_times(lat, lon, py_date, off)
            lbl_sunrise.setText(_fmt_hhmm(sunrise))
            lbl_sunset.setText(_fmt_hhmm(sunset))
        except Exception as e:
            _log(f"erro no cálculo solar: {e}")
            lbl_sunrise.setText("--:--")
            lbl_sunset.setText("--:--")

    def _retranslate_sun_labels() -> None:
        lbl_noon.setText(_t("Noon"))

    sun_box._refresh_hooks = (_recalc_sun_marks, _retranslate_sun_labels)
    _SUN_LABELS.append(sun_box)

    def _on_time_changed(v: int) -> None:
        lbl_val.setText(_minutes_to_text(v))
        _change_time(main_window, v)

    s.valueChanged.connect(_on_time_changed)
    _REFRESH_HOOKS.append(lambda: lbl_val.setText(_minutes_to_text(s.value())))

    return container


_SUN_LABELS: list = []


def _refresh_sun_marks() -> None:
    for item in list(_SUN_LABELS):
        hooks = getattr(item, "_refresh_hooks", None)
        if hooks:
            for hook in hooks:
                try:
                    hook()
                except Exception as e:
                    _log(f"erro ao atualizar marcas solares: {e}")


# ==========================================================================
# Botão do calendário
# ==========================================================================
def _make_calendar_button(main_window) -> QWidget:
    w = QWidget()
    w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

    lay = QHBoxLayout(w)
    lay.setContentsMargins(4, 0, 4, 0)
    lay.setSpacing(4)

    btn_cal = QPushButton()
    btn_cal.setToolTip(_t("Calendar"))
    icon_cal = _load_themed_icon("shadows_calendar", main_window)
    if not icon_cal.isNull():
        btn_cal.setIcon(icon_cal)
    else:
        btn_cal.setText("📅")
    btn_cal.setFixedWidth(28)

    def _open_calendar():
        sh = _get_scene_shadows(main_window)
        init_d = QDate(2026, sh.month, sh.day) if sh else QDate.currentDate()
        init_t = QTime(sh.hour, sh.minute) if sh else QTime(12, 0)
        dlg = ShadowsCalendarDialog(parent=main_window,
                                    initial_date=init_d, initial_time=init_t)
        if dlg.exec() == QDialog.Accepted:
            sel_d, sel_t = dlg.get_date_time()
            day_num = sel_d.dayOfYear()
            minutes_num = sel_t.hour() * 60 + sel_t.minute()
            _change_date(main_window, day_num)
            _change_time(main_window, minutes_num)
            if _DATE_SLIDER is not None:
                _DATE_SLIDER.setValue(day_num)
            if _TIME_SLIDER is not None:
                _TIME_SLIDER.setValue(minutes_num)
            _refresh_sun_marks()

    btn_cal.clicked.connect(_open_calendar)
    lay.addWidget(btn_cal)
    return w


# ==========================================================================
# Slider de intensidade
# ==========================================================================
def _make_intensity_slider(main_window) -> QWidget:
    w = QWidget()
    w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

    lay = QHBoxLayout(w)
    lay.setContentsMargins(4, 0, 4, 0)
    lay.setSpacing(6)

    caption = QLabel(_t("Int."))
    _LABEL_WIDGETS.append((caption, "Int."))

    s = QSlider(Qt.Horizontal)
    s.setRange(0, 100)
    s.setFixedWidth(60)
    s.setFixedHeight(10)

    sh = _get_scene_shadows(main_window)
    s.setValue(int((sh.darkness if sh else 0.55) * 100))
    s.valueChanged.connect(lambda v: _change_intensity(main_window, v))

    lay.addWidget(caption)
    lay.addWidget(s)
    return w


# ==========================================================================
# Combo de fonte de mapa
# ==========================================================================
def _make_map_source_combo(main_window) -> QWidget:
    w = QWidget()
    w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

    lay = QHBoxLayout(w)
    lay.setContentsMargins(4, 0, 4, 0)
    lay.setSpacing(4)

    caption = QLabel(_t("Source"))
    _LABEL_WIDGETS.append((caption, "Source"))

    combo = QComboBox()
    combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
    combo.setMinimumContentsLength(12)
    combo.setFixedWidth(110)
    for label, sid in _MAP_SOURCES:
        combo.addItem(label, sid)

    base_panel = _find_base_map_panel(main_window)
    current_sid = _SELECTED_MAP_SID
    if base_panel is not None:
        src = getattr(base_panel, "_source", None)
        if src is not None:
            current_sid = (getattr(base_panel, "_last_sid", None)
                           or src.currentData()
                           or _SELECTED_MAP_SID)
    for i in range(combo.count()):
        if combo.itemData(i) == current_sid:
            combo.setCurrentIndex(i)
            break

    def _on_source_changed(idx: int):
        global _SELECTED_MAP_SID
        sid = combo.itemData(idx)
        if sid:
            _SELECTED_MAP_SID = sid

    combo.currentIndexChanged.connect(_on_source_changed)
    lay.addWidget(caption)
    lay.addWidget(combo)
    return w


# ==========================================================================
# Coordenadas + botão mapa + checkbox
# ==========================================================================
def _make_location_widget(main_window) -> QWidget:
    w = QWidget()
    w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

    lay = QHBoxLayout(w)
    lay.setContentsMargins(4, 0, 4, 0)
    lay.setSpacing(4)

    txt_coords = QLineEdit()
    txt_coords.setFixedWidth(145)
    txt_coords.setPlaceholderText("-19.9167, -43.9345")

    init_lat, init_lng = _get_lat_lon(main_window)
    txt_coords.setText(f"{init_lat:.4f}, {init_lng:.4f}")

    def _on_text_edited():
        try:
            parts = [float(p.strip()) for p in txt_coords.text().split(",")]
            if len(parts) == 2:
                _change_location(main_window, parts[0], parts[1])
                _refresh_sun_marks()
        except ValueError:
            pass

    txt_coords.editingFinished.connect(_on_text_edited)

    chk_map = QCheckBox(_t("Load map"))
    chk_map.setChecked(_LOAD_MAP_TOO)

    def _on_chk_changed(state):
        global _LOAD_MAP_TOO
        try:
            _LOAD_MAP_TOO = (int(state) == int(Qt.Checked))
        except Exception:
            _LOAD_MAP_TOO = bool(state)

    chk_map.stateChanged.connect(_on_chk_changed)

    btn_map = QPushButton()
    btn_map.setToolTip(_t("Select Location"))
    icon_map = _load_themed_icon("tb_map_picker", main_window)
    if not icon_map.isNull():
        btn_map.setIcon(icon_map)
    else:
        btn_map.setText("🗺️")
    btn_map.setFixedWidth(28)

    def _open_map():
        coords = _open_native_georef_dialog(main_window)
        if coords is not None:
            lat, lng = coords
            txt_coords.setText(f"{lat:.6f}, {lng:.6f}")
            _change_location(main_window, lat, lng)
            _refresh_sun_marks()

    btn_map.clicked.connect(_open_map)

    lay.addWidget(txt_coords)
    lay.addWidget(btn_map)
    lay.addWidget(chk_map)
    return w

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
    _refresh_sun_marks()


def _poll_language() -> None:
    global _LAST_LANG
    code = _it_language()
    if code != _LAST_LANG:
        _LAST_LANG = code
        _retranslate()


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


_TOOLBAR_CREATED = False


# ==========================================================================
# Criação da barra de ferramentas
# ==========================================================================
def _create_shadows_toolbar(main_window) -> None:
    global _TOOLBAR_CREATED
    if _TOOLBAR_CREATED:
        return
    if main_window is None or not hasattr(main_window, "addToolBar"):
        return

    try:
        tb = QToolBar(_t("Shadows"), main_window)
        tb.setObjectName("igz_tb_shadows")
        tb.setWindowTitle(_t("Shadows"))
        main_window.addToolBar(Qt.TopToolBarArea, tb)
        _TOOLBARS.append(tb)

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

        act.toggled.connect(_on_toggle)
        tb.addAction(act)

        tb.addSeparator()
        tb.addWidget(_make_date_slider(main_window))
        tb.addSeparator()
        tb.addWidget(_make_time_slider(main_window))
        tb.addSeparator()
        tb.addWidget(_make_calendar_button(main_window))
        tb.addSeparator()
        tb.addWidget(_make_intensity_slider(main_window))
        tb.addSeparator()
        tb.addWidget(_make_map_source_combo(main_window))
        tb.addSeparator()
        tb.addWidget(_make_location_widget(main_window))

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        tb.addWidget(spacer)

        tb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        _TOOLBAR_CREATED = True
        _install_language_watcher()
        _refresh_sun_marks()
        _log("'Shadows' toolbar created")
    except Exception:
        traceback.print_exc()


def setup(app):
    print(f"[igz_tb_shadows] setup(app) — PID={os.getpid()}", file=sys.stderr, flush=True)

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