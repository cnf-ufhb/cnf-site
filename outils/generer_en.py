#!/usr/bin/env python3
"""Génère la version anglaise du site (public/en/index.html).

La page française public/index.html sert de modèle unique : la version
anglaise reprend exactement la même mise en page, avec les textes de
traductions/en.json. La section Actualités reste en français (seul son
titre est traduit, avec une mention « published in French »).

À lancer après chaque modification de la page française :
    python3 outils/generer_en.py
Le script s'arrête si un texte à traduire n'est plus trouvé dans la page
française (texte modifié) : il faut alors mettre à jour traductions/en.json.
"""
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "public" / "index.html"
CIBLE = RACINE / "public" / "en" / "index.html"
TRADUCTIONS = RACINE / "traductions" / "en.json"

DEBUT = "<!-- ACTUALITES:DEBUT"
FIN = "<!-- ACTUALITES:FIN -->"


def motif(texte):
    """Recherche tolérante aux retours à la ligne et espaces multiples."""
    morceaux = [re.escape(m) for m in texte.split()]
    return re.compile(r"\s+".join(morceaux))


def traduire(html, paires, erreurs):
    # Les textes les plus longs d'abord, pour qu'un texte court ne remplace
    # pas un morceau d'un texte plus long.
    for fr, en in sorted(paires, key=lambda p: -len(p[0])):
        html, n = motif(fr).subn(lambda _m: en, html)
        if n == 0:
            erreurs.append(fr)
    return html


def main():
    fr = SOURCE.read_text(encoding="utf-8")
    donnees = json.loads(TRADUCTIONS.read_text(encoding="utf-8"))

    entete_actus = [(p["fr"], p["en"]) for p in donnees["actualites_entete"]]
    paires = [
        (p["fr"], p["en"])
        for cle, liste in donnees.items()
        if cle not in ("_lisez-moi", "actualites_entete")
        for p in liste
    ]

    i, j = fr.find(DEBUT), fr.find(FIN)
    if i < 0 or j < 0:
        sys.exit("Repères ACTUALITES:DEBUT / ACTUALITES:FIN introuvables dans public/index.html")
    avant, actus, apres = fr[:i], fr[i:j], fr[j:]

    erreurs = []
    reste = traduire(avant + "\x00" + apres, paires, erreurs)
    actus = traduire(actus, entete_actus, erreurs)
    if erreurs:
        print("Textes introuvables dans la page française (mettre à jour traductions/en.json) :")
        for e in erreurs:
            print("  -", e[:110])
        sys.exit(1)

    avant, apres = reste.split("\x00")
    en = avant + actus + apres
    en = en.replace(
        "<!DOCTYPE html>",
        "<!DOCTYPE html>\n<!-- FICHIER GÉNÉRÉ par outils/generer_en.py : ne pas modifier à la main. -->",
        1,
    )
    CIBLE.parent.mkdir(parents=True, exist_ok=True)
    CIBLE.write_text(en, encoding="utf-8")
    print(f"Version anglaise générée : {CIBLE.relative_to(RACINE)} ({len(paires) + len(entete_actus)} textes)")


if __name__ == "__main__":
    main()
