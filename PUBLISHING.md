# Publicar no catálogo de Extensões do IngeTrazo

> **Status: v1.4.0 e v1.5.1 já publicadas no catálogo; v1.5.2 pronta para
> publicar.** A v1.5.2 é a versão das **três barras** — *Styles*, *Shadows* e
> *Map*. Este guia descreve os passos da publicação inicial e, na prática,
> como publicar cada atualização (ex.: a v1.5.2).

Este documento (PT) e a seção em inglês mais abaixo descrevem como publicar
esta extensão no catálogo <https://github.com/ingelibre/ingetrazo-extensions>
(mostrado em <https://ingetrazo.com/extensiones>).

---

## O que já está pronto

| Item | Onde | Observação |
|---|---|---|
| Código limpo | `igz_tb_style.py` (barra *Styles*), `igz_tb_shadows.py` (barras *Shadows* e *Map*) | Artefatos de citação (`[cite: 3]`) removidos; versões alinhadas em **1.5.2**. |
| Empacotador | `packaging/build_extension.ps1` (Windows) e `packaging/build_extension.py` (multi-plataforma) | Gera um `.zip` determinístico com **uma** pasta de topo `igz_tb_toolbar/`. |
| Ponto de entrada do pacote | `packaging/igz_tb_toolbar/__init__.py` | Define `setup(app)` e carrega os dois módulos por caminho de arquivo; é ele que cria as **três** barras. |
| Artefato | `dist/igz_tb_toolbar.zip` | Já construído. **sha256** = `bdd84b5c98bf500ac2bf2612764c0f729405bd232a1f81dc25e279e3ce49ed42`. |
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

4. **Crie a Release `v1.5.2`** em
   <https://github.com/em-rezende/Ingetrazo-igz-toolbars/releases/new> e
   **anexe `dist/igz_tb_toolbar.zip` como asset** (nome exatamente
   `igz_tb_toolbar.zip`). O endereço de download na ficha aponta para:
   `.../releases/download/v1.5.2/igz_tb_toolbar.zip`.

5. **Abra o pull request no repositório do catálogo** (sem Git, pelo
   navegador):
   - *Add file ▸ Create new file* → `extensions/igz_toolbars.toml`, cole o
     conteúdo de `ingetrazo-extensions-submission/extensions/igz_toolbars.toml`.
   - *Add file ▸ Upload files* → envie
     `ingetrazo-extensions-submission/screenshots/igz_toolbars.png` para
     `screenshots/`, com o nome `igz_toolbars.png` (o mesmo do campo
     `screenshot`).
   - **Propose changes ▸ Create pull request**.

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

Um robô revisa a ficha em ~1 minuto e um mantenedor aprova. Depois disso, a
página do catálogo se atualiza sozinha. A extensão aparece como
**«Comunidade»** até um mantenedor ler o arquivo exato (aí vira
**«Revisada»**).


---

## Detalhes que você pode querer ajustar

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

> **Status: v1.4.0 and v1.5.1 already published; v1.5.2 ready to publish.**
> v1.5.2 is the **three-toolbar** version — *Styles*, *Shadows* and *Map*.
> This guide also covers publishing each update (e.g. v1.5.2).

Everything needed is in place (clean code, a `.zip` builder, the entry file
and a screenshot). To publish, once you authorise it:

1. Commit locally (`git add -A; git commit -m "chore: release 1.5.2 ..."`).
2. (Only if the code changed) rebuild: `packaging\build_extension.ps1` and
   copy the printed `sha256` into the entry.
3. `git push origin main`, then `git tag v1.5.2` and `git push origin v1.5.2`.
4. Create the **v1.5.2** GitHub Release and attach `dist/igz_tb_toolbar.zip`
   as an asset named exactly `igz_tb_toolbar.zip`.
5. In <https://github.com/ingelibre/ingetrazo-extensions>, copy
   `ingetrazo-extensions-submission/extensions/igz_toolbars.toml` to
   `extensions/igz_toolbars.toml` and
   `ingetrazo-extensions-submission/screenshots/igz_toolbars.png` to
   `screenshots/igz_toolbars.png` (browser: *Add file ▸ Create new file* /
   *Upload files*), then **Create pull request**.
6. Fill in the PR template checklist and answer the prompts (the extension
   uses no network by itself — the *Map* toolbar only triggers IngeTrazo's own
   **Terreno** panel, which does the tile download — runs no external programs
   and deletes no files).

The **sha256** in the entry
(`bdd84b5c98bf500ac2bf2612764c0f729405bd232a1f81dc25e279e3ce49ed42`) is the
fingerprint of `dist/igz_tb_toolbar.zip` as built by the script. It **must**
match the uploaded asset; if you rebuild, update the value.
