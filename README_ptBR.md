# Extensões IngeTrazo — Barras "Styles" e "Shadows"

Duas barras de ferramenta para o [IngeTrazo](https://github.com/ingelibre/ingetrazo),
inspiradas no SketchUp: uma de **estilos de exibição** e outra de **sombras**.

- **Autor:** Ezequiel M. Rezende
- **Data:** 2026-09-30
- **Versão:** 1.0.0
- **Licença:** [GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.html)
  (mesma do IngeTrazo — ver [LICENSE](https://github.com/ingelibre/ingetrazo/blob/main/LICENSE))

---

## Arquivos

```
<plugins>/
├── igz_tb_style.py          # barra "Styles"
├── igz_tb_shadows.py        # barra "Shadows"
├── README.md                # este arquivo
├── README_ptBR.md           # esta versão em português
├── LICENSE                  # texto completo da GPL-3.0
├── THIRD-PARTY.md           # avisos de terceiros
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

## Barra "Styles"

Oito botões que aplicam os estilos internos do IngeTrazo ao viewport.

| Botão           | Estilo aplicado             | Observação |
|-----------------|-----------------------------|------------|
| **Back Edges**  | *(toggle)* `back_edges`     | Alterna arestas posteriores no estilo atual |
| **Hidden Line** | `"Hidden line"`             | |
| **Monochrome**  | `"Monochrome"`              | |
| **PBR**         | `"Default"`                 | Aproximação — o IngeTrazo não tem um estilo "PBR" separado |
| **Shaded**      | `"Shaded"`                  | |
| **Textures**    | `"Architectural"`           | Texturas em fundo branco |
| **Wireframe**   | `"Wireframe"`               | |
| **X-Ray**       | `"X-ray"`                   | |

**Mecanismo:** `viewport.style_override = core.style.style_by_name("...")`.
Reatribuir o atributo (em vez de mutar o objeto `Style` existente) é o que
força o redesenho — o motor do IngeTrazo faz cache do estilo por frame.

---

## Barra "Shadows"

Três sliders + um toggle, seguindo o modelo do SketchUp.

| Controle | Campo afetado                       | Faixa |
|----------|-------------------------------------|-------|
| **Toggle** (ícone) | `scene.shadows.enabled`     | on/off |
| **Data** | `scene.shadows.month` + `.day`      | 1–365 (dia do ano) |
| **Hora** | `scene.shadows.hour` + `.minute`    | 0–1439 min |
| **Int.** | `scene.shadows.darkness`            | 0.0–1.0 |

**Mecanismo:** mudar os campos de `scene.shadows` e chamar
`viewport.update()`. O `paintGL` do IngeTrazo **relê `scene.shadows` a
cada frame** e recalcula a direção do sol, regenera o shadow map e
redesenha tudo automaticamente. Nada mais precisa ser tocado.

> ⚠️ Testes anteriores mostraram que setar `viewport._LIGHT`,
> `viewport._shadow_key` ou chamar `viewport._ensure_shadow_map()` **não
> é necessário** e, na prática, não muda a sombra visualmente. O caminho
> correto é sempre via `scene.shadows` + `update()`.

---

## Compatibilidade com a API de plugins do IngeTrazo

O IngeTrazo declara em [`docs/plugins.md`](https://github.com/ingelibre/ingetrazo/blob/main/docs/plugins.md):

> The plugin API is **not stable yet** — expect breaking changes during
> the 0.x series.

As duas extensões **funcionam** na versão atual (0.5.x), mas usam alguns
pontos que **não fazem parte da API pública de extensão**. Estão todos
marcados com `⚠️ FRÁGIL` no código-fonte. Lista consolidada:

### Pontos frágeis em `igz_tb_style.py`

| Símbolo | Onde | Por quê |
|---|---|---|
| `viewport.style_override` | `_aplicar_estilo` | Atributo Qt do viewport; não é API de extensão |
| `core.style.style_by_name(...)` | `_aplicar_estilo` | Módulo `core` (semi-público) |
| `QToolBar` + `MainWindow.addToolBar(...)` | `_criar_toolbar_style` | Fora da API `app.add_panel` / `app.add_menu_action` |

### Pontos frágeis em `igz_tb_shadows.py`

| Símbolo | Onde | Por quê |
|---|---|---|
| `viewport.scene.shadows` | `_get_scene_shadows` | Cadeia interna; a cena não está em `app.scene` |
| `ShadowSettings.{enabled, month, day, hour, minute, darkness}` | várias | Dataclass interna (`core.sun`) |
| `QToolBar` + `MainWindow.addToolBar(...)` | `_criar_toolbar_shadows` | Idem acima |
| Texto literal `"Sombras"` na busca da QAction nativa | `_on_toggle` | Quebra se a UI for traduzida |

### O que **está** de acordo com o `plugins.md`

- Arquivo `.py` na pasta de plugins correta.
- Define `setup(app)` no nível do módulo.
- Tolerante a falhas: qualquer exceção dentro dos callbacks é capturada e
  logada — o app continua funcionando.
- Não mexe no documento sem passar pelo comando (na verdade não mexe em
  geometria; só em `scene.shadows`).
- Não assume `sys.path` nem importa o próprio pacote.
- Respeita threading (tudo na main thread).

### O que **não** está previsto pelo `plugins.md`

- Barras de ferramenta horizontais **não** têm API oficial na versão 0.x.
  O documento menciona `app.add_panel(...)` (aba lateral),
  `app.add_menu_action(...)` (item de menu) e `app.add_context_menu(...)`,
  mas não `add_toolbar(...)`. Estas extensões usam `QToolBar` **direto via
  PySide** — funciona, mas é o caminho "informal".
- Não há subclasse de `tools.base.Tool`. Isso significa que os plugins
  **não aparecem no menu Extensions**, não têm atalho e não entram na
  busca F3. Se isso for desejado, ver "Melhorias futuras" abaixo.
- Nenhuma persistência via `app.document_data`. Os valores de sombra já
  vivem dentro de `scene.shadows` (e são salvos no `.igz` como parte do
  documento), mas a posição dos sliders **não** é lembrada.

### Se a API 0.x quebrar

- `viewport.style_override` → migrar para a futura API pública de estilos
  (`app.viewport.set_style(...)` ou similar), quando existir.
- `viewport.scene.shadows` → verificar se `app.scene` passa a expor a
  cena diretamente (o `plugins.md` menciona `app.scene` na API `setup`).
- `QToolBar` → se aparecer `app.add_toolbar(...)`, migrar.

---

## Instalação

1. Localize a pasta de plugins do IngeTrazo:
   - **Linux:** `~/.local/share/ingetrazo/plugins/`
   - **Windows:** `%APPDATA%\ingetrazo\plugins\`
   - Ou use o menu **Extensões ▸ Abrir pasta de plugins**.
2. Copie `igz_tb_style.py`, `igz_tb_shadows.py`, `README.md` e a pasta
   `icons/` para lá.
3. Reinicie o IngeTrazo.

As barras **Styles** e **Shadows** aparecem na área superior.

---

## Uso

### Styles
- Clique em qualquer botão para trocar o estilo do viewport.
- **Back Edges** é um **toggle**: clique para alternar arestas
  posteriores no estilo atual.

### Shadows
- Clique no ícone para **ligar/desligar** sombras.
- Arraste o slider **Data** → a sombra gira ao longo do ano.
- Arraste o slider **Hora** → a sombra gira ao longo do dia.
- Arraste o slider **Int.** → sombra mais clara ou mais escura.

Ao arrastar qualquer slider, as sombras são ligadas automaticamente
(senão os ajustes não seriam visíveis).

---

## Melhorias futuras (opcional)

Tudo o que o `plugins.md` recomenda e que ainda **não** está implementado.
Nenhuma destas melhorias é necessária — as barras funcionam bem sem elas.

1. **`Tool` subclasse** para cada extensão: "Styles…" e "Shadows…" no menu
   Extensions, com atalhos. Permite que o usuário reabra a barra se ela
   for fechada.

2. **Persistência em `app.document_data`**: guardar as posições dos
   sliders no `.igz` para que, ao reabrir, tudo esteja como estava.

3. **Migrar para `app.add_panel(...)`** se quiser 100% de conformidade
   com a API. Perde-se o formato "barra horizontal", mas ganha-se
   integração com a bandeja lateral (Janela ▸ Painéis).

4. **Internacionalização** do texto `"Sombras"` na sincronização com a
   QAction nativa. Se a UI mudar de idioma, a sincronia para — sem
   quebrar nada.

5. **Botão "Agora"** para resetar data/hora ao momento atual.

6. **Expor `utc_offset`** em um combo (o campo existe em `ShadowSettings`).

---

## Licença

GPL-3.0-or-later — a mesma licença do IngeTrazo.
Avisos de terceiros ficam em [THIRD-PARTY.md](THIRD-PARTY.md), que também
preserva o aviso MIT herdado da primeira versão do projeto.

Ver <https://www.gnu.org/licenses/gpl-3.0.html>.

Copyright (C) 2026 Ezequiel M. Rezende.

Este programa é software livre: você pode redistribuí-lo e/ou modificá-lo
sob os termos da GNU General Public License, versão 3 ou posterior,
conforme publicada pela Free Software Foundation.

Este programa é distribuído na esperança de ser útil, mas **sem qualquer
garantia**; sem mesmo a garantia implícita de **comercialização** ou
**adequação a um propósito específico**. Veja a GNU General Public License
para mais detalhes.

