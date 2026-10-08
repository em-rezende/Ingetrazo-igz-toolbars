# Submission bundle — IngeTrazo extension catalog

> **Bundle already published.** Pull request #58
> (<https://github.com/ingelibre/ingetrazo-extensions/pull/58>) carried these
> two files and was **merged automatically on 2026-10-08** (squash commit
> `91bafc9`), so the catalog's `main` — and the `catalog.json` read by
> <https://ingetrazo.com/extensiones> — already lists **igz_toolbars 1.5.2**,
> the version with the **three** toolbars (*Styles*, *Shadows* and *Map*). The
> copies here stay in sync for a future release; the extension shows as
> «Community» until a maintainer records its sha256 in `reviewed.toml`.

Copy these two things into the catalog repository:

| From here | To the catalog repository |
|---|---|
| `extensions/igz_toolbars.toml` | `extensions/igz_toolbars.toml` |
| `screenshots/igz_toolbars.png` | `screenshots/igz_toolbars.png` |

The screenshot shows the three toolbars on screen (950×674 px, ~65 KB) and
must keep the file name `igz_toolbars.png` — that is the name in the entry's
`screenshot` field.

Then open the pull request (browser: *Add file ▸ Create new file* and *Add
file ▸ Upload files* → **Propose changes** → **Create pull request**) and fill
in the template checklist.

## Before you submit

- The `download` URL points at the **v1.5.2** GitHub Release asset
  `igz_tb_toolbar.zip`, which is already published (68 553 bytes). Re-upload it
  with `packaging/publish_release.ps1` if the archive is ever rebuilt.
- The `sha256` in the entry must match that asset byte-for-byte:
  `bdd84b5c98bf500ac2bf2612764c0f729405bd232a1f81dc25e279e3ce49ed42`.
  Rebuild with `packaging/build_extension.ps1` (or
  `packaging/build_extension.py`) if the code changed, and paste the value it
  prints. (If it is wrong, the catalog's automatic check tells you the right
  one.)
- `version` is **1.5.2** and `tags` gained `terrain`, because the **Map**
  toolbar drives the **Terreno** (BaseMap) panel: tile source, project
  location and *Load map*.

## What the catalog's check demands

Every pull request runs `pytest -q tests` and `python tools/catalog.py check`.
Both refuse an entry that breaks any rule below (the offline tests catch all of
them except the download itself), so the lengths matter:

| Field | Rule |
|---|---|
| `name` | at most **60** characters per language |
| `summary` | at most **240** characters per language |
| `description` | optional, at most **2000** characters per language |
| `tags` | 1 to 4, from the catalog's fixed list (`terrain` is one of them) |
| `license` | SPDX id of a free licence (here `GPL-3.0-or-later`) |
| `download` | `https://`, ending in `.py` or `.zip`, naming a tag or a commit — never a branch |
| `sha256` | the 64-character hash of exactly that file |
| `screenshot` | a file name in `screenshots/`, at most 600 KB, `.png`/`.jpg`/`.webp` |

The archive itself must hold **one** package folder with an `__init__.py` inside
(here `igz_tb_toolbar/`), at most 5 MB on disk, and the code must expose a
top-level `setup(app)` function or a `Tool` subclass.

Full, step-by-step instructions are in [`../PUBLISHING.md`](../PUBLISHING.md).
