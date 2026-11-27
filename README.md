# Skull King : carnet de scores

- `scores-skull-king.html` : l'app de scores pour iPhone et iPad (joueurs, cartes par manche, paris, plis, bonus, classement). Publiée en page privée sur claude.ai.
- `planche-skull-king-A4.pdf` : planche de scores à imprimer, deux grilles de 6 joueurs par feuille A4.
- `planche-src.html` : source du PDF (à imprimer en PDF depuis Chrome, sans marges).

## Version autonome (GitHub Pages, hors ligne)

`python3 build.py` reconstruit `docs/` à partir de `scores-skull-king.html` : page complète, police embarquée, icône, et un service worker qui garde l'app disponible sans réseau. Après une modification de l'app : relancer `build.py`, puis commit et push.
