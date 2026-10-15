# Roadmap

## V1 — MVP livré

- Modèle normalisé et base SQLite.
- Scoring à règles et fiches réflexes.
- Alertes dashboard à partir de 70/100.
- Collecteur local, URLhaus et support NVD.
- API FastAPI, dashboard React, tests, Docker et CI.

## V1.1 — Enrichissement livré

- Connecteurs AlienVault OTX et AbuseIPDB.
- Déduplication par indicateur, source et période.
- Import manuel CSV/JSON et suivi de l’état de traitement.
- Authentification et rôles utilisateur.

## V1.2 — Alertes multicanal livrées

- Email, Telegram, Slack et Webhook.
- Préférences par niveau et type de menace.
- Acquittement, assignation et historique des décisions.

## V2 — Industrialisation livrée

- PostgreSQL, Alembic et tâches de collecte planifiées.
- Files de messages et traitements asynchrones.
- Formats Wazuh/Elastic ECS et profil PostgreSQL/Redis reproductible.
- Métriques, logs structurés, sauvegardes et observabilité.

## V3 — Analyse avancée livrée

- Corrélation multi-sources et matching avec les actifs propres à la PME.
- Détection d'anomalies statistique robuste, explicable et expérimentale.
- Échange MISP, STIX 2.1 et TAXII 2.1 en lecture seule.

## Après le PFA

- corrélation temporelle de journaux déléguée à Wazuh/Elastic ;
- modèle ML supervisé seulement après constitution et validation d'un jeu de
  données étiqueté ;
- haute disponibilité multi-nœuds et tests de reprise sur une cible réelle.
