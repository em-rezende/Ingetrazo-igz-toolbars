# Submission bundle — IngeTrazo extension catalog

> **Not published yet.** Nothing here has been sent anywhere; these are the
> files to copy into a pull request of
> <https://github.com/ingelibre/ingetrazo-extensions> once you authorise it.

Copy these two things into the catalog repository:

| From here | To the catalog repository |
|---|---|
| `extensions/igz_toolbars.toml` | `extensions/igz_toolbars.toml` |
| `screenshots/igz_toolbars.png` | `screenshots/igz_toolbars.png` |

Then open the pull request (browser: *Add file ▸ Create new file* and *Add
file ▸ Upload files* → **Propose changes** → **Create pull request**) and fill
in the template checklist.

## Before you submit

- The `download` URL points at the **v1.4.0** GitHub Release asset
  `igz_toolbars.zip`, so create that tag/release in this repository first and
  upload `dist/igz_toolbars.zip` as the asset with that exact name.
- The `sha256` in the entry must match that asset byte-for-byte:
  `b495e6c05d5a9010bf4e32201e9409ededa4d183c09704a83f23af5fc734b4b8`.
  Rebuild with `packaging/build_extension.ps1` (or
  `packaging/build_extension.py`) if the code changed, and paste the value it
  prints. (If it is wrong, the catalog's automatic check tells you the right
  one.)

Full, step-by-step instructions are in [`../PUBLISHING.md`](../PUBLISHING.md).
