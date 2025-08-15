Jobs Radar – LinkedIn Job Scraper (CSV par recherche)

Outil Python pour chercher des offres LinkedIn par mot-clé et localisation, puis les ajouter dans un CSV dédié à chaque recherche.
Aux relances, le script déduplique et n’ajoute que les nouvelles offres.

⚠️ Note : le scraping de LinkedIn peut contrevenir à ses CGU et être limité/bloqué. Utilisez une fréquence faible (3–4 runs/jour), des pauses, et prévoyez un fallback légal (RSS Indeed / Welcome to the Jungle).

✨ Fonctionnalités

CSV par recherche : ex. Développeur Java @ Paris → out/jobs_developpeur-java_paris-ile-de-france-france.csv.

Déduplication : identifiant basé sur l’ID LinkedIn (si présent) sinon hash titre|entreprise|ville|mot-clé.

Fenêtre temporelle : filtre par date de publication (--past_hours : 24h / 7j / 30j / 0 = pas de filtre).

Multi-profils : exécute plusieurs recherches en série via profiles.yaml.

🗂️ Structure
LinkedIn-Job-Selenium-Scrapper/
├─ Linkedin_Scrapper.py     # scraper CLI (arguments : --job, --location, …)
├─ run_profiles.py          # exécute toutes les recherches listées dans profiles.yaml
├─ profiles.yaml            # configuration des recherches (job/location/pages/past_hours)
├─ out/                     # CSV générés (1 fichier par recherche)
└─ scraping.log             # logs (debug)

✅ Prérequis

macOS / Linux / Windows

Python 3.10+

Google Chrome installé (Selenium Manager gère automatiquement le driver)

🚀 Installation
# 1) cloner le repo
git clone https://github.com/<votre-user>/<votre-repo>.git
cd <votre-repo>

# 2) environnement Python (recommandé)
python3 -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
# .\.venv\Scripts\Activate.ps1

# 3) mise à jour pip
python -m pip install --upgrade pip

# 4) dépendances
pip install "selenium>=4.21,<5" beautifulsoup4==4.12.3 requests==2.32.3 pyyaml==6.0.2 lxml==5.2.2

⚙️ Configuration

Créer (ou éditer) profiles.yaml à la racine :

profiles:
  - job: "Développeur Java Angular"
    location: "Paris, Île-de-France, France"
    pages: 1
    past_hours: 24

  - job: "DevOps"
    location: "Casablanca, Maroc"
    pages: 1
    past_hours: 168

  - job: "QA Automaticien"
    location: "Casablanca, Maroc"
    pages: 1
    past_hours: 168


job : mots-clés (FR/EN OK).

location : utilisez un libellé reconnu par LinkedIn (ex. Paris, Île-de-France, France).

pages : 1 page ≈ 25 résultats (commencez à 1).

past_hours : 24 = 1 jour ; 168 = 7 jours ; 0 = pas de filtre de date.

▶️ Utilisation
1) Une seule recherche (CLI)
# venv activé
python Linkedin_Scrapper.py \
  --job "Développeur Java" \
  --location "Paris, Île-de-France, France" \
  --pages 1 \
  --past_hours 24


Résultat :

crée/ajoute dans out/jobs_developpeur-java_paris-ile-de-france-france.csv ;

append et déduplication (n’ajoute que les nouvelles offres).

Options utiles :

--past_hours 0 → pas de filtre de date ;

--csv out/mon_fichier.csv → forcer le nom du CSV de sortie.

2) Plusieurs recherches (batch)
python run_profiles.py


Exécute chaque profil défini dans profiles.yaml et met à jour 1 CSV par profil dans out/.