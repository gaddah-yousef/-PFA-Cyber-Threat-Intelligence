# Plan de finalisation globale — 15 octobre 2026

## Objectif

Fermer les écarts restants entre le MVP démontrable et une livraison PFA
industrialisée, sans transformer Sentinel PME en SIEM complet. Les intégrations
externes restent optionnelles et désactivées tant que leurs variables
d'environnement ne sont pas configurées.

## Ordre d'implémentation

### Phase A — Bloqueurs de livraison

- [x] Remplacer la suppression de SQLite dans `start-sentinel.bat` par `alembic upgrade head`.
- [x] Refuser les identifiants administrateur par défaut en production.
- [x] Persister le contexte PME utilisé par le scoring.
- [x] Recalculer les correspondances actifs/CVE après une collecte NVD.
- [x] Synchroniser la documentation des phases et versions.

### Phase B — Notifications et interopérabilité SOC

- [x] Ajouter les notifications SMTP, Slack et Telegram, toutes optionnelles.
- [x] Ajouter des formats SIEM dédiés Wazuh et Elastic ECS.
- [x] Conserver le webhook HMAC existant et isoler les pannes par canal.

### Phase C — Analyse et échange avancés

- [x] Exposer les menaces au format STIX 2.1 et MISP JSON.
- [x] Ajouter une corrélation multi-sources des indicateurs.
- [x] Ajouter un détecteur d'anomalies expérimental, explicable et sans décision automatique.

### Phase D — Industrialisation

- [x] Ajouter métriques, readiness et logs structurés.
- [x] Ajouter une sauvegarde SQLite contrôlée et documentée.
- [x] Vérifier PostgreSQL dans la CI et ajouter Redis/RQ.
- [x] Ajouter une configuration de déploiement production reproductible.
- [x] Initialiser Git localement sans publier de secret.
- [x] Publier Git sur `gaddah-yousef/-PFA-Cyber-Threat-Intelligence` et activer GitHub Actions.

### Phase E — Livraison

- [x] Ajouter l'administration des utilisateurs dans le frontend.
- [x] Valider par navigateur réel la connexion, le dashboard et l'administration.
- [x] Mettre à jour README, architecture, roadmap et checklist finale.
- [x] Exécuter tous les tests, builds, migrations et contrôles de sécurité disponibles.

## Limites externes

- Le premier workflow distant `CI DevSecOps` est activé, mais son exécution du 15 octobre 2026 doit encore être corrigée (échec GitHub Actions, alors que les validations locales passent).
- Le déploiement public exige le choix et l'accès à une plateforme cible.
- Les canaux SMTP, Slack, Telegram, Wazuh, Elastic et MISP exigent leurs URLs ou secrets réels.

# Implementation Plan: Sentinel PME - montée en niveau SOC/SIEM

## Overview

Faire évoluer Sentinel PME d'un simple tableau de bord de Threat Intelligence vers une plateforme MVP plus proche d'un environnement entreprise : alertes exploitables par un analyste, export SIEM, workflow SOC léger, documentation claire et tests de non-régression.

## Architecture Decisions

- Garder le cœur MVP existant : FastAPI, SQLAlchemy, React, collecteurs Threat Intelligence, scoring et fiches réflexes.
- Ajouter une couche SOC légère autour des alertes au lieu de prétendre remplacer un SIEM complet.
- Exposer les alertes au format JSON SIEM-friendly via une API REST additive, sans casser les endpoints existants.
- Conserver une approche incrémentale : backend d'abord, puis dashboard SOC, puis intégration SIEM avancée.

## Task List

### Phase 1: Foundation SOC/SIEM

- [x] Task 1: Ajouter un workflow SOC minimal aux alertes
- [x] Task 2: Ajouter un endpoint d'export SIEM JSON
- [x] Task 3: Documenter le positionnement SIEM/SOC dans les docs
- [x] Bonus : score explicable persisté + bonus de corrélation multi-sources, journal d'audit

### Checkpoint: Foundation

- [x] Tests backend écrits pour toutes les nouveautés (`test_api.py`, `test_advanced_features.py`)
- [x] Swagger expose les nouveaux endpoints (routes FastAPI avec `response_model`)
- [x] Les alertes existantes restent compatibles (`/acknowledge` conservé, champs SOC avec défauts)

### Phase 2: Dashboard SOC

- [x] Task 4: Ajouter les types frontend pour les statuts SOC et l'export SIEM
- [x] Task 5: Améliorer la page Alertes avec statut, assignation et export
- [x] Task 6: Ajouter une page ou section "SOC View" — intégrée directement à la page Alertes (statut/assignation/notes/export) plutôt qu'une page séparée, pour éviter de fragmenter le flux analyste

### Checkpoint: Dashboard

- [x] Build frontend validé localement (`npm run build`, 1 667 modules transformés).
- [x] Le flux analyste fonctionne : voir, traiter (statut/assignation/notes), exporter (SIEM JSON)

### Phase 3: Integrations avancées

- [x] Task 7: Ajouter une configuration webhook SIEM optionnelle (`WEBHOOK_URL`/`WEBHOOK_SECRET`, signature HMAC)
- [x] Task 8: Intégrer Wazuh et Elastic — formats JSON dédiés, endpoints d'export et connecteurs push optionnels ; Splunk reste pris en charge via le webhook générique documenté.
- [x] Task 9: Enrichir les playbooks SOC — procédures chronologiques, preuves à préserver, critères d'escalade et références intégrés aux fiches réflexes.

### Checkpoint: Complete

- [x] Tests backend et frontend validés localement : 60 tests backend et 17 tests frontend réussis.
- [x] Documentation de démonstration prête (`docs/08-integration-soc-siem.md`, README mis à jour)
- [x] Projet présentable comme MVP entreprise (workflow SOC, export SIEM, audit, scoring explicable)

### Validation locale — 15 octobre 2026

- `pytest -q` : 60 tests réussis.
- `npm run test -- --run` : 10 fichiers et 17 tests réussis.
- `npm run lint` : aucune erreur ESLint.
- `npm run build` : build TypeScript/Vite réussi, 1 667 modules transformés.
- Migration Alembic vérifiée jusqu'à la révision `d4f6027a9b31` sur une base vierge.
- Workflow d'alerte email validé avec une menace critique de score 97/100.

## Extension Sentinel PME 2.0 — Phase 1

- [x] Audit du dépôt et revue de l’architecture existante.
- [x] Inventaire des actifs et des logiciels avec RBAC et audit.
- [x] Conservation des configurations CPE de la NVD.
- [x] Matching CVE prudent (`confirmed`, `potential`, `not_affected`).
- [x] Migration Alembic additive vérifiée sur SQLite vierge.
- [x] Écrans React parc informatique et détail actif.
- [x] Tests de non-régression backend/frontend et build.

## Extension Sentinel PME 2.0 — Phase 2

- [x] Interrogation de FIRST EPSS par lots de CVE sans clé API.
- [x] Corrélation avec le flux JSON officiel CISA KEV.
- [x] Dégradation contrôlée : une source d’enrichissement indisponible ne bloque pas la collecte NVD.
- [x] Persistance et exposition API des signaux EPSS/KEV.
- [x] Score contextuel : +10 points au-dessus du 90e percentile EPSS, +5 au-dessus du 75e, +15 pour une CVE KEV.
- [x] Vue frontend dédiée à la priorisation de la vulnérabilité.
- [x] Tests backend/frontend et migration Alembic.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Transformer le projet en SIEM trop ambitieux | High | Positionner Sentinel PME comme brique Threat Intelligence + SOC-light |
| Casser les alertes existantes | Medium | Ajouter des champs optionnels/defaults et tester l'ancien flux |
| Complexifier l'interface trop tôt | Medium | Backend SOC/SIEM d'abord, UI ensuite |
| Dépendre d'un SIEM externe absent | Medium | Commencer par un export JSON local/testable |

## Décisions actées

- Wazuh et Elastic disposent de formats et connecteurs optionnels dédiés ; les autres SIEM peuvent utiliser le webhook HMAC générique.
- L'authentification avec rôles `admin`, `analyst` et `viewer` est implémentée dans l'API et le frontend.
- Les notifications email, Slack et Telegram sont intégrées après le workflow SOC et restent configurables par variables d'environnement.
