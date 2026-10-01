# =========================================================================
# Extensão: igz_tb_style
# Autor: Ezequiel M. Rezende
# Versão: 1.0.0
# Data: 2026-09-30
# Licença: GPL-3.0-or-later (mesma do IngeTrazo)
#
# IngeTrazo — Barra de Ferramentas "Styles"
# Local: <plugins>/igz_tb_style.py
#
# ⚠️  AVISO DE API FRÁGIL
# -------------------------------------------------------------------------
# O `docs/plugins.md` do IngeTrazo afirma explicitamente:
#     "The plugin API is not stable yet — expect breaking changes during
#      the 0.x series."
#
# Este plugin usa alguns pontos que NÃO estão documentados como API
# pública de extensão:
#
#   • viewport.style_override         (atributo público mas não na API)
#   • core.style.style_by_name(...)   (módulo core — semi-público)
#   • QToolBar criada direto via PySide, sem a API `app.add_*`
#
# Se qualquer um desses mudar numa próxima versão 0.x, o plugin pode
# parar de funcionar. Os pontos frágeis estão marcados abaixo com
# "⚠️ FRÁGIL". A lógica principal é tolerante a falhas: se algo der
# errado, apenas loga e retorna, sem quebrar o IngeTrazo.
# =========================================================================
from __future__ import annotations

import os
import sys
import traceback

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QToolBar, QMessageBox, QSizePolicy   # QSizePolicy necessário


DEBUG = True

def _log(msg: str) -> None:
    if DEBUG:
        print(f"[igz_tb_style] {msg}", file=sys.stderr, flush=True)


# --- Localização da pasta de ícones ---------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))

def _localizar_pasta_icones():
    """Ícones ficam em `<plugins>/icons/`, ao lado deste arquivo."""
    c = os.path.join(_HERE, "icons")
    return c if os.path.isdir(c) else None

_ICONS_DIR = _localizar_pasta_icones()
_log(f"pasta de ícones: {_ICONS_DIR}")


# --- Descoberta da janela principal ---------------------------------------
def _descobrir_main_window():
    """
    Descoberta da MainWindow via QApplication.topLevelWidgets().

    A API oficial (plugins.md) expõe `app.window` no `setup(app)`;
    porém usar essa referência diretamente torna o plugin dependente
    do ciclo de vida da app. A descoberta dinâmica é mais robusta
    durante a fase 0.x.
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


# --- Definição das ações --------------------------------------------------
# (nome, arquivo_ícone, dica, tipo, valor)
# tipo = "style"  → aplica o estilo interno 'valor' (nome em core.style)
# tipo = "toggle" → inverte o flag booleano 'valor' no estilo atual
ACOES_STYLE = [
    ("Back Edges",  "tb_backedges.svg",  "Exibe arestas posteriores",         "toggle", "back_edges"),
    ("Hidden Line", "tb_hiddenline.svg", "Estilo linha oculta",               "style",  "Hidden line"),
    ("Monochrome",  "tb_monochrome.svg", "Estilo monocromático",              "style",  "Monochrome"),
    ("PBR",         "tb_pbr.svg",        "Renderização com texturas (Default)","style", "Default"),
    ("Shaded",      "tb_shaded.svg",     "Estilo sombreado",                  "style",  "Shaded"),
    ("Textures",    "tb_textures.svg",   "Texturas em fundo branco (Architectural)","style", "Architectural"),
    ("Wireframe",   "tb_wireframe.svg",  "Estilo wireframe",                  "style",  "Wireframe"),
    ("X-Ray",       "tb_xray.svg",       "Estilo raio-X (transparente)",      "style",  "X-ray"),
]


# --- Callback dos botões --------------------------------------------------
def _aplicar_estilo(nome: str, tipo: str, valor: str, main_window) -> None:
    """
    tipo='style'  -> aplica o estilo interno 'valor' via viewport.style_override
    tipo='toggle' -> alterna o flag booleano 'valor' no estilo efetivo

    ⚠️ FRÁGIL: usa `viewport.style_override` (atributo Qt, não é API de
    extensão). Em IngeTrazo 0.x funciona; se virar 1.x, é provável que
    apareça uma API pública (`app.viewport.set_style(...)`). Basta
    trocar aqui.
    """
    import core.style   # ⚠️ FRÁGIL: módulo `core` (semi-público)

    viewport = getattr(main_window, "viewport", None)
    if viewport is None:
        _log("viewport indisponível")
        return

    try:
        if tipo == "style":
            style = core.style.style_by_name(valor)
            if style is None:
                _log(f"estilo '{valor}' não encontrado em core.style")
                return
            # Aplica o estilo via atributo do viewport.
            # Reatribuir (em vez de mutar) é o que força o redesenho.
            viewport.style_override = style
            _log(f"estilo aplicado: {valor}")

        elif tipo == "toggle":
            import copy
            # Base: o override atual (se houver) ou o estilo Default
            base = getattr(viewport, "style_override", None) \
                   or core.style.style_by_name("Default")
            if base is None:
                _log("não foi possível obter um estilo base para o toggle")
                return

            # Style é um @dataclass → cópia rasa basta. Mutar o objeto
            # original diretamente não dispara repaint (cache interno).
            novo = copy.copy(base)
            valor_atual = bool(getattr(base, valor, False))
            setattr(novo, valor, not valor_atual)
            viewport.style_override = novo
            _log(f"flag '{valor}': {valor_atual} → {getattr(novo, valor)}")

        # Pede redesenho
        if hasattr(viewport, "update"):
            viewport.update()

        # Atualiza a dica de status, se a MainWindow expuser
        if hasattr(main_window, "status_hint"):
            try:
                main_window.status_hint = f"Styles: {nome}"
            except Exception:
                pass

    except Exception:
        traceback.print_exc()


# --- Criação da toolbar ---------------------------------------------------
_TOOLBAR_CRIADA = False

def _criar_toolbar_style(main_window) -> None:
    """
    Cria a barra "Styles".

    ⚠️ FRÁGIL: `QToolBar` + `main_window.addToolBar(...)` são API do Qt,
    não da extensão. O `docs/plugins.md` recomenda `app.add_panel(...)`
    ou `app.add_menu_action(...)`. Uma toolbar horizontal como esta não
    tem equivalente oficial na API 0.x; o comportamento aqui é
    equivalente ao das barras nativas (Shadows, Styles, etc.) e por
    isso é funcional — mas fica fora do caminho documentado.
    """
    global _TOOLBAR_CRIADA
    if _TOOLBAR_CRIADA:
        _log("toolbar já criada — ignorando")
        return

    if main_window is None or not hasattr(main_window, "addToolBar"):
        _log("toolbar não criada: MainWindow indisponível")
        return

    try:
        tb = QToolBar("Styles", main_window)
        tb.setObjectName("igz_tb_style")
        tb.setWindowTitle("Styles")
        main_window.addToolBar(Qt.TopToolBarArea, tb)

        for nome, arquivo, dica, tipo, valor in ACOES_STYLE:
            icon = QIcon()
            if _ICONS_DIR:
                p = os.path.join(_ICONS_DIR, arquivo)
                if os.path.isfile(p):
                    icon = QIcon(p)
                else:
                    _log(f"ícone não encontrado: {p}")

            a = QAction(icon, nome, main_window)
            a.setToolTip(dica)
            a.setStatusTip(dica)
            a.triggered.connect(
                lambda _=False, n=nome, t=tipo, v=valor:
                    _aplicar_estilo(n, t, v, main_window)
            )
            tb.addAction(a)

        # Faz a barra acoplada respeitar o tamanho do conteúdo
        # (senão o Qt estica a barra para preencher a linha inteira).
        tb.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        tb.setMaximumWidth(tb.sizeHint().width())

        _TOOLBAR_CRIADA = True
        _log("toolbar 'Styles' criada")
    except Exception:
        traceback.print_exc()


# --- setup() — ponto de entrada -------------------------------------------
def setup(app):
    """
    Ponto de entrada chamado UMA vez pelo IngeTrazo, quando a janela
    principal já existe. Ver `docs/plugins.md` §"Beyond tools: setup(app)".

    Este plugin NÃO define subclasse de `Tool`, portanto não aparece no
    menu Extensions nem tem atalho. Para adicionar isso, ver README.md.
    """
    print(f"[igz_tb_style] setup(app) — PID={os.getpid()}",
          file=sys.stderr, flush=True)
    _log(f"app: {type(app).__module__}.{type(app).__name__}")

    try:
        main_window = _descobrir_main_window()
        if main_window is None:
            main_window = getattr(app, "main_window", None) \
                          or getattr(app, "window", None)

        if main_window is None:
            QMessageBox.warning(
                None, "Styles",
                "Não foi possível localizar a janela principal do IngeTrazo."
            )
            return

        _criar_toolbar_style(main_window)
    except Exception:
        traceback.print_exc()