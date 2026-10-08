#!/usr/bin/env python3
"""Ajoute la fiche d'un chercheur dans la section « Notre équipe ».

Chaque chercheur est décrit dans un fichier fiches/<nom>.json (textes en
français et en anglais). Le script insère sa carte par ordre alphabétique
parmi les chercheurs (avant la Pr Emma Aké-Assi et la Directrice, qui
ferment la section) et ajoute ses traductions dans traductions/en.json.

    python3 outils/ajouter_chercheur.py fiches/akaffou.json
    python3 outils/generer_en.py

Format du fichier fiche :
{
  "nom": "Dr AKAFFOU Sopie Elvire Vanessa",      # tel qu'affiché
  "photo": "akaffou-sopie-elvire-vanessa.jpg",    # dans public/img/, ou null
  "initiales": "SA",                              # si pas de photo
  "grade": ["Chargée de recherche — Chercheure", "Research Fellow (Chargée de recherche)"],
  "labo": ["…", "…"],
  "specialites": [["Invasions biologiques", "Biological invasions"], …],
  "presentation": ["…", "…"],
  "publications": ["…", …],                       # non traduites
  "liens": [["ORCID", "https://orcid.org/…"], ["nom@exemple.ci", "mailto:nom@exemple.ci"]]
}
"""
import html
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PAGE = RACINE / "public" / "index.html"
TRADUCTIONS = RACINE / "traductions" / "en.json"
EXTERNE = ' target="_blank" rel="noopener"'


def cle_tri(nom):
    """« Dr AKAFFOU Sopie » → « akaffou sopie » (sans titre ni accents)."""
    nom = re.sub(r"^(Dr|Pr|Professeure?|M\.|Mme)\s+", "", nom)
    return nom.lower().translate(str.maketrans("éèêëàâîïôöûüç'", "eeeeaaiioouuc "))


def carte(f):
    if f.get("photo"):
        avatar = f'<img src="/img/{f["photo"]}" alt="{html.escape(f["nom"], quote=True)}" loading="lazy">'
    else:
        avatar = f'<div class="initiales" aria-hidden="true">{f["initiales"]}</div>'
    tags = "".join(f"<li>{fr}</li>" for fr, _ in f["specialites"])
    pubs = "".join(f"\n                <li>{p}</li>" for p in f["publications"])
    liens = "".join(
        f'<a href="{u}"{"" if u.startswith("mailto:") else EXTERNE}>{n}</a>' for n, u in f.get("liens", [])
    )
    bloc_pubs = (
        f"""
          <details>
            <summary>Publications principales</summary>
            <ul>{pubs}
            </ul>
          </details>"""
        if pubs
        else ""
    )
    bloc_liens = f'\n          <div class="liens">{liens}</div>' if liens else ""
    return f"""        <article class="cherch">
          <div class="cherch-top">
            {avatar}
            <div>
              <h3>{f["nom"]}</h3>
              <p class="grade">{f["grade"][0]}</p>
              <p class="labo">{f["labo"][0]}</p>
            </div>
          </div>
          <ul class="tags">{tags}</ul>
          <p class="bio">{f["presentation"][0]}</p>{bloc_pubs}{bloc_liens}
        </article>
"""


def main():
    f = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    page = PAGE.read_text(encoding="utf-8")
    if f"<h3>{f['nom']}</h3>" in page:
        sys.exit(f"{f['nom']} figure déjà sur la page.")

    debut = page.index('<div class="cherch-grid">')
    fin = page.index('<article class="directrice"', debut)
    cartes = [m.start() for m in re.finditer(r"        <article class=\"cherch\">", page[debut:fin])]
    position = None
    for c in cartes:
        titre = re.search(r"<h3>([^<]+)</h3>", page[debut + c :]).group(1)
        # Les chercheurs (« Dr … ») sont triés ; les professeures ferment la section.
        if not titre.startswith("Dr ") or cle_tri(titre) > cle_tri(f["nom"]):
            position = debut + c
            break
    if position is None:
        sys.exit("Emplacement introuvable dans la grille des chercheurs.")
    page = page[:position] + carte(f) + page[position:]
    PAGE.write_text(page, encoding="utf-8")

    trad = json.loads(TRADUCTIONS.read_text(encoding="utf-8"))
    existantes = {p["fr"] for liste in trad.values() if isinstance(liste, list) for p in liste}
    nouvelles = [
        (f'<p class="grade">{f["grade"][0]}</p>', f'<p class="grade">{f["grade"][1]}</p>'),
        (f'<p class="labo">{f["labo"][0]}</p>', f'<p class="labo">{f["labo"][1]}</p>'),
        (f["presentation"][0], f["presentation"][1]),
        *[(f"<li>{fr}</li>", f"<li>{en}</li>") for fr, en in f["specialites"]],
    ]
    if f.get("photo"):
        nom_en = f.get("nom_en", f["nom"])
        if nom_en != f["nom"]:
            nouvelles.append((f'alt="{f["nom"]}"', f'alt="{nom_en}"'))
    for fr, en in nouvelles:
        if fr not in existantes and fr != en:
            trad["chercheurs"].append({"fr": fr, "en": en})
            existantes.add(fr)
    pied = trad.pop("pied_de_page")
    trad["pied_de_page"] = pied
    TRADUCTIONS.write_text(json.dumps(trad, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Ajouté : {f['nom']}")


if __name__ == "__main__":
    main()
