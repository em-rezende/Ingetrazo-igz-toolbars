# =========================================================================
# Extensão: igz_tb_style
# Autor: Ezequiel M. Rezende
# Versão: 1.2.0
# Data: 2026-10-01
# Licença: GPL-3.0-or-later (mesma do IngeTrazo)
#
# IngeTrazo — Barra de Ferramentas "Styles"
# Local: <plugins>/igz_tb_style.py
#
# Espelha os comandos do menu Câmera ▸ Estilo.
# Em vez de reimplementar a lógica, encontra a QAction nativa e
# dispara trigger() — exatamente o que o usuário faria clicando.
# =========================================================================
from __future__ import annotations

import os
import sys
import traceback

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QToolBar, QMessageBox, QSizePolicy, QFrame

DEBUG = True

def _log(msg: str) -> None:
    if DEBUG:
        print(f"[igz_tb_style] {msg}", file=sys.stderr, flush=True)


# --- Localização da pasta de ícones ---------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))

def _localizar_pasta_icones():
    c = os.path.join(_HERE, "icons")
    return c if os.path.isdir(c) else None

_ICONS_DIR = _localizar_pasta_icones()


# --- Descoberta da MainWindow ---------------------------------------------
def _descobrir_main_window():
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


# --- Mapa: nome do botão → texto exato da QAction no menu ----------------
# (ordem idêntica à do menu Câmera ▸ Estilo)
ACOES_MENU = [
    ("Padrão",          "tb_default.svg",      "Padrão"),
    ("Arquitetônico",   "tb_architectural.svg","Arquitetônico"),
    ("Sombreado",       "tb_shaded.svg",       "Sombreado"),
    ("Linha oculta",    "tb_hiddenline.svg",   "Linha oculta"),
    ("Monocromático",   "tb_monochrome.svg",   "Monocromático"),
    ("Wireframe",       "tb_wireframe.svg",    "Wireframe"),
    ("Raio-X",          "tb_xray.svg",         "Raio-X"),
    # separador implícito no layout abaixo
    ("Alternar raio-X", "tb_xraytoggle.svg",   "Alternar raio-X"),
    ("Arestas",         "tb_edges.svg",        "Arestas"),
    ("Perfis",          "tb_profiles.svg",     "Perfis"),
    ("Arestas de trás", "tb_backedges.svg",    "Arestas de trás"),
]


# --- Encontra e dispara a QAction nativa ----------------------------------
def _disparar_acao(main_window, texto_acao: str) -> bool:
    """
    Procura uma QAction com o texto exato (case-sensitive) na MainWindow
    e dispara trigger() — exatamente como o menu nativo faria.
    """
    try:
        for a in main_window.findChildren(QAction):
            if a.text() == texto_acao:
                a.trigger()
                _log(f"trigger: '{texto_acao}'")
                return True
        _log(f"QAction '{texto_acao}' não encontrada no menu")
        return False
    except Exception:
        traceback.print_exc()
        return False


# --- Criação da toolbar ---------------------------------------------------
_TOOLBAR_CRIADA = False

from PySide6.QtCore import Qt, QTimer   # adicione QTimer ao import

def _criar_toolbar_style(main_window) -> None:
    global _TOOLBAR_CRIADA
    if _TOOLBAR_CRIADA:
        return
    if main_window is None or not hasattr(main_window, "addToolBar"):
        _log("MainWindow indisponível")
        return

    try:
        tb = QToolBar("Styles", main_window)
        tb.setObjectName("igz_tb_style")
        tb.setWindowTitle("Styles")
        main_window.addToolBar(Qt.TopToolBarArea, tb)

        def _adicionar_separador():
            """Linha vertical com cor forçada — visível sobre o fundo escuro."""
            f = QFrame(tb)
            f.setFrameShape(QFrame.VLine)
            f.setFrameShadow(QFrame.Plain)          # ← Plain, não Sunken
            f.setFixedWidth(1)
            f.setContentsMargins(6, 4, 6, 4)
            f.setStyleSheet(
                "QFrame { background-color: rgba(160, 160, 160, 0.9); "
                "border: none; }"
            )
            tb.addWidget(f)

        for i, (nome, arquivo, texto_acao) in enumerate(ACOES_MENU):
            # Separador antes dos toggles (após "Raio-X", índice 6)
            if i == 7:
                _adicionar_separador()

            icon = QIcon()
            if _ICONS_DIR:
                p = os.path.join(_ICONS_DIR, arquivo)
                if os.path.isfile(p):
                    icon = QIcon(p)

            a = QAction(icon, nome, main_window)
            a.setToolTip(texto_acao)
            a.setStatusTip(texto_acao)
            a.triggered.connect(
                lambda _=False, t=texto_acao:
                    _disparar_acao(main_window, t)
            )
            tb.addAction(a)

        # Faz a barra acoplada respeitar o tamanho do conteúdo.
        # Sem +40 de margem — o sizeHint já inclui o separador.
        tb.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        tb.setMaximumWidth(tb.sizeHint().width())

        _TOOLBAR_CRIADA = True
        _log("toolbar 'Styles' criada (espelhando o menu nativo)")
    except Exception:
        traceback.print_exc()
        
        
# --- setup() --------------------------------------------------------------
def setup(app):
    print(f"[igz_tb_style] setup(app) — PID={os.getpid()}",
          file=sys.stderr, flush=True)
    try:
        mw = _descobrir_main_window() \
             or getattr(app, "main_window", None) \
             or getattr(app, "window", None)
        if mw is None:
            QMessageBox.warning(
                None, "Styles",
                "Não foi possível localizar a janela principal."
            )
            return
        _criar_toolbar_style(mw)
    except Exception:
        traceback.print_exc()