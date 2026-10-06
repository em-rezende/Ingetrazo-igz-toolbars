# Submission bundle — IngeTrazo extension catalog

> **Update bundle for the IngeTrazo extension catalog.** v1.4.0 is already
> published; these are the files to copy into a pull request of
> <https://github.com/ingelibre/ingetrazo-extensions> to publish the update.

Copy these two things into the catalog repository:

| From here | To the catalog repository |
|---|---|
| `extensions/igz_toolbars.toml` | `extensions/igz_toolbars.toml` |
| `screenshots/igz_toolbars.png` | `screenshots/igz_toolbars.png` |

Then open the pull request (browser: *Add file ▸ Create new file* and *Add
file ▸ Upload files* → **Propose changes** → **Create pull request**) and fill
in the template checklist.

## Before you submit

- The `download` URL points at the **v1.5.0** GitHub Release asset
  `igz_toolbars.zip`, so create that tag/release in this repository first and
  upload `dist/igz_toolbars.zip` as the asset with that exact name.
- The `sha256` in the entry must match that asset byte-for-byte:
  `854d0874dc68b04908e8b74f5d581574560dfb962bf645bf3a1624a1427904d4`.
  Rebuild with `packaging/build_extension.ps1` (or
  `packaging/build_extension.py`) if the code changed, and paste the value it
  prints. (If it is wrong, the catalog's automatic check tells you the right
  one.)

Full, step-by-step instructions are in [`../PUBLISHING.md`](../PUBLISHING.md).
