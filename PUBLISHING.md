# Publicar no catálogo de Extensões do IngeTrazo

> **Status: publicado.** A Release `v1.5.2` está no GitHub com o asset
> `igz_tb_toolbar.zip` verificado, e a ficha da **1.5.2** — a versão das **três
> barras** (*Styles*, *Shadows* e *Map*) — foi **mesclada no catálogo** pela PR
> #58 em 08/10/2026 (commit `91bafc9`): o `check` passou e o `automerge` fundiu
> a PR sozinho, sem revisão manual. A automação já reconstruiu o
> `catalog.json`, então a página do catálogo serve esta versão. A extensão
> aparece como **«Comunidade»** até um mantenedor ler o arquivo exato e
> registrar o sha256 em `reviewed.toml` — nada mais depende de você. Este guia
> descreve os passos da publicação inicial e, na prática, como publicar cada
> atualização.

Este documento (PT) e a seção em inglês mais abaixo descrevem como publicar
esta extensão no catálogo <https://github.com/ingelibre/ingetrazo-extensions>
(mostrado em <https://ingetrazo.com/extensiones>).

---

## O que já está pronto

| Item | Onde | Observação |
|---|---|---|
| Código limpo | `igz_tb_style.py` (barra *Styles*), `igz_tb_shadows.py` (barras *Shadows* e *Map*) | Artefatos de citação (`[cite: 3]`) removidos; versões alinhadas em **1.5.2**. |
| Empacotador | `packaging/build_extension.ps1` (Windows) e `packaging/build_extension.py` (multi-plataforma) | Gera um `.zip` determinístico com **uma** pasta de topo `igz_tb_toolbar/`. |
| Script da Release | `packaging/publish_release.ps1` | Cria/reaproveita a Release do GitHub, envia o asset e confere o `sha256` contra a ficha do catálogo (`-DryRun` só verifica). |
| Notas da Release | `packaging/release_notes/v1.5.2.md` | Texto publicado na Release `v1.5.2` (é o `-Notes` padrão do script para essa etiqueta). |
| Ponto de entrada do pacote | `packaging/igz_tb_toolbar/__init__.py` | Define `setup(app)` e carrega os dois módulos por caminho de arquivo; é ele que cria as **três** barras. |
| Artefato | `dist/igz_tb_toolbar.zip` | Já construído. **sha256** = `bdd84b5c98bf500ac2bf2612764c0f729405bd232a1f81dc25e279e3ce49ed42`. |
| Release publicada | <https://github.com/em-rezende/Ingetrazo-igz-toolbars/releases/tag/v1.5.2> | ID `406975286`, publicada em **08/10/2026**, asset `igz_tb_toolbar.zip` com **68 553 bytes** e o sha256 acima (conferido pelo campo `digest` da API e por download público anônimo). |
| Ficha do catálogo | `ingetrazo-extensions-submission/extensions/igz_toolbars.toml` | Copiar para `extensions/igz_toolbars.toml` no repositório do catálogo. |
| Captura de tela | `ingetrazo-extensions-submission/screenshots/igz_toolbars.png` | Copiar para `screenshots/igz_toolbars.png` no repositório do catálogo. |

O `.zip` contém exatamente uma pasta de topo:

```
igz_tb_toolbar/
├── __init__.py          # setup(app)
├── igz_tb_style.py
├── igz_tb_shadows.py
├── icons/*.svg
├── LICENSE
├── README.md
├── README_ptBR.md
└── THIRD-PARTY.md
```

O catálogo instala **um arquivo por extensão**: um `.py`, ou um `.zip` com
**uma** pasta contendo um `__init__.py` (ver `TEMPLATE.toml` no repositório do
catálogo). Por isso esta extensão, que traz dois módulos e uma pasta de ícones,
usa o formato `.zip`.

---

## Passos para publicar (quando autorizar)

Pré-requisitos atendidos: repositório público, licença livre
(GPL-3.0-or-later), e o arquivo baixado define `setup(app)`.

1. **Confirme as alterações locais e faça o commit.**
   ```powershell
   git add -A
   git commit -m "chore: release 1.5.2 with the Map toolbar for the IngeTrazo catalog"
   ```
   (Revise `git status` antes: a nova captura de tela em `screenshots/`,
   `packaging/` e `ingetrazo-extensions-submission/` ainda não rastreados.)

2. **(Opcional) Reconstrua o artefato** — só é preciso se você mudou o código:
   ```powershell
   powershell -ExecutionPolicy Bypass -File packaging\build_extension.ps1
   ```
   Anote o `sha256` impresso e atualize-o em
   `ingetrazo-extensions-submission/extensions/igz_toolbars.toml`.

3. **Envie o código para o GitHub e crie a etiqueta `v1.5.2`.**
   ```powershell
   git push origin main
   git tag v1.5.2
   git push origin v1.5.2
   ```

4. **Crie a Release `v1.5.2`** — ✔️ **já feita em 08/10/2026** (ID
   `406975286`), com `dist/igz_tb_toolbar.zip` anexado como asset
   `igz_tb_toolbar.zip`. O endereço de download na ficha aponta para:
   `.../releases/download/v1.5.2/igz_tb_toolbar.zip`.

   Na próxima versão, use o script em vez da tela do navegador: ele é
   **idempotente** (reaproveita a Release da etiqueta; numa etiqueta já
   publicada não mexe nem no texto nem num asset que já está correto) e confere
   o `sha256` no fim.
   ```powershell
   # só verifica o estado atual: não cria, não envia e não apaga nada
   powershell -ExecutionPolicy Bypass -File packaging\publish_release.ps1 `
       -Tag v1.5.2 -DryRun

   # publica de verdade (numa etiqueta já publicada isso não muda nada)
   powershell -ExecutionPolicy Bypass -File packaging\publish_release.ps1 `
       -Tag v1.5.2
   ```
   As notas saem de `packaging/release_notes/<etiqueta>.md` (a v1.5.2 em
   `packaging/release_notes/v1.5.2.md`, o mesmo texto que está na Release);
   `-Notes` troca o arquivo e `-Force` reenvia o asset mesmo quando ele já tem
   o sha256 esperado. O token vem do **Git Credential Manager** (usuário
   `em-rezende`), nunca é impresso, e sem `-ExpectedSha256` o script compara o
   asset com o `sha256` lido da ficha
   `ingetrazo-extensions-submission/extensions/igz_toolbars.toml`.

5. **Abra o pull request no repositório do catálogo** (sem Git, pelo
   navegador):
   - *Add file ▸ Create new file* → `extensions/igz_toolbars.toml`, cole o
     conteúdo de `ingetrazo-extensions-submission/extensions/igz_toolbars.toml`.
   - *Add file ▸ Upload files* → envie
     `ingetrazo-extensions-submission/screenshots/igz_toolbars.png` para
     `screenshots/`, com o nome `igz_toolbars.png` (o mesmo do campo
     `screenshot`).
   - **Propose changes ▸ Create pull request**.

   Se a **PR #58** (que levava a **1.5.1**) ainda estiver aberta, o caminho
   limpo é mandar esta atualização para o **mesmo branch** dela
   (`add-igz_toolbars-1.5.1` no fork `em-rezende/ingetrazo-extensions`) e
   trocar o título para v1.5.2, em vez de abrir uma segunda PR. ✅ **Foi assim
   que a 1.5.2 entrou:** a PR levava 1.5.1, o commit único foi alterado
   (`git commit --amend`) e o branch atualizado com
   `git push --force-with-lease origin add-igz_toolbars-1.5.1`; a ficha da
   versão antiga nunca chegou a ser publicada. Para a **próxima** versão, repita
   o truque enquanto uma PR sua estiver aberta.

6. **Responda o checklist** do template do PR:
   - [x] Um arquivo `extensions/igz_toolbars.toml`, copiado de `TEMPLATE.toml`.
   - [x] `download` aponta para uma **tag** (`v1.5.2`), não para uma branch.
   - [x] Testado com a versão do IngeTrazo em `ingetrazo` (**0.5.7**).
   - [x] A licença em `license` é a do código (GPL-3.0-or-later).
   - [x] `reviewed.toml` **não** foi tocado (só mantenedores).
   - Descreva no PR: usa PySide/Qt em memória; **não** acessa a rede por conta
     própria (a barra *Map* apenas aciona o painel **Terreno** nativo do
     IngeTrazo, que é quem baixa os tiles), **não** executa programas externos
     e **não** apaga arquivos.

Um robô revisa a ficha em ~1 minuto: o `check` roda `pytest -q tests` e
`python tools/catalog.py check` (ficha, download, `sha256` e captura) e, quando
nada falha, é o próprio `automerge` que faz o merge, sem esperar um mantenedor —
foi o que aconteceu com a PR #58 (merge em ~15 s). Em seguida o `publish`
reconstrói o `catalog.json` e a página do catálogo se atualiza sozinha. A
extensão aparece como **«Comunidade»** até um mantenedor ler o arquivo exato
(aí vira **«Revisada»**).


---

## Detalhes que você pode querer ajustar

- **Limites dos campos da ficha** (`name` ≤ 60, `summary` ≤ 240,
  `description` ≤ 2000 caracteres por idioma; 1–4 tags da lista fixa): a tabela
  completa, com o que o `pytest -q tests` do catálogo reprova, está em
  [`ingetrazo-extensions-submission/README.md`](ingetrazo-extensions-submission/README.md).
  Resumos longos vão em `[description]`, não em `[summary]` — foi um `summary`
  de 290 caracteres que travou o `check` da PR #58 antes do ajuste.
- **Versão do IngeTrazo** (`ingetrazo = "0.5.7"`): use a versão com que você
  realmente testou.
- **Tags** (`tags = [...]`): só são válidas `architecture`, `bim`,
  `structures`, `terrain`, `drawing`, `analysis`, `import-export`,
  `rendering`, `fabrication`, `productivity`, `education`, `other`.
- **Captura de tela**: a atual tem 950×674 px (~65 KB) e mostra as três
  barras (*Styles*, *Shadows* e *Map*) na janela do IngeTrazo. A sugestão do
  catálogo é ~1200×750 e o limite é 600 KB, então há espaço para uma imagem
  ainda maior.
- **Uma ficha por barra**: se preferir três extensões separadas, dá para
  publicar `igz_tb_style` (Styles), `igz_tb_shadows` (Shadows) e uma para a
  barra **Map** como entradas distintas — mas cada uma precisa do seu próprio
  arquivo baixável (e os ícones teriam de ir junto, novamente via `.zip`). O
  caminho combinado (atual) é mais simples.

---

# Publishing to the IngeTrazo extension catalog (EN)

> **Status: published.** The GitHub Release `v1.5.2` is live with a verified
> asset, and the **1.5.2** entry — the **three-toolbar** version (*Styles*,
> *Shadows* and *Map*) — was **merged into the catalog** by pull request #58 on
> 2026-10-08 (commit `91bafc9`): the automatic `check` passed and the
> `automerge` workflow merged it on its own, with no manual review. The
> automation has already rebuilt `catalog.json`, so the catalog page serves
> this version. The extension shows as **«Community»** until a maintainer reads
> the exact file and records its sha256 in `reviewed.toml` — nothing else is
> pending on your side.

Everything needed is in place (clean code, a `.zip` builder, the entry file
and a screenshot). To publish, once you authorise it:

1. Commit locally (`git add -A; git commit -m "chore: release 1.5.2 ..."`).
2. (Only if the code changed) rebuild: `packaging\build_extension.ps1` and
   copy the printed `sha256` into the entry.
3. `git push origin main`, then `git tag v1.5.2` and `git push origin v1.5.2`.
4. Create the **v1.5.2** GitHub Release and attach `dist/igz_tb_toolbar.zip`
   as an asset named exactly `igz_tb_toolbar.zip` — ✔️ **done on 2026-10-08**
   (release id `406975286`, 68 553 bytes, sha256 above). For the next version,
   prefer `packaging\publish_release.ps1` over the web UI:
   `-Tag v1.5.2` (the notes come from `packaging\release_notes\v1.5.2.md`),
   plus `-DryRun` for a read-only check and `-Force` to upload again an asset
   that is already in place. It is idempotent (reuses the release of that tag
   and rewrites the text only when it differs), reads the token from Git
   Credential Manager and verifies the sha256.
5. In <https://github.com/ingelibre/ingetrazo-extensions>, copy
   `ingetrazo-extensions-submission/extensions/igz_toolbars.toml` to
   `extensions/igz_toolbars.toml` and
   `ingetrazo-extensions-submission/screenshots/igz_toolbars.png` to
   `screenshots/igz_toolbars.png` (browser: *Add file ▸ Create new file* /
   *Upload files*), then **Create pull request**. ✔️ **Done on 2026-10-08** —
   it is pull request #58 (branch `add-igz_toolbars-1.5.1`, one commit), which
   passed `check` and was merged automatically by `automerge`; for the next
   version, reuse the same branch while that PR is still open instead of
   opening a second one.
6. Fill in the PR template checklist and answer the prompts (the extension
   uses no network by itself — the *Map* toolbar only triggers IngeTrazo's own
   **Terreno** panel, which does the tile download — runs no external programs
   and deletes no files).

The **sha256** in the entry
(`bdd84b5c98bf500ac2bf2612764c0f729405bd232a1f81dc25e279e3ce49ed42`) is the
fingerprint of `dist/igz_tb_toolbar.zip` as built by the script. It **must**
match the uploaded asset; if you rebuild, update the value.
