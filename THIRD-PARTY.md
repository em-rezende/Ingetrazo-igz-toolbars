# Third-Party Notices

This project is distributed under **GPL-3.0-or-later** — see [LICENSE](LICENSE).

This file records notices for material that was **not** authored by the
project author, as required by the original licenses.

---

## 1. Inherited MIT notice

An earlier revision of this repository shipped its `LICENSE` file as the
**MIT License**, naming two copyright holders:

    Copyright (c) 2015 Juergen Weichand
    Copyright (c) 2026 Ezequiel M Rezende

When the project license was changed to GPL-3.0-or-later, that `LICENSE` file
was replaced by the full GPL-3.0 text. The MIT License requires that its
copyright notice and permission notice be *retained* in all copies or
substantial portions of the software, so the notice is reproduced here in
full and preserved.

### MIT License (preserved verbatim)

```
MIT License

Copyright (c) 2015 Juergen Weichand
Copyright (c) 2026 Ezequiel M Rezende

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Scope of the MIT notice

> **Not yet confirmed by the author.** The specific files covered by the MIT
> notice above have not been formally identified.

Evidence gathered while auditing the repository:

| Artefact | Finding |
|---|---|
| `icons/*.svg` (9 files) | Original SVG exports from **CorelDRAW 2026** (`<!-- Creator: CorelDRAW 2026 -->` + Corel metadata layer, custom palette `#4B4B4D`/`#854220`/`#F37329`/`#FCC19F`). Edition sources live in the local `Desenvolvimento/*.cdr` folder. |
| Third-party markers in the SVGs | **None** — no Inkscape/FreeCAD/SketchUp metadata, no embedded author or license field. |
| `igz_tb_style.py`, `igz_tb_shadows.py` | Written for this project; headers declare `GPL-3.0-or-later`. |

Because the icon set carries no third-party provenance, it does **not** appear
to derive from Juergen Weichand's work. The MIT notice is therefore retained
defensively until the author confirms which file(s) — if any — originated from
that MIT-licensed source. If none did, this section can be dropped.

---

## 2. IngeTrazo

The toolbar API used here belongs to **IngeTrazo** by the IngeTrazo/Ingelibre
project — <https://github.com/ingelibre/ingetrazo> — also licensed
**GPL-3.0-or-later**. The GPL text in [LICENSE](LICENSE) is byte-identical to
the one IngeTrazo ships. No IngeTrazo source code is vendored in this
repository; the plugins only call its runtime API at load time.

---

# Avisos de Terceiros

Este projeto é distribuído sob **GPL-3.0-or-later** — veja [LICENSE](LICENSE).

Este arquivo registra avisos de material que **não** foi criado pelo autor do
projeto, conforme exigido pelas licenças originais.

## 1. Aviso MIT herdado

Uma revisão anterior deste repositório trazia o `LICENSE` como **Licença
MIT**, nomeando `Copyright (c) 2015 Juergen Weichand` e
`Copyright (c) 2026 Ezequiel M Rezende`. Ao migrar o projeto para
GPL-3.0-or-later, esse arquivo foi substituído pelo texto completo da GPL-3.0.
Como a Licença MIT exige que o aviso de copyright e o aviso de permissão sejam
**preservados** em cópias ou porções substanciais do software, o texto MIT
original está reproduzido integralmente acima, na seção em inglês.

**Escopo ainda não confirmado pelo autor:** os arquivos abrangidos por esse
aviso MIT ainda não foram identificados. Os ícones em `icons/*.svg` são
trabalhos originais exportados do **CorelDRAW 2026** (fontes em
`Desenvolvimento/*.cdr`) e não contêm metadados de terceiros — portanto **não
parecem** derivar do trabalho de Juergen Weichand. O aviso MIT é mantido por
segurança até a confirmação do autor; se nenhum arquivo vier daquela fonte,
esta seção pode ser removida.

## 2. IngeTrazo

A API de barras de ferramenta usada aqui pertence ao **IngeTrazo**, do projeto
Ingetrazo/Ingelibre — <https://github.com/ingelibre/ingetrazo> — também sob
**GPL-3.0-or-later**. Nenhum código-fonte do IngeTrazo é incorporado a este
repositório; os plugins apenas chamam a API em tempo de execução.
