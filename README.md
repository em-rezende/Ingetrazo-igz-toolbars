# IngeTrazo Extensions — "Styles" and "Shadows" Toolbars

Two toolbars for [IngeTrazo](https://github.com/ingelibre/ingetrazo),
inspired by SketchUp: one for **display styles**, one for **shadows**.

- **Author:** Ezequiel M. Rezende
- **Date:** 2026-10-01
- **Version:** 1.4.0
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
    ├── tb_default.svg            / tb_default_light.svg
    ├── tb_architectural.svg      / tb_architectural_light.svg
    ├── tb_shaded.svg             / tb_shaded_light.svg
    ├── tb_hiddenline.svg         / tb_hiddenline_light.svg
    ├── tb_monochrome.svg         / tb_monochrome_light.svg
    ├── tb_wireframe.svg          / tb_wireframe_light.svg
    ├── tb_xray.svg               / tb_xray_light.svg
    ├── tb_xraytoggle.svg         / tb_xraytoggle_light.svg
    ├── tb_edges.svg              / tb_edges_light.svg
    ├── tb_profiles.svg           / tb_profiles_light.svg
    ├── tb_backedges.svg          / tb_backedges_light.svg
    ├── tb_hiddenobjects.svg      / tb_hiddenobjects_light.svg
    ├── tb_hiddengeometry.svg     / tb_hiddengeometry_light.svg
    └── tb_shadowtoggle.svg       / tb_shadowtoggle_light.svg
```

---

## "Styles" Toolbar

Thirteen buttons that **mirror the native commands** of the
**Camera ▸ Style** menu. The toolbar does not reimplement any style
logic — it looks up the matching `QAction` in the main window and calls
`trigger()` on it, exactly as if the user had clicked the menu entry.

The labels below are IngeTrazo's **English source strings** — the same
keys its native menu passes to `tr()`. The buttons are shown translated
to whatever language IngeTrazo is in (see *Language* below), and each
button shows the same text as its native menu entry.

| Button (source)     | Type   |
|---------------------|--------|
| **Default**         | style  |
| **Architectural**   | style  |
| **Shaded**          | style  |
| **Hidden line**     | style  |
| **Monochrome**      | style  |
| **Wireframe**       | style  |
| **X-ray**           | style  |
| **Toggle X-ray**    | toggle |
| **Edges**           | toggle |
| **Profiles**        | toggle |
| **Back edges**      | toggle |
| **Hidden Objects**  | toggle |
| **Hidden Geometry** | toggle |

**Mechanism:** for each button, `_trigger_action()` searches the main
window for the native `QAction` whose label is that English source — in
any UI language, via `core.i18n.source_of` — and calls `trigger()` on it.
Nothing is mutated directly — the native command runs with all its usual
side effects (menu state, axes, redraw, etc.), so the toolbar and the
menu never fall out of sync.

> The toolbar order matches the menu order, with a separator inserted
> before the display toggles (*Toggle X-ray*, *Edges*, *Profiles*,
> *Back edges*) and another before the visibility toggles
> (*Hidden Objects*, *Hidden Geometry*).

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

Dragging any slider automatically turns shadows on (otherwise the
adjustments would not be visible).

---

## Icons & themes

Each button ships **two icon variants**, so the toolbar stays legible on
both dark and light interfaces:

- `tb_<name>.svg` — the default variant (used on dark themes).
- `tb_<name>_light.svg` — the light-theme variant.

At start-up, `_load_themed_icon()` inspects the `QPalette.Window` colour
of the main window. On a **light** UI it loads the `_light.svg` file when
it exists and otherwise falls back to the default icon; on a dark UI it
always uses the default one. No configuration is required — the icons
follow the application theme automatically.

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
| `QAction` lookup by label | `_find_action` / `_trigger_action` | Matches IngeTrazo's English source via `core.i18n`; only breaks if IngeTrazo renames that source string |
| `QToolBar` + `MainWindow.addToolBar(...)` | `_create_style_toolbar` | Outside the `app.add_panel` / `app.add_menu_action` API |

### Fragile points in `igz_tb_shadows.py`

| Symbol | Where | Why |
|---|---|---|
| `viewport.scene.shadows` | `_get_scene_shadows` | Internal chain; the scene is not on `app.scene` |
| `ShadowSettings.{enabled, month, day, hour, minute, darkness}` | various | Internal dataclass (`core.sun`) |
| `QToolBar` + `MainWindow.addToolBar(...)` | `_create_shadows_toolbar` | Same as above |
| Native `"Shadows"` action lookup | `_on_toggle` | Found by English source via `core.i18n`; only breaks if IngeTrazo renames it |

### What **is** compliant with `plugins.md`

- `.py` file in the correct plugins folder.
- Defines module-level `setup(app)`.
- Fault-tolerant: any exception inside the callbacks is caught and
  logged — the app keeps running.
- Does not modify the document without going through the command layer
  (the Styles toolbar delegates everything to the native commands; the
  Shadows toolbar only touches `scene.shadows`).
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

- **Styles toolbar:** the lookup matches IngeTrazo's English source
  strings through `core.i18n`, so translating the UI no longer breaks it.
  It would only break if IngeTrazo renamed the source string itself (then
  update `MENU_ACTIONS`); each miss is logged.
- **Shadows toolbar:** `viewport.scene.shadows` → check whether
  `app.scene` starts exposing the scene directly (the `plugins.md`
  mentions `app.scene` in the `setup` API).
- **Both:** `QToolBar` → if `app.add_toolbar(...)` appears, migrate.

---

## Language & internationalization

IngeTrazo's UI is translated with a lightweight JSON catalog
(`core/i18n.py`; English is the source language, catalogs live in
`i18n/<lang>.json`). The toolbars reuse it:

- **Native command names** (`Default`, `Edges`, `Shadows`, …) come straight
  from IngeTrazo's own catalog through `tr()`, so they always match what
  the **Camera ▸ Style** menu shows.
- **Our own strings** (toolbar titles, the `Date`/`Time`/`Int.` slider
  labels, the toggle tooltip and the error dialog) are not in IngeTrazo's
  catalog, so the plugin carries a small table for English, Spanish,
  Indonesian, Italian and Brazilian Portuguese; anything else falls back
  to English.
- **Switching language:** IngeTrazo's **Window ▸ Language** applies on the
  next start (it says so in a message). The toolbars follow the language
  at start-up, and a small timer also re-labels them the moment the
  language changes, without touching the rest of the UI.

You do **not** need to edit anything to pick up a language IngeTrazo
already ships: the command names come from its catalog. To translate the
plugin's own few strings into a new language, add its code to `_LOCAL`
(and, for the month abbreviations, `_LOCAL_MONTHS`) near the top of
`igz_tb_shadows.py` / `igz_tb_style.py`.

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
- Click any button to run the matching command from
  **Câmera ▸ Estilo** — the effect is exactly the same, and the menu
  state stays in sync.
- **Alternar raio-X**, **Arestas**, **Perfis**, and **Arestas de trás**
  are toggles: each click flips the corresponding native flag.

### Shadows
- Click the icon to **turn shadows on/off**.
- Drag the **Date** slider → the shadow rotates through the year.
- Drag the **Time** slider → the shadow rotates through the day.
- Drag the **Int.** slider → shadow gets lighter or darker.

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

4. ~~**Robust QAction lookup** for the Styles toolbar: use `objectName`
   instead of the visible `text()` so the toolbar survives UI language
   changes.~~ **Done** — the lookup now resolves IngeTrazo's English
   source through `core.i18n`, so it survives UI language changes.

5. **"Now" button** to reset date/time to the current moment.

6. **Expose `utc_offset`** in a combo box (the field exists in
   `ShadowSettings`).

---

## License

GPL-3.0-or-later — the same license as IngeTrazo.
Third-party notices are recorded in [THIRD-PARTY.md](THIRD-PARTY.md).

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
