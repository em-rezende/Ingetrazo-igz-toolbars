# =========================================================================
# Copyright (C) 2026 Ezequiel M. Rezende
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
# =========================================================================
# Extension: igz_toolbars — package entry point
# Author: Ezequiel M. Rezende
# Version: 1.5.0
# Date: 2026-10-01
# License: GPL-3.0-or-later (same as IngeTrazo)
#
# IngeTrazo — "Styles" and "Shadows" toolbars.
#
# The IngeTrazo extension catalog installs ONE file per entry: a .py file,
# or a .zip holding a single folder with an __init__.py. This package is
# the zip form, because the extension ships two modules plus a folder of
# SVG icons:
#
#   • igz_tb_style.py    — "Styles" toolbar (13 buttons that mirror the
#                          native Camera ▸ Style menu).
#   • igz_tb_shadows.py  — "Shadows" toolbar (toggle + date/time/intensity
#                          sliders).
#   • icons/             — SVG icons for both toolbars.
#
# Both modules are written as standalone single-file plugins: each exposes
# its own `setup(app)`. This __init__.py loads them by file path (so it
# works whether IngeTrazo imports the package or the file directly, without
# relying on sys.path) and calls both `setup(app)` functions in turn.
# =========================================================================
from __future__ import annotations

import importlib.util
import os
import sys
import traceback

_HERE = os.path.dirname(os.path.abspath(__file__))

_DEBUG = True


def _log(msg: str) -> None:
    if _DEBUG:
        print(f"[igz_toolbars] {msg}", file=sys.stderr, flush=True)


def _load_module(module_name: str):
    """Load a sibling .py file by path.

    Importing by path (instead of a relative import) keeps this package
    working however IngeTrazo discovers it — the docs warn plugins must not
    assume the plugin folder is on ``sys.path`` nor that they are importable
    by package name."""
    path = os.path.join(_HERE, f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(
        f"igz_toolbars_{module_name}", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# Loaded once, at import time, just like a single-file plugin would be.
try:
    _STYLE = _load_module("igz_tb_style")
except Exception:
    _STYLE = None
    traceback.print_exc()

try:
    _SHADOWS = _load_module("igz_tb_shadows")
except Exception:
    _SHADOWS = None
    traceback.print_exc()


def setup(app) -> None:
    """Called once by IngeTrazo when the main window is built.

    See ``docs/plugins.md → setup(app)``. Builds both toolbars; a failure in
    one never stops the other (and never breaks IngeTrazo itself)."""
    _log(f"setup(app) — PID={os.getpid()}")
    for name, module in (("igz_tb_style", _STYLE),
                         ("igz_tb_shadows", _SHADOWS)):
        if module is None:
            _log(f"{name} failed to import at startup; skipped")
            continue
        try:
            module.setup(app)
        except Exception:
            _log(f"{name}.setup(app) raised; continuing with the rest")
            traceback.print_exc()
