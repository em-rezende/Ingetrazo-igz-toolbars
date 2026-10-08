# Submission bundle — IngeTrazo extension catalog

> **Update bundle for the IngeTrazo extension catalog.** The catalog on `main`
> published v1.4.0 and then 1.5.0; the 1.5.1 pull request
> (<https://github.com/ingelibre/ingetrazo-extensions/pull/58>) is still open.
> These are the files to copy into a pull request of
> <https://github.com/ingelibre/ingetrazo-extensions> to publish v1.5.2 — the
> version with the **three** toolbars (*Styles*, *Shadows* and *Map*).

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

Full, step-by-step instructions are in [`../PUBLISHING.md`](../PUBLISHING.md).
