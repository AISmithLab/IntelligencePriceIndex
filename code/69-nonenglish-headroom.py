#!/usr/bin/env python3
"""
Step 69: Does step 04's English-only keyword list hide non-English listings?

Step 67 shows translation is the thinnest collected category and step 68's leakage
table gives it nothing back. Both step-04 keyword lists are English stems, so a
listing worded `traducir-del-espanol-al-ingles` or `escribir-articulos` matches
nothing and lands in `uncategorized`. This measures that, over DISTINCT gigs.

Input:  data/cdx-index/gig-pages-classified.tsv
Output: runs/uncollected-headroom/nonenglish.md
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gigfilter import is_gig

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT = BASE_DIR / "data" / "cdx-index" / "gig-pages-classified.tsv"
OUTDIR = BASE_DIR / "runs" / "uncollected-headroom"

# Non-English stems, mapped to the collected domain the listing belongs to.
# Spanish / Portuguese / French / Italian / German / Indonesian — the languages
# that actually show up in Fiverr slugs.
NONENG = {
    "translation": ["traducir", "traduc", "traduzir", "traduzione", "traduire",
                    "ubersetz", "uebersetz", "terjemah", "vertaal", "tradutor",
                    "traductor", "interprete", "sottotitol", "subtitul", "legenda"],
    "writing": ["escribir", "redactar", "redaccion", "articulo", "articulos",
                "escrever", "redigir", "ecrire", "rediger", "schreiben",
                "texto", "textos", "contenido", "conteudo", "guion", "roteiro",
                "corregir", "revisar", "menulis"],
    "design": ["diseno", "disenar", "disenare", "logotipo", "grafico", "grafica",
               "ilustracion", "ilustrar", "desenho", "desenhar", "dibujo",
               "dibujar", "disegno", "gestalten", "portada", "capa-de",
               "tarjeta", "folleto", "cartel", "desain"],
    "video": ["editar-tu-video", "editar-video", "editar-videos", "edicion-de-video",
              "montaje", "animacion", "animacao", "video-editar", "videos-en",
              "edicao-de-video", "montagem"],
    "audio": ["locucion", "locutor", "voz-en-off", "voz-", "narracion", "musica",
              "cancion", "cantar", "grabar", "gravar", "mezcla", "mixagem",
              "sprecher", "stimme"],
    "marketing": ["publicidad", "marketing-digital", "redes-sociales", "seguidores",
                  "posicionamiento", "divulgacao", "publicacion", "campana",
                  "anuncio", "anuncios", "vendas"],
    "coding": ["programar", "programacao", "pagina-web", "paginas-web", "sitio-web",
               "site-em", "desarrollar", "desarrollo", "desenvolver", "aplicacion",
               "aplicativo", "programmieren", "webseite"],
}


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    seen = set()
    hits = Counter()
    samples = {k: [] for k in NONENG}
    total_uncat = 0
    scanned = 0

    with open(INPUT, encoding="utf-8", errors="replace") as f:
        next(f)
        for line in f:
            scanned += 1
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 7 or parts[6] != "uncategorized":
                continue
            url = parts[2]
            if not is_gig(url):
                continue
            gid = url.split("fiverr.com/", 1)[-1].split("?")[0].strip("/")
            if gid in seen:
                continue
            seen.add(gid)
            total_uncat += 1
            slug = gid.lower()
            for cat, stems in NONENG.items():
                if any(s in slug for s in stems):
                    hits[cat] += 1
                    if len(samples[cat]) < 4:
                        samples[cat].append(gid)
                    break

    # what each collected label already holds, for the "vs." column
    lines = []
    lines.append("# Non-English listings step 04's English-only keywords miss\n")
    lines.append(f"Distinct `uncategorized` gigs scanned: **{total_uncat:,}** "
                 f"({scanned:,} index rows).\n")
    lines.append("First-match assignment, so each gig counts once.\n")
    lines.append("| collected domain | non-English gigs recoverable |")
    lines.append("|---|---:|")
    for cat, n in hits.most_common():
        lines.append(f"| {cat} | {n:,} |")
    lines.append(f"| **total** | **{sum(hits.values()):,}** |")
    lines.append("")
    lines.append("## Samples\n")
    for cat in hits:
        for s in samples[cat]:
            lines.append(f"- `{cat}` — `{s}`")
    out = "\n".join(lines) + "\n"
    (OUTDIR / "nonenglish.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
