# Site du Centre National de Floristique (CNF)

Site internet du CNF — Université Félix Houphouët-Boigny.

- Adresse : https://cnf-ufhb.ci
- Contenu du site : dossier `public/` (page principale : `public/index.html`)
- Hébergement : Cloudflare Workers (projet `cnf-site`), relié à ce dépôt GitHub.

Toute modification envoyée sur la branche `main` est publiée automatiquement en 1 à 2 minutes.

## Site bilingue (FR / EN)

- Version française (principale) : `public/index.html` → https://cnf-ufhb.ci/
- Version anglaise : `public/en/index.html` → https://cnf-ufhb.ci/en/ — **fichier généré, ne pas le modifier à la main**.
- Les textes anglais sont dans `traductions/en.json` (un texte français → sa traduction).
- La section **Actualités** reste en français sur les deux versions (seul son titre est traduit). Elle est délimitée dans la page française par les repères `ACTUALITES:DEBUT` / `ACTUALITES:FIN`.
- Les images sont dans `public/img/`, partagées par les deux versions.

Après toute modification de la page française :

    python3 outils/generer_en.py

Si un texte français a changé, le script le signale : mettre à jour la traduction correspondante dans `traductions/en.json`, puis relancer.

## Ajouter un chercheur

1. Recadrer la photo (portrait carré 360 × 360) dans `public/img/`.
2. Décrire la fiche dans `fiches/<nom>.json` (textes FR et EN — voir le modèle en tête de `outils/ajouter_chercheur.py`).
3. `python3 outils/ajouter_chercheur.py fiches/<nom>.json` puis `python3 outils/generer_en.py`.

Les fiches préparées mais pas encore publiées attendent sur la branche locale `chercheurs-a-publier` (non envoyée sur GitHub, donc invisible en ligne). Pour publier : `git checkout main && git merge chercheurs-a-publier && git push`.
