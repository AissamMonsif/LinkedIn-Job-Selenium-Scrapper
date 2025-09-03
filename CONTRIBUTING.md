Contribution Guide

- Branches: feature/<topic>, fix/<topic>.
- Discussions: ouvrez une issue pour cadrer la portée avant un gros refactor.
- Code: privilégiez des fonctions pures testables; évitez la logique dans les scripts.
- Tests: ajoutez des tests unitaires pour les helpers; évitez des tests E2E Selenium instables.
- Style: suivez ruff et black (voir pyproject.toml). Pas d’imports non utilisés.
- CI: l’intention est de garder les tests rapides et sans navigateur.

Local setup

- Créez un venv, installez les dépendances de requirements.txt.
- Exécutez pytest localement avant d’ouvrir une PR.

