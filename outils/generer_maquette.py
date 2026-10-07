#!/usr/bin/env python3
"""Génère une maquette autonome du site bilingue (un seul fichier HTML).

Le fichier réunit les versions française et anglaise, avec les boutons
FR / EN fonctionnels et les photos intégrées : il s'ouvre par double-clic,
sans serveur. Destiné à être soumis au CNF pour validation.

    python3 outils/generer_en.py        (d'abord, pour mettre à jour l'anglais)
    python3 outils/generer_maquette.py
"""
import base64
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PUBLIC = RACINE / "public"
CIBLE = RACINE / "Documents_CNF" / "Maquette_Site_CNF_bilingue.html"

CSS = """<style>
  .bandeau-maquette{background:#7a1f1f; color:#fff; text-align:center; font-size:.88rem; padding:10px 16px; line-height:1.5;}
  .bandeau-maquette strong{letter-spacing:.06em;}
  #en-nav-toggle{display:none;}
  @media (max-width:820px){ #en-nav-toggle:checked ~ .nav ul{display:flex;} }
  [hidden]{display:none !important;}
</style>
"""

BANDEAU = """<div class="bandeau-maquette"><strong>MAQUETTE</strong> — Proposition de site bilingue français / anglais, soumise à validation du CNF. Cliquez sur <strong>FR</strong> / <strong>EN</strong> en haut à droite pour changer de langue. La rubrique Actualités reste en français dans les deux versions.</div>
"""

JS = """<script>
(function(){
  var fr=document.getElementById('version-fr'), en=document.getElementById('version-en');
  function choisir(l){ fr.hidden=(l!=='fr'); en.hidden=(l!=='en'); document.documentElement.lang=l; window.scrollTo(0,0); }
  document.querySelectorAll('[data-lang]').forEach(function(a){ a.addEventListener('click',function(e){ e.preventDefault(); choisir(a.getAttribute('data-lang')); }); });
  document.querySelectorAll('.nav a').forEach(function(a){ a.addEventListener('click',function(){ document.querySelectorAll('#nav-toggle,#en-nav-toggle').forEach(function(c){c.checked=false;}); }); });
})();
</script>
"""


def corps(html):
    return html[html.index("<body>") + 6 : html.index("<script>")]


def boutons_langue(html):
    return html.replace('href="/" lang="fr"', 'href="#" data-lang="fr" lang="fr"').replace(
        'href="/en/" lang="en"', 'href="#" data-lang="en" lang="en"'
    )


def integrer_images(html):
    def remplacer(m):
        chemin = PUBLIC / "img" / m.group(1)
        type_mime = "image/png" if chemin.suffix == ".png" else "image/jpeg"
        donnees = base64.b64encode(chemin.read_bytes()).decode()
        return f'src="data:{type_mime};base64,{donnees}"'

    return re.sub(r'src="/img/([^"]+)"', remplacer, html)


def main():
    fr = (PUBLIC / "index.html").read_text(encoding="utf-8")
    en = (PUBLIC / "en" / "index.html").read_text(encoding="utf-8")

    corps_fr = boutons_langue(corps(fr))
    # Identifiants et ancres distincts pour la version anglaise
    corps_en = re.sub(r'id="([a-z-]+)"', r'id="en-\1"', corps(en))
    corps_en = re.sub(r'href="#([a-z-]+)"', r'href="#en-\1"', corps_en)
    corps_en = boutons_langue(corps_en.replace('for="nav-toggle"', 'for="en-nav-toggle"'))

    entete = fr[: fr.index("</head>")]
    entete = re.sub(r'<link rel="(canonical|alternate)"[^>]*>\n', "", entete)
    entete = re.sub(r"<title>.*?</title>", "<title>Maquette — Site bilingue du Centre National de Floristique</title>", entete)

    page = (
        entete + CSS + "</head>\n<body>\n" + BANDEAU
        + '<div id="version-fr">\n' + corps_fr + "</div>\n"
        + '<div id="version-en" lang="en" hidden>\n' + corps_en + "</div>\n"
        + JS + "</body>\n</html>\n"
    )
    CIBLE.parent.mkdir(exist_ok=True)
    CIBLE.write_text(integrer_images(page), encoding="utf-8")
    print(f"Maquette générée : {CIBLE.relative_to(RACINE)}")


if __name__ == "__main__":
    main()
