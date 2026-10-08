# IngeTrazo Extensions — "Styles" and "Shadows" Toolbars

Two toolbars for [IngeTrazo](https://github.com/ingelibre/ingetrazo),
inspired by SketchUp: one for **display styles**, one for **shadows**.

- **Author:** Ezequiel M. Rezende
- **Date:** 2026-10-01
- **Version:** 1.5.1
- **License:** [GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.html)
  (same as IngeTrazo — see [LICENSE](https://github.com/ingelibre/ingetrazo/blob/main/LICENSE))

---

![IngeTrazo with the "Styles" and "Shadows" toolbars on screen](screenshots/igz-toolbars-main.png)

*The **Styles** toolbar (thirteen style buttons) and the **Shadows**
toolbar (date, time, calendar, intensity, map source and location).*

---

## Files

```
<plugins>/
└── igz_tb_toolbar/
    ├── __init__.py              # package entry point (setup(app))
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

| Button (source)     | Type   | Icon | 
|---------------------|--------|----|
| **Default**         | style  | ![Default](icons/tb_default.svg) |
| **Architectural**   | style  | ![Architectural](icons/tb_architectural.svg) |
| **Shaded**          | style  | ![Shaded](icons/tb_shaded.svg) |
| **Hidden line**     | style  | ![Hidden line](icons/tb_hiddenline.svg) |
| **Monochrome**      | style  | ![Monochrome](icons/tb_monochrome.svg) |
| **Wireframe**       | style  | ![Wireframe](icons/tb_wireframe.svg) |
| **X-ray**           | style  | ![X-ray](icons/tb_xray.svg) |
| **Toggle X-ray**    | toggle | ![Toggle X-ray](icons/tb_xraytoggle.svg) |
| **Edges**           | toggle | ![Edges](icons/tb_edges.svg) |
| **Profiles**        | toggle | ![Profiles](icons/tb_profiles.svg) |
| **Back edges**      | toggle | ![Back edges](icons/tb_backedges.svg) |
| **Hidden Objects**  | toggle | ![Hidden Objects](icons/tb_hiddenobjects.svg) |
| **Hidden Geometry** | toggle | ![Hidden Geometry](icons/tb_hiddengeometry.svg) |

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

A toggle, two colour-coded sliders, a calendar button, an intensity
slider and a row of source/location controls, following the SketchUp model.

| Control | Field affected | Range |
|---------|----------------|-------|
| **Toggle** (icon) | `scene.shadows.enabled` | on/off |
| **Date** slider | `scene.shadows.month` + `.day` | 1–365 (day of year) |
| **Time** slider | `scene.shadows.hour` + `.minute` | 0–1439 min |
| **Calendar** (icon) | `scene.shadows.month`/`.day`/`.hour`/`.minute` | date + time dialog |
| **Int.** slider | `scene.shadows.darkness` | 0–100 (→ 0.0–1.0) |
| **Source** combo | Terreno panel map source | Esri / Sentinel-2 / OSM |
| **Location** row | `scene.shadows.latitude` + `.longitude` | coords + map picker |

Notes on the controls:

- **Date slider** — painted with a **seasonal gradient** (southern
  hemisphere: red summer → yellow winter) and showing the month initials
  (*J F M A M J J A S O N D*) underneath.
- **Time slider** — painted with a **day/night gradient** (dark-blue
  night → light day → dark-blue night) and showing the day's
  **sunrise**, **Noon** and **sunset** underneath.
- **Calendar button** — opens a dialog with a `QCalendarWidget` and a
  `QTimeEdit` to enter an exact date and time.
- **Source / Location / Load map** — integrate with IngeTrazo's
  **Terreno** (BaseMap) panel: choose the tile source, then type the
  project coordinates or use the map-picker button, which runs the
  panel's native *Search location* command. *Load map* keeps the fetched
  tiles; when it is off, the tiles are discarded once the coordinates are
  applied.

The **sunrise** and **sunset** marks are computed by an **internal solar
algorithm with no external dependencies** (*Almanac for Computers* /
USNO, ±2 min typical) from the scene's `latitude`, `longitude` and
`utc_offset` — so they update when the date or the location changes
(never when only the time slider moves).

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
| `ShadowSettings.{enabled, month, day, hour, minute, darkness, latitude, longitude, utc_offset}` | various | Internal dataclass (`core.sun`) |
| `BaseMapPanel` internals (`_source`, `_find`, `_lat`, `_lon`, `_last_sid`) | `_find_base_map_panel` / `_open_native_georef_dialog` | Reached through `findChildren`; the **Terreno** panel is not a public API |
| `scene.{tile_layer, terrain, photo_mesh}` snapshot | `_open_native_georef_dialog` | Internal scene attributes, restored when *Load map* is off |
| `QToolBar` + `MainWindow.addToolBar(...)` | `_create_shadows_toolbar` | Same as above |

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
  labels, `Location`, `Select Location`, `Calendar`, `Source`, `Load map`,
  `Noon`, the toggle tooltip and the error dialog) are not in IngeTrazo's
  catalog, so the plugin carries a small table for English, Spanish,
  Indonesian, Italian and Brazilian Portuguese; anything else falls back
  to English. The month abbreviations and the month initials under the
  date slider are localised the same way (`_LOCAL_MONTHS` /
  `_LOCAL_MONTH_LETTERS`).
- **Switching language:** IngeTrazo's **Window ▸ Language** applies on the
  next start (it says so in a message). The toolbars follow the language
  at start-up, and a small timer also re-labels them the moment the
  language changes, without touching the rest of the UI.

You do **not** need to edit anything to pick up a language IngeTrazo
already ships: the command names come from its catalog. To translate the
plugin's own few strings into a new language, add its code to `_LOCAL`
(and, for the month abbreviations/initials, `_LOCAL_MONTHS` and
`_LOCAL_MONTH_LETTERS`) near the top of `igz_tb_shadows.py` /
`igz_tb_style.py`.

---

## Installation

1. Locate IngeTrazo's plugins folder:
   - **Linux:** `~/.local/share/ingetrazo/plugins/`
   - **Windows:** `%APPDATA%\ingetrazo\plugins\`
   - Or use the **Extensions ▸ Open plugins folder** menu.
2. Unpack the **`igz_tb_toolbar`** folder — from the latest release ZIP, or
   from the `dist/igz_tb_toolbar.zip` you build with
   `packaging/build_extension.ps1` (it holds `__init__.py`, both modules,
   the docs and the `icons/` folder) — into that plugins folder, so the
   files end up at `<plugins>/igz_tb_toolbar/`.
3. Restart IngeTrazo.

The **Styles** and **Shadows** toolbars appear in the top area.

### From the IngeTrazo extension catalog

The extension is also packaged for the community catalog at
<https://ingetrazo.com/extensiones> (repository
<https://github.com/ingelibre/ingetrazo-extensions>), which installs a single
`.zip` holding one folder with an `__init__.py`. Build that archive with
`packaging/build_extension.ps1` (Windows) or `packaging/build_extension.py`
(any platform); it lands in `dist/igz_tb_toolbar.zip` and unpacks into
`<plugins>/igz_tb_toolbar/`. See
[`PUBLISHING.md`](PUBLISHING.md) for the release and submission steps.

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
- Drag the **Date** slider → the shadow rotates through the year (the
  month initials underneath mark the months; the track colour is a
  seasonal gradient).
- Drag the **Time** slider → the shadow rotates through the day (the
  track colour is a day/night gradient; the times underneath are that
  day's **sunrise**, **noon** and **sunset**).
- Click the **Calendar** button to pick an exact **date and time**.
- Drag the **Int.** slider → shadow gets lighter or darker.
- Choose a tile **Source** and set the **Location** (type the coordinates
  or use the map-picker button) to define the project's
  latitude/longitude; the sunrise/sunset marks follow. *Load map* keeps
  the fetched map tiles, otherwise they are discarded after the
  coordinates are applied.

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
