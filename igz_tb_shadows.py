# =========================================================================
# Extensão: igz_tb_shadows
# Autor: Ezequiel M. Rezende
# Versão: 1.0.0
# Data: 2026-09-30
# Licença: GPL-3.0-or-later (mesma do IngeTrazo)
#
# IngeTrazo — Barra de Ferramentas "Shadows"
# Local: <plugins>/igz_tb_shadows.py
#
# ⚠️  AVISO DE API FRÁGIL
# -------------------------------------------------------------------------
# O `docs/plugins.md` do IngeTrazo afirma:
#     "The plugin API is not stable yet — expect breaking changes during
#      the 0.x series."
#
# Este plugin usa pontos NÃO documentados como API pública de extensão:
#
#   • viewport.scene.shadows          (cena via viewport, não app.scene)
#   • ShadowSettings.*                (campos: month/day/hour/minute/...)
#   • QToolBar criada direto via PySide, sem a API `app.add_*`
#
# Todos os pontos frágeis estão marcados com "⚠️ FRÁGIL" abaixo.
# O código é tolerante a falhas: se `shadows` não existir, apenas
# loga e retorna, sem quebrar o IngeTrazo.
# =========================================================================
from __future__ import annotations

import os
import sys
import traceback

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QToolBar, QMessageBox, QSlider, QLabel, QWidget, QHBoxLayout, QSizePolicy
)

DEBUG = True

def _log(msg: str) -> None:
    if DEBUG:
        print(f"[igz_tb_shadows] {msg}", file=sys.stderr, flush=True)


# --- Localização da pasta de ícones ---------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))


def _localizar_pasta_icones():
    """Ícones ficam em `<plugins>/icons/`, ao lado deste arquivo."""
    c = os.path.join(_HERE, "icons")
    return c if os.path.isdir(c) else None

_ICONS_DIR = _localizar_pasta_icones()
_log(f"pasta de ícones: {_ICONS_DIR}")


# --- Descoberta da MainWindow ---------------------------------------------
def _descobrir_main_window():
    """
    Descoberta via QApplication.topLevelWidgets().
    Mesma estratégia do igz_tb_style.py — ver comentário lá.
    """
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


# --- Acesso à cena e ao viewport ------------------------------------------
def _get_scene_shadows(main_window):
    """
    A cena vive em `main_window.viewport.scene` — MainWindow NÃO tem
    atributo `.scene`.

    ⚠️ FRÁGIL: usa a cadeia `viewport.scene.shadows`, que é como o
    IngeTrazo 0.x armazena as configurações do sol. Não está na API
    pública de extensão. Se mudar de lugar numa próxima versão, basta
    ajustar este único helper — todo o resto usa ele.
    """
    vp = getattr(main_window, "viewport", None)
    if vp is None:
        return None
    scene = getattr(vp, "scene", None)
    if scene is None:
        return None
    return getattr(scene, "shadows", None)


def _repintar(main_window) -> None:
    """
    Pede um repaint do viewport. O paintGL do IngeTrazo lê
    `scene.shadows` a cada frame e redesenha o sol sozinho.
    """
    vp = getattr(main_window, "viewport", None)
    if vp is not None and hasattr(vp, "update"):
        vp.update()


# --- Ações (só alteram scene.shadows + update) ----------------------------
# ⚠️ FRÁGIL: os nomes dos campos (`enabled`, `month`, `day`, `hour`,
# `minute`, `darkness`) são os da dataclass `core.sun.ShadowSettings`.
# Se a dataclass mudar, os atributos precisam acompanhar.

def _toggle_shadows(main_window, checked: bool) -> None:
    sh = _get_scene_shadows(main_window)
    if sh is None:
        return
    sh.enabled = bool(checked)
    _repintar(main_window)


def _mudar_data(main_window, dia_do_ano: int) -> None:
    sh = _get_scene_shadows(main_window)
    if sh is None:
        return
    d = QDate(2026, 1, 1).addDays(dia_do_ano - 1)
    sh.month = d.month()
    sh.day   = d.day()
    sh.enabled = True
    _repintar(main_window)


def _mudar_hora(main_window, minutos: int) -> None:
    sh = _get_scene_shadows(main_window)
    if sh is None:
        return
    sh.hour   = minutos // 60
    sh.minute = minutos % 60
    sh.enabled = True
    _repintar(main_window)


def _mudar_intensidade(main_window, valor_0_100: int) -> None:
    sh = _get_scene_shadows(main_window)
    if sh is None:
        return
    sh.darkness = valor_0_100 / 100.0
    _repintar(main_window)


# --- Labels dinâmicos ------------------------------------------------------
_MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
          "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

def _dia_do_ano_para_texto(dia_do_ano: int) -> str:
    d = QDate(2026, 1, 1).addDays(dia_do_ano - 1)
    return f"{d.day():02d} {_MESES[d.month()-1]}"

def _minutos_para_texto(minutos: int) -> str:
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


# --- Widgets ---------------------------------------------------------------
def _fazer_slider_data(main_window) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(4, 0, 4, 0)
    lay.setSpacing(6)

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
    lbl.setText(_dia_do_ano_para_texto(s.value()))

    def _on_change(v):
        lbl.setText(_dia_do_ano_para_texto(v))
        _mudar_data(main_window, v)

    s.valueChanged.connect(_on_change)

    lay.addWidget(QLabel("Data"))
    lay.addWidget(s)
    lay.addWidget(lbl)
    return w


def _fazer_slider_hora(main_window) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(4, 0, 4, 0)
    lay.setSpacing(6)

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
    lbl.setText(_minutos_para_texto(s.value()))

    def _on_change(v):
        lbl.setText(_minutos_para_texto(v))
        _mudar_hora(main_window, v)

    s.valueChanged.connect(_on_change)

    lay.addWidget(QLabel("Hora"))
    lay.addWidget(s)
    lay.addWidget(lbl)
    return w


def _fazer_slider_intensidade(main_window) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(4, 0, 4, 0)
    lay.setSpacing(6)

    s = QSlider(Qt.Horizontal)
    s.setRange(0, 100)
    s.setFixedWidth(60)

    sh = _get_scene_shadows(main_window)
    s.setValue(int((sh.darkness if sh else 0.55) * 100))

    s.valueChanged.connect(
        lambda v: _mudar_intensidade(main_window, v)
    )

    lay.addWidget(QLabel("Int."))
    lay.addWidget(s)
    return w


# --- Criação da toolbar ---------------------------------------------------
_TOOLBAR_CRIADA = False

def _criar_toolbar_shadows(main_window) -> None:
    """
    Cria a barra "Shadows".

    ⚠️ FRÁGIL: mesmo caso do igz_tb_style — QToolBar via PySide.
    Nota: o botão toggle SINCRONIZA com a ação nativa "Sombras" do
    menu do IngeTrazo, para que os dois nunca fiquem fora de fase.
    """
    global _TOOLBAR_CRIADA
    if _TOOLBAR_CRIADA:
        _log("toolbar já criada")
        return
    if main_window is None or not hasattr(main_window, "addToolBar"):
        _log("MainWindow indisponível")
        return

    try:
        tb = QToolBar("Shadows", main_window)
        tb.setObjectName("igz_tb_shadows")
        tb.setWindowTitle("Shadows")
        main_window.addToolBar(Qt.TopToolBarArea, tb)

        # Botão toggle
        icon = QIcon()
        if _ICONS_DIR:
            p = os.path.join(_ICONS_DIR, "tb_shadowtoggle.svg")
            if os.path.isfile(p):
                icon = QIcon(p)
            else:
                _log(f"ícone não encontrado: {p}")

        act = QAction(icon, "Shadows", main_window)
        act.setToolTip("Liga/desliga sombras")
        act.setCheckable(True)

        sh = _get_scene_shadows(main_window)
        if sh is not None:
            act.setChecked(bool(sh.enabled))

        def _on_toggle(checked):
            _toggle_shadows(main_window, checked)
            # ⚠️ FRÁGIL: procura por uma QAction de texto "Sombras"
            # (nome em português, mantido pelo IngeTrazo). Se a UI for
            # traduzida ou a ação mudar de texto, esta sincronia para
            # de funcionar — mas a barra continua operando normalmente.
            try:
                for a in main_window.findChildren(QAction):
                    if a.text() == "Sombras" and a.isCheckable() and a is not act:
                        if a.isChecked() != checked:
                            a.setChecked(checked)
                        break
            except Exception:
                pass

        act.toggled.connect(_on_toggle)
        tb.addAction(act)

        # Sliders
        tb.addSeparator()
        tb.addWidget(_fazer_slider_data(main_window))
        tb.addSeparator()
        tb.addWidget(_fazer_slider_hora(main_window))
        tb.addSeparator()
        tb.addWidget(_fazer_slider_intensidade(main_window))

        # Faz a barra acoplada respeitar o tamanho do conteúdo
        tb.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        tb.setMaximumWidth(tb.sizeHint().width())

        _TOOLBAR_CRIADA = True
        _log("toolbar 'Shadows' criada")
    except Exception:
        traceback.print_exc()


# --- setup() --------------------------------------------------------------
def setup(app):
    """
    Ponto de entrada chamado UMA vez pelo IngeTrazo.
    Ver comentário equivalente em igz_tb_style.py.
    """
    print(f"[igz_tb_shadows] setup(app) — PID={os.getpid()}",
          file=sys.stderr, flush=True)
    _log(f"app: {type(app).__module__}.{type(app).__name__}")

    try:
        mw = _descobrir_main_window() \
             or getattr(app, "main_window", None) \
             or getattr(app, "window", None)

        if mw is None:
            QMessageBox.warning(
                None, "Shadows",
                "Não foi possível localizar a janela principal do IngeTrazo."
            )
            return

        _criar_toolbar_shadows(mw)
    except Exception:
        traceback.print_exc()