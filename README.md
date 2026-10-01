# IngeTrazo Extensions — "Styles" and "Shadows" Toolbars

Two toolbars for [IngeTrazo](https://github.com/ingelibre/ingetrazo),
inspired by SketchUp: one for **display styles**, one for **shadows**.

- **Author:** Ezequiel M. Rezende
- **Date:** 2026-09-30
- **Version:** 1.0.0
- **License:** [GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.html)
  (same as IngeTrazo — see [LICENSE](https://github.com/ingelibre/ingetrazo/blob/main/LICENSE))

---

## Files

```
<plugins>/
├── igz_tb_style.py          # "Styles" toolbar
├── igz_tb_shadows.py        # "Shadows" toolbar
├── README.md                # this file
├── README_ptBR.md           # Portuguese version
├── LICENSE                  # full GPL-3.0 text
├── THIRD-PARTY.md           # third-party notices
└── icons/
    ├── tb_backedges.svg
    ├── tb_hiddenline.svg
    ├── tb_monochrome.svg
    ├── tb_pbr.svg
    ├── tb_shaded.svg
    ├── tb_textures.svg
    ├── tb_wireframe.svg
    ├── tb_xray.svg
    └── tb_shadowtoggle.svg
```

---

## "Styles" Toolbar

Eight buttons that apply IngeTrazo's built-in display styles to the viewport.

| Button          | Style applied               | Notes |
|-----------------|-----------------------------|-------|
| **Back Edges**  | *(toggle)* `back_edges`     | Toggles back edges on the current style |
| **Hidden Line** | `"Hidden line"`             | |
| **Monochrome**  | `"Monochrome"`              | |
| **PBR**         | `"Default"`                 | Approximation — IngeTrazo has no separate "PBR" style |
| **Shaded**      | `"Shaded"`                  | |
| **Textures**    | `"Architectural"`           | Textures on a white background |
| **Wireframe**   | `"Wireframe"`               | |
| **X-Ray**       | `"X-ray"`                   | |

**Mechanism:** `viewport.style_override = core.style.style_by_name("...")`.
Reassigning the attribute (instead of mutating the existing `Style` object)
is what forces a redraw — IngeTrazo's engine caches the style per frame.

---

## "Shadows" Toolbar

Three sliders plus a toggle, following the SketchUp model.

| Control | Field affected                      | Range |
|---------|-------------------------------------|-------|
| **Toggle** (icon) | `scene.shadows.enabled`     | on/off |
| **Date** | `scene.shadows.month` + `.day`      | 1–365 (day of year) |
| **Time** | `scene.shadows.hour` + `.minute`    | 0–1439 min |
| **Int.** | `scene.shadows.darkness`            | 0.0–1.0 |

**Mechanism:** change the fields on `scene.shadows` and call
`viewport.update()`. IngeTrazo's `paintGL` **re-reads `scene.shadows` every
frame** and recomputes the sun direction, regenerates the shadow map, and
redraws everything automatically. Nothing else needs to be touched.

> ⚠️ Earlier tests showed that setting `viewport._LIGHT`,
> `viewport._shadow_key`, or calling `viewport._ensure_shadow_map()` is
> **not necessary** and, in practice, does not change the shadow visually.
> The correct path is always through `scene.shadows` + `update()`.

---

## Compatibility with the IngeTrazo plugin API

IngeTrazo states in [`docs/plugins.md`](https://github.com/ingelibre/ingetrazo/blob/main/docs/plugins.md):

> The plugin API is **not stable yet** — expect breaking changes during
> the 0.x series.

Both extensions **work** in the current version (0.5.x), but they use a few
points that are **not part of the public extension API**. They are all
marked with `⚠️ FRAGILE` in the source code. Consolidated list:

### Fragile points in `igz_tb_style.py`

| Symbol | Where | Why |
|---|---|---|
| `viewport.style_override` | `_aplicar_estilo` | Qt attribute of the viewport; not part of the extension API |
| `core.style.style_by_name(...)` | `_aplicar_estilo` | `core` module (semi-public) |
| `QToolBar` + `MainWindow.addToolBar(...)` | `_criar_toolbar_style` | Outside the `app.add_panel` / `app.add_menu_action` API |

### Fragile points in `igz_tb_shadows.py`

| Symbol | Where | Why |
|---|---|---|
| `viewport.scene.shadows` | `_get_scene_shadows` | Internal chain; the scene is not on `app.scene` |
| `ShadowSettings.{enabled, month, day, hour, minute, darkness}` | various | Internal dataclass (`core.sun`) |
| `QToolBar` + `MainWindow.addToolBar(...)` | `_criar_toolbar_shadows` | Same as above |
| Literal text `"Sombras"` in the native QAction lookup | `_on_toggle` | Breaks if the UI is translated |

### What **is** compliant with `plugins.md`

- `.py` file in the correct plugins folder.
- Defines module-level `setup(app)`.
- Fault-tolerant: any exception inside the callbacks is caught and
  logged — the app keeps running.
- Does not modify the document without going through the command layer
  (in fact it does not touch geometry; only `scene.shadows`).
- Does not assume `sys.path` and does not import its own package.
- Respects threading (everything on the main thread).

### What is **not** covered by `plugins.md`

- Horizontal toolbars have **no official API** in the 0.x version. The
  document mentions `app.add_panel(...)` (side tab),
  `app.add_menu_action(...)` (menu entry), and `app.add_context_menu(...)`,
  but not `add_toolbar(...)`. These extensions use `QToolBar` **directly
  via PySide** — it works, but it is the "informal" path.
- There is no subclass of `tools.base.Tool`. This means the plugins
  **do not appear in the Extensions menu**, have no shortcut, and are not
  in the F3 search. If that is desired, see "Future improvements" below.
- No persistence via `app.document_data`. The shadow values already live
  inside `scene.shadows` (and are saved in the `.igz` as part of the
  document), but slider positions are **not** remembered.

### If the 0.x API breaks

- `viewport.style_override` → migrate to the future public style API
  (`app.viewport.set_style(...)` or similar), once it exists.
- `viewport.scene.shadows` → check whether `app.scene` starts exposing
  the scene directly (the `plugins.md` mentions `app.scene` in the
  `setup` API).
- `QToolBar` → if `app.add_toolbar(...)` appears, migrate.

---

## Installation

1. Locate IngeTrazo's plugins folder:
   - **Linux:** `~/.local/share/ingetrazo/plugins/`
   - **Windows:** `%APPDATA%\ingetrazo\plugins\`
   - Or use the **Extensions ▸ Open plugins folder** menu.
2. Copy `igz_tb_style.py`, `igz_tb_shadows.py`, `README.md`, and the
   `icons/` folder into it.
3. Restart IngeTrazo.

The **Styles** and **Shadows** toolbars appear in the top area.

---

## Usage

### Styles
- Click any button to switch the viewport style.
- **Back Edges** is a **toggle**: click it to toggle back edges on the
  current style.

### Shadows
- Click the icon to **turn shadows on/off**.
- Drag the **Date** slider → the shadow rotates through the year.
- Drag the **Time** slider → the shadow rotates through the day.
- Drag the **Int.** slider → shadow gets lighter or darker.

Dragging any slider automatically turns shadows on (otherwise the
adjustments would not be visible).

---

## Future improvements (optional)

Everything `plugins.md` recommends that is **not** implemented yet.
None of these improvements are required — the toolbars work fine
without them.

1. **`Tool` subclass** for each extension: "Styles…" and "Shadows…" in
   the Extensions menu, with shortcuts. Lets the user reopen the toolbar
   if it gets closed.

2. **Persistence in `app.document_data`**: store slider positions in the
   `.igz` so that reopening restores everything as it was.

3. **Migrate to `app.add_panel(...)`** for 100% compliance with the API.
   You lose the "horizontal toolbar" format but gain integration with
   the side tray (Window ▸ Panels).

4. **Internationalization** of the literal `"Sombras"` string used to
   sync with the native QAction. If the UI language changes, the sync
   stops — without breaking anything.

5. **"Now" button** to reset date/time to the current moment.

6. **Expose `utc_offset`** in a combo box (the field exists in
   `ShadowSettings`).

---

## License

GPL-3.0-or-later — the same license as IngeTrazo.
Third-party notices are recorded in [THIRD-PARTY.md](THIRD-PARTY.md), which also
preserves the MIT notice inherited from the project's first release.

See <https://www.gnu.org/licenses/gpl-3.0.html>.

Copyright (C) 2026 Ezequiel M. Rezende.

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License, version 3 or later,
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful, but
**without any warranty**; without even the implied warranty of
**merchantability** or **fitness for a particular purpose**. See the
GNU General Public License for more details.
```

---

### What changed vs. the Portuguese version

| Item | Change |
|---|---|
| All headings | Translated to English |
| Table headers | `Botão` → `Button`, `Estilo aplicado` → `Style applied`, `Observação` → `Notes` |
| Table headers (Shadows) | `Controle` → `Control`, `Campo afetado` → `Field affected`, `Faixa` → `Range` |
| Code comments | Kept as-is (they are in Portuguese inside the `.py` files) |
| Filenames | `README.md` (same as before) |
| Cross-references | `Arquivos` → `Files`, `Instalação` → `Installation`, `Uso` → `Usage` |
| Footer license text | Translated to the official GPL-3.0 English wording |
| All technical content | Unchanged — same tables, same warnings, same `⚠️ FRAGILE` markers |

The only thing I intentionally kept in Portuguese are the **code comments inside the `.py` files** themselves — those are part of the source code you already have. If you want, I can also translate the code comments to English for a fully internationalized release. Just say the word.
