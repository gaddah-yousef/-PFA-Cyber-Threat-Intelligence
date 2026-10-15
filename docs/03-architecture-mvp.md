# Architecture du MVP

```text
Threat Intelligence APIs
        ↓
Python Collectors
        ↓
Normalizer
        ↓
Risk Scoring Engine
        ↓
Database
        ↓
FastAPI Backend
        ↓
React Dashboard
        ↓
Alerts + Fiches Réflexes
```

## Composants

Les collecteurs convertissent les formats NVD, URLhaus ou locaux vers un schéma `ThreatInput`. Cette frontière empêche les différences entre sources de se propager dans le reste du système.

Le moteur de scoring attribue des points à des facteurs explicites, puis le service métier enrichit la menace avec une action recommandée. SQLAlchemy enregistre la menace et crée une alerte si son score atteint 70.

FastAPI expose les données validées au dashboard React. Le frontend consulte l’API via Axios, fournit les filtres et affiche les informations sans recalculer le risque côté navigateur.

## Modèle de données

Une menace contient un UUID, un indicateur, ses types, sa source, sa sévérité, son score et niveau de risque, une description, une recommandation et ses dates d’observation. Une alerte référence éventuellement la menace et conserve son niveau, son message, son canal et son état d’acquittement.

## Sécurité et exploitation

Les secrets ne sont jamais intégrés au code, CORS autorise uniquement les origines configurées et Pydantic valide les entrées. SQLite simplifie le développement ; une URL `postgresql+psycopg://...` permet de basculer vers PostgreSQL. Elasticsearch et Kibana restent des améliorations de montée en charge.
