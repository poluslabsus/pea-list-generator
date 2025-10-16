# Générateur de CSV — Actions éligibles au PEA

Application Streamlit pour créer un CSV listant des actions **éligibles PEA** (France + EEE)
à partir des pages publiques ProRealTime.

## Fichiers

- `app.py` : interface Streamlit (prévisualisation + téléchargement)
- `pea_sources.py` : fonctions de collecte et de parsing
- `requirements.txt` : dépendances Python

## Lancer en local

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Déploiement Streamlit Cloud

1. Pousse ce repo sur GitHub (public).
2. Sur Streamlit Cloud : **New app** → sélectionne le repo → fichier `app.py` → Deploy.
3. L'application propose un bouton pour télécharger le CSV.

> **Avertissement** : l'éligibilité PEA peut changer. Vérifie auprès de ton courtier.
