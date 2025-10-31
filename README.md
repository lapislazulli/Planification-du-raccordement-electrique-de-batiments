# ⚡️ Planification du Raccordement Électrique de Bâtiments

## 🎯 Objectif

Ce projet propose une simulation simple et visuelle de la **planification du raccordement électrique** de différents bâtiments (habitations, écoles, hôpitaux) à un réseau local.  
Il s’appuie sur des **données géospatiales (shapefiles)** et applique des **règles de coûts et durées** pour modéliser le déroulement des travaux.

L’idée est de trouver un équilibre entre **rapidité d’exécution**, **coût total**, et **priorisation des bâtiments critiques** (comme les hôpitaux).

---

## 🗂 Structure du dépôt

/data/ → shapefiles et fichiers sources
/scripts/ → scripts Python de traitement et d’optimisation
.gitignore
LICENSE
README.md


- Le dossier **data/** contient les shapefiles et fichiers CSV du réseau et des bâtiments.  
- Le dossier **scripts/** regroupe les fichiers Python pour l’analyse, l’optimisation et la génération de résultats.  
- Les sorties peuvent inclure des shapefiles, fichiers CSV, ou graphiques (Gantt, statistiques).

---

## 💻 Outils utilisés

| Outil / Librairie | Utilisation |
|--------------------|-------------|
| Python 3.x | Langage principal |
| GeoPandas | Lecture et traitement des shapefiles |
| Pandas | Analyse et manipulation de données |
| Matplotlib | Visualisation (graphiques, diagrammes Gantt) |
| CSV | Export des résultats structurés |

Le code utilise des structures classiques : piles, files, arbres binaires, et des algorithmes de tri et de filtrage pour ordonner les priorités.

---

## ⚙️ Paramètres du modèle

| Type d’infrastructure | Coût (€/m) | Durée (h/m) |
|------------------------|------------|--------------|
| Aérien                 | 500 €      | 2 h          |
| Semi-aérien            | 750 €      | 4 h          |
| Fourreau               | 900 €      | 5 h          |

- **Taux horaire** : 37,5 €/h  
- **Ouvriers maximum** : 4 par chantier  
- **Autonomie du générateur d’hôpital** : 20 h  
- **Phases de construction** :  
  - Phase 0 : Hôpital  
  - Phase 1 : 40 % du réseau  
  - Phases 2–4 : 20 % chacune  

---

## 🧩 Exemple d’exécution

```bash
# Cloner le dépôt
git clone https://github.com/lapislazulli/Planification-du-raccordement-electrique-de-batiments.git
cd Planification-du-raccordement-electrique-de-batiments

# Installer les dépendances
pip install -r requirements.txt

# Lancer la simulation
python scripts/optimize_grid_connections.py
