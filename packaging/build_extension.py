#!/usr/bin/env python3
# =========================================================================
# Copyright (C) 2026 Ezequiel M. Rezende
# License: GPL-3.0-or-later (same as IngeTrazo)
# =========================================================================
# Build the distributable ``igz_toolbars.zip`` for the IngeTrazo extension
# catalog (https://github.com/ingelibre/ingetrazo-extensions).
#
# The catalog installs ONE file per entry: a .py file, or a .zip holding a
# single folder with an __init__.py (see TEMPLATE.toml in that repository).
# This extension needs the zip form because it ships two modules plus a
# folder of SVG icons.
#
# The archive is built deterministically on purpose: fixed timestamps,
# sorted entries and a fixed create-system, so its SHA-256 changes ONLY
# when the content changes. That is what lets the catalog fingerprint
# (``sha256`` in ``extensions/<id>.toml``) be verified and reproduced.
#
# Usage:
#     python packaging/build_extension.py
#
# Output:
#     dist/igz_toolbars.zip
#     dist/igz_toolbars.zip.sha256   (the value to paste in the catalog entry)
#
# The printed SHA-256 is what goes into ``extensions/igz_toolbars.toml``;
# upload the very same dist/igz_toolbars.zip as a GitHub Release asset of
# the tag named in the entry's ``download`` URL.
# =========================================================================
from __future__ import annotations

import hashlib
import os
import re
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIST = os.path.join(ROOT, "dist")

#: Single top-level folder inside the zip (required by the catalog).
PACKAGE = "igz_toolbars"
ZIP_NAME = f"{PACKAGE}.zip"

#: Modules copied verbatim from the repository root.
MODULES = ["igz_tb_style.py", "igz_tb_shadows.py"]

#: Documentation bundled inside the package (optional but tidy).
EXTRA_FILES = ["LICENSE", "README.md", "README_ptBR.md", "THIRD-PARTY.md"]

#: The package entry point (defines setup(app)); lives in the repo, not the
#: root, so the repository root stays a valid manual-install layout.
INIT_SRC = os.path.join(HERE, PACKAGE, "__init__.py")

#: Icons folder in the repository root.
ICONS_DIR = os.path.join(ROOT, "icons")

#: Fixed timestamp so the archive is byte-for-byte reproducible.
FIXED_DATE = (2026, 1, 1, 0, 0, 0)


def read_version() -> str:
    """Read the version from the module header, so it never drifts."""
    with open(os.path.join(ROOT, "igz_tb_style.py"), encoding="utf-8") as fh:
        for line in fh:
            match = re.match(r"#\s*Version:\s*(\S+)", line)
            if match:
                return match.group(1)
    return "0.0.0"


def _read(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def collect_entries() -> list[tuple[str, bytes]]:
    """Return ``(arcname, data)`` for every file, sorted by name."""
    entries: list[tuple[str, bytes]] = []

    entries.append((f"{PACKAGE}/__init__.py", _read(INIT_SRC)))

    for name in MODULES:
        entries.append((f"{PACKAGE}/{name}", _read(os.path.join(ROOT, name))))

    for name in EXTRA_FILES:
        path = os.path.join(ROOT, name)
        if os.path.isfile(path):
            entries.append((f"{PACKAGE}/{name}", _read(path)))

    if os.path.isdir(ICONS_DIR):
        for name in sorted(os.listdir(ICONS_DIR)):
            path = os.path.join(ICONS_DIR, name)
            if os.path.isfile(path) and name.lower().endswith(".svg"):
                entries.append((f"{PACKAGE}/icons/{name}", _read(path)))

    entries.sort(key=lambda item: item[0])
    return entries


def build() -> str:
    os.makedirs(DIST, exist_ok=True)
    out_zip = os.path.join(DIST, ZIP_NAME)

    with zipfile.ZipFile(out_zip, "w") as zf:
        for arcname, data in collect_entries():
            info = zipfile.ZipInfo(arcname, date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3          # 3 = Unix: stable across OSes
            info.external_attr = 0o644 << 16
            zf.writestr(info, data)

    digest = hashlib.sha256(_read(out_zip)).hexdigest()

    with open(out_zip + ".sha256", "w", encoding="ascii") as fh:
        fh.write(f"{digest}  {ZIP_NAME}\n")

    return digest


def main() -> None:
    version = read_version()
    digest = build()
    print(f"igz_toolbars {version}")
    print(f"  dist/{ZIP_NAME}")
    print(f"  sha256 = \"{digest}\"")
    print("")
    print("  Paste that sha256 into extensions/igz_toolbars.toml and upload")
    print(f"  dist/{ZIP_NAME} to the GitHub Release of the tag in `download`.")


if __name__ == "__main__":
    main()
