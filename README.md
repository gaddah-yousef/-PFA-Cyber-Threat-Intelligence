# PFA CMRPI — Détection et alerte précoce des cybermenaces ciblant les PME

Plateforme web de Threat Intelligence qui collecte, normalise et priorise des indicateurs cyber afin d’aider les PME à agir avant qu’un incident ne prenne de l’ampleur.

> Ce projet est un système d’alerte précoce avec des fonctions « SIEM-light ». Il ne remplace pas un SIEM complet comme Splunk ou QRadar et ne collecte pas massivement les journaux internes.

## Objectifs

- Centraliser des indicateurs issus de sources Threat Intelligence.
- Calculer un score de risque explicable de 0 à 100.
- Détecter automatiquement les menaces élevées et critiques.
- Présenter les résultats dans un dashboard simple pour une PME.
- Associer chaque menace à des actions de réponse concrètes.

## Architecture

```text
Threat Intelligence APIs
        ↓
Python Collectors
        ↓
Normalizer
        ↓
Risk Scoring Engine
        ↓
SQLite / PostgreSQL
        ↓
FastAPI Backend
        ↓
React Dashboard
        ↓
Alerts + Fiches Réflexes
```

## Fonctionnalités du MVP

- Modèle unifié pour IP, domaines, URLs, CVE et hashes.
- Cinq collecteurs : jeu de démonstration, URLhaus, NVD, AbuseIPDB et AlienVault OTX.
- Collecte planifiée automatiquement (APScheduler) et déclenchable à la demande depuis le dashboard.
- Déduplication : une même paire (indicateur, source) met à jour la menace existante au lieu de la dupliquer.
- Scoring selon la sévérité, la source, le type, la récence et le contexte PME.
- Authentification JWT avec 3 rôles (Administrateur, Analyste, Responsable PME) et permissions différenciées.
- API FastAPI documentée automatiquement avec OpenAPI, protégée par authentification et limitation de débit sur les endpoints d’écriture.
- Stockage SQLAlchemy sur SQLite, configurable pour PostgreSQL, avec migrations Alembic.
- Alertes persistées pour les scores supérieurs ou égaux à 70, avec un mini-workflow SOC (statut, assignation, notes d’analyste) en plus de l’acquittement simple.
- Score de risque explicable : les facteurs du calcul (sévérité, type, source, récence, corrélation multi-sources…) sont persistés et consultables via l’API et le dashboard.
- Export SIEM générique, formats Wazuh et Elastic ECS, ainsi que notifications optionnelles HMAC, Slack, Telegram et SMTP — voir [`docs/08-integration-soc-siem.md`](./docs/08-integration-soc-siem.md).
- Interopérabilité CTI par exports STIX 2.1 et MISP, corrélations multi-sources et détection d'anomalies explicable.
- Readiness, métriques Prometheus, logs structurés, sauvegarde SQLite et file Redis/RQ optionnelle.
- Administration des utilisateurs depuis le dashboard (rôles et activation).
- Journal d’audit des actions sensibles (connexion, gestion des comptes, traitement des alertes, déclenchement des collecteurs), consultable par l’administrateur.
- Dashboard avec statistiques, filtres, détails (y compris le détail du score), centre d’alertes façon SOC et suivi des sources de veille.
- Fiches réflexes pour phishing, malware, ransomware, brute force et CVE.
- Inventaire du parc PME (actifs et logiciels), import CSV contrôlé et rapprochement explicable avec les plages CPE/version des CVE NVD.
- Enrichissement automatique des CVE NVD avec EPSS (probabilité d’exploitation) et CISA KEV (exploitation active connue), pris en compte dans le score et affiché dans la fiche menace.
- Tests pytest (backend) et Vitest/React Testing Library (frontend), images Docker et pipeline GitHub Actions DevSecOps avec audits de dépendances, SAST, détection de secrets, scans Trivy, SBOM et attestations de provenance.

## Stack technique

| Couche | Technologies |
|---|---|
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| Données | SQLite en local, configuration PostgreSQL prête |
| Frontend | React, TypeScript, Vite, Tailwind CSS, Axios |
| Qualité | pytest, TypeScript, GitHub Actions |
| Déploiement | Docker, Docker Compose, Nginx |

## Installation locale

### Prérequis

- Python 3.12 ou version compatible
- Node.js 22 ou version compatible
- Git

### Backend

```bash
cd backend
python -m venv .venv
# Windows : .venv\Scripts\activate
# Linux/macOS : source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # puis renseigner JWT_SECRET_KEY et les clés API souhaitées
alembic upgrade head
uvicorn app.main:app --reload
```

L’API répond sur `http://localhost:8000` et sa documentation interactive sur `http://localhost:8000/docs`.

Au premier démarrage, si aucun utilisateur n’existe, un compte administrateur est créé automatiquement à partir de `ADMIN_EMAIL` / `ADMIN_PASSWORD` (valeurs par défaut : `admin@pme-cyber.local` / `ChangeMe123!`, **à changer en production**). Cet administrateur peut ensuite créer des comptes Analyste ou Responsable PME via `POST /api/auth/users`.

### Frontend

Dans un second terminal :

```bash
cd frontend
npm install
npm run dev
```

Le dashboard est disponible sur `http://localhost:5173`.

### Tests et build

```bash
cd backend
pytest -q

cd ../frontend
npm run test -- --run
npm run build
```

### Migrations de base de données (Alembic)

```bash
cd backend
alembic upgrade head              # appliquer les migrations
alembic revision --autogenerate -m "description"   # après une évolution des modèles
```

En local avec SQLite, `init_db()` crée aussi les tables manquantes au démarrage pour rester sans friction ; Alembic est le chemin recommandé dès que la base évolue (notamment sur PostgreSQL en production).

## Lancement avec Docker Compose

```bash
docker compose up --build
```

- Dashboard : `http://localhost:3000`
- API : `http://localhost:8000`
- Swagger : `http://localhost:8000/docs`

Le profil production PostgreSQL + Redis + worker est documenté dans
[`docs/12-deploiement-production.md`](./docs/12-deploiement-production.md).

## CI/CD DevSecOps

Chaque push et pull request exécute les tests backend/frontend, une migration Alembic sur base vierge, les audits de dépendances, Bandit, Gitleaks, Trivy et le build des images Docker. Un tag sémantique comme `v1.0.0` publie ensuite les images backend et frontend dans GHCR avec SBOM et attestation de provenance.

La configuration, les barrières de sécurité et les réglages GitHub recommandés sont détaillés dans [`docs/09-ci-cd-devsecops.md`](./docs/09-ci-cd-devsecops.md).

## Endpoints principaux

| Méthode | Endpoint | Accès |
|---|---|---|
| POST | `/api/auth/login` | Public — authentification (renvoie un JWT) |
| GET | `/api/auth/me` | Authentifié |
| POST | `/api/auth/users` | Admin — créer un utilisateur |
| GET | `/health` | Public |
| GET | `/api/threats` | Authentifié — lister et filtrer les menaces (en-tête `X-Total-Count`) |
| GET | `/api/threats/{id}` | Authentifié |
| POST | `/api/threats/analyze` | Admin/Analyste — limité en débit |
| POST | `/api/threats/manual` | Admin/Analyste — limité en débit |
| GET | `/api/threats/critical` | Authentifié |
| GET | `/api/threats/{id}/explain` | Authentifié — détail du calcul du score |
| GET | `/api/stats` | Authentifié — alimente les cartes du dashboard |
| GET | `/api/reflex-sheets` | Authentifié |
| GET | `/api/alerts` | Authentifié |
| POST | `/api/alerts/test` | Admin/Analyste — limité en débit |
| PATCH | `/api/alerts/{id}` | Admin/Analyste — workflow SOC (statut, assignation, notes) |
| PATCH | `/api/alerts/{id}/acknowledge` | Admin/Analyste — compatibilité, acquitte et résout |
| GET | `/api/alerts/{id}/siem-event` | Authentifié — export JSON SIEM-friendly |
| GET | `/api/alerts/{id}/siem-event/elastic` | Authentifié — événement Elastic ECS |
| GET | `/api/alerts/{id}/siem-event/wazuh` | Authentifié — événement Wazuh |
| GET | `/api/intelligence/export/stix` | Authentifié — bundle STIX 2.1 |
| GET | `/api/intelligence/export/misp` | Authentifié — événement MISP JSON |
| GET | `/taxii2/`, `/api/taxii2/collections/` | Découverte publique, collection TAXII authentifiée |
| GET | `/api/intelligence/correlations` | Authentifié — confirmations multi-sources |
| GET | `/api/intelligence/anomalies` | Authentifié — écarts de score expliqués |
| GET | `/api/collectors` | Authentifié — état des sources de veille |
| POST | `/api/collectors/{name}/run` | Admin/Analyste — déclenche une collecte, limité en débit |
| POST | `/api/collectors/{name}/enqueue` | Admin/Analyste — collecte via Redis/RQ |
| GET | `/api/collectors/jobs/{id}` | Authentifié — état de la tâche |
| GET | `/api/audit-logs` | Admin — journal d’audit des actions sensibles |
| GET | `/api/assets` | Authentifié — inventaire filtrable (`X-Total-Count`) |
| POST | `/api/assets` | Admin/Analyste — créer un actif |
| POST | `/api/assets/import` | Admin/Analyste — importer un CSV validé |
| GET/POST | `/api/assets/{id}/software` | Authentifié en lecture, Admin/Analyste en écriture |
| GET | `/api/assets/{id}/vulnerabilities` | Authentifié — correspondances CVE expliquées |
| GET | `/health/ready` | Public — readiness base de données |
| GET | `/metrics` | Public — métriques Prometheus |

## Captures d’écran

> À compléter après la première démonstration : vue d’ensemble, registre des menaces, détail d’un score et centre d’alertes.

## Documentation

Les choix fonctionnels et techniques sont détaillés dans le dossier [`docs`](./docs), notamment l’état de l’art, les sources, l’architecture, le scoring, l’API, les tests et la roadmap.

## Sécurité

- Authentification JWT (`python-jose`/`PyJWT` + `bcrypt`) et autorisation par rôle (admin/analyste/viewer) sur tous les endpoints sensibles.
- Limitation de débit (`slowapi`) sur les endpoints d’écriture pour limiter l’empoisonnement de données et les abus.
- En-têtes de sécurité (CSP, X-Frame-Options, X-Content-Type-Options, HSTS en production) sur toutes les réponses API.
- CI avec analyse de dépendances (`pip-audit`, `npm audit`), analyse statique (`bandit`) et détection de secrets (`gitleaks`).
- Images Docker backend et frontend exécutées avec des utilisateurs non-root.
- `.env` jamais commité (voir `.gitignore`) ; secrets injectés via variables d’environnement.

## Roadmap

- Alertes Email, Telegram, Slack (webhook générique déjà disponible, voir [`docs/08-integration-soc-siem.md`](./docs/08-integration-soc-siem.md)).
- Corrélation d’indicateurs multi-sources plus fine (fenêtre temporelle, règles multi-indicateurs — un premier bonus de corroboration multi-sources existe déjà dans le scoring).
- Connecteurs dédiés Wazuh/Elastic plutôt qu’un webhook générique.
- Modèle Scikit-learn expérimental en complément du scoring à règles.
- Elasticsearch/Kibana pour les volumes plus importants.
- Gestion d’utilisateurs côté frontend (interface d’administration des comptes).
- Recalcul automatique des correspondances actifs/CVE après chaque collecte NVD.

## Auteur

**Étudiant(e) :** à compléter
**Encadrant(e) CMRPI/EMC :** à compléter
**Année universitaire :** 2025–2026
