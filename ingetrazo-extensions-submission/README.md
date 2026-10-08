# Submission bundle — IngeTrazo extension catalog

> **Update bundle for the IngeTrazo extension catalog.** v1.4.0 is already
> published; these are the files to copy into a pull request of
> <https://github.com/ingelibre/ingetrazo-extensions> to publish v1.5.1.

Copy these two things into the catalog repository:

| From here | To the catalog repository |
|---|---|
| `extensions/igz_toolbars.toml` | `extensions/igz_toolbars.toml` |
| `screenshots/igz_toolbars.png` | `screenshots/igz_toolbars.png` |

Then open the pull request (browser: *Add file ▸ Create new file* and *Add
file ▸ Upload files* → **Propose changes** → **Create pull request**) and fill
in the template checklist.

## Before you submit

- The `download` URL points at the **v1.5.1** GitHub Release asset
  `igz_tb_toolbar.zip`, so create that tag/release in this repository first and
  upload `dist/igz_tb_toolbar.zip` as the asset with that exact name.
- The `sha256` in the entry must match that asset byte-for-byte:
  `ad3ffed2a2f9af276c7499afee35e98bc92fa8ae5811c4aead26687203cd3eee`.
  Rebuild with `packaging/build_extension.ps1` (or
  `packaging/build_extension.py`) if the code changed, and paste the value it
  prints. (If it is wrong, the catalog's automatic check tells you the right
  one.)

Full, step-by-step instructions are in [`../PUBLISHING.md`](../PUBLISHING.md).
