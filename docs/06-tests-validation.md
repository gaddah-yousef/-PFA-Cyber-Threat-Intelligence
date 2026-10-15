# Tests et validation

## Tests backend automatisés

La suite pytest vérifie :

- l’état de santé de l’API ;
- l’analyse et l’enregistrement d’une menace ;
- les bornes et seuils du moteur de scoring ;
- la liste des menaces critiques ;
- le contenu d’une fiche réflexe.

```bash
cd backend
pytest -q
```

Les tests utilisent une base SQLite dédiée, recréée pour chaque cas. Ils ne contactent aucune API Threat Intelligence externe.

## Validation frontend

TypeScript et Vite vérifient le typage et produisent le bundle :

```bash
cd frontend
npm run build
```

La recette manuelle couvre la vue d’ensemble, les filtres, le détail d’une menace, la génération d’une alerte test, les fiches réflexes et l’affichage responsive.

## Critères d’acceptation

- Tous les tests passent sans secret ni accès réseau.
- Le dashboard charge les données de l’API sans erreur CORS.
- Un score de 70 crée une alerte élevée et un score de 90 une alerte critique.
- Une entrée invalide reçoit une erreur 422 et une ressource absente une erreur 404.
