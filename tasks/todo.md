# Finalisation globale — checklist active

- [x] Bloqueurs de livraison et sécurité production
- [x] Notifications multicanal et formats SIEM dédiés
- [x] STIX/MISP, corrélation et analyse expérimentale
- [x] Observabilité, sauvegarde, Redis/RQ et validation PostgreSQL en CI
- [x] Interface d'administration et documentation finale
- [x] Validation navigateur locale
- [ ] Activation GitHub et déploiement public (accès externes requis)

# Sentinel PME - TODO SOC/SIEM

## Task 1: Ajouter un workflow SOC minimal aux alertes — ✅ Terminé

**Description:** Étendre les alertes pour représenter un mini-incident SOC avec statut, assignation et notes analyste.

**Acceptance criteria:**
- [x] Une alerte expose un `status` parmi `new`, `investigating`, `resolved`, `false_positive`.
- [x] Une alerte peut contenir `assigned_to` et `resolution_notes`.
- [x] L'ancien endpoint `PATCH /api/alerts/{id}/acknowledge` continue de fonctionner.

**Verification:**
- [x] Tests backend alertes passent (`test_alert_soc_status_update_flow`, `test_alert_acknowledge_flow`).
- [x] Une alerte acquittée passe dans un statut cohérent (`resolved`).

**Dependencies:** None

**Files touchés:**
- `backend/app/models/alert.py`
- `backend/app/schemas/alert.py`
- `backend/app/api/routes_alerts.py`
- `backend/alembic/versions/3d41050f4232_soc_workflow_audit_log_and_score_.py`
- `backend/tests/test_api.py`

**Estimated scope:** Medium

## Task 2: Ajouter un endpoint d'export SIEM JSON — ✅ Terminé

**Description:** Exposer une alerte dans un format JSON stable exploitable par un SIEM ou un webhook SOC.

**Acceptance criteria:**
- [x] `GET /api/alerts/{id}/siem-event` retourne un objet JSON SIEM-friendly.
- [x] Le JSON inclut alerte, menace associée, score, source, action recommandée et horodatage.
- [x] Le endpoint nécessite une authentification.

**Verification:**
- [x] Test API dédié (`test_alert_siem_event_export`, `test_siem_event_requires_an_associated_threat`).
- [x] Le endpoint retourne 404 si l'alerte n'existe pas (ou si elle n'a pas de menace associée).

**Dependencies:** Task 1

**Files touchés:**
- `backend/app/schemas/alert.py`
- `backend/app/api/routes_alerts.py`
- `backend/tests/test_api.py`

**Estimated scope:** Small

## Task 3: Documenter le positionnement SIEM/SOC — ✅ Terminé

**Description:** Ajouter une documentation claire expliquant que Sentinel PME est une brique SOC/SIEM-light, pas un SIEM complet.

**Acceptance criteria:**
- [x] Une page documentation explique l'architecture SOC/SIEM.
- [x] La roadmap mentionne Wazuh/Elastic/Splunk comme intégrations possibles.

**Verification:**
- [x] Relecture Markdown.

**Dependencies:** Task 2

**Files touchés:**
- `docs/08-integration-soc-siem.md`
- `README.md`

**Estimated scope:** Small

## Bonus (hors périmètre initial, ajoutés dans la même itération)

- [x] Score de risque explicable et persisté (`score_factors`) + `GET /api/threats/{id}/explain`.
- [x] Bonus de scoring pour corrélation multi-sources d'un même indicateur.
- [x] Journal d'audit (`audit_logs`) + `GET /api/audit-logs` (admin).
- [x] Webhook SOC sortant optionnel, signé HMAC (`WEBHOOK_URL`/`WEBHOOK_SECRET`).
- [x] Frontend : page Alertes transformée en vue SOC (statut, assignation, notes, export SIEM) ; détail du score sur la page menace.

Voir `tasks/plan.md` pour les tâches restantes (Phase 3 : intégrations avancées).

## Sentinel PME 2.0 — Phase 1 Asset Intelligence — ✅ Terminée

- [x] CRUD et import CSV des actifs.
- [x] Inventaire logiciel avec CPE/PURL optionnels.
- [x] Matching local des CVE NVD avec justification.
- [x] RBAC admin/analyste/viewer et journal d’audit.
- [x] Migration Alembic et interfaces React.
- [x] Documentation dans `docs/architecture-sentinel-pme-2.md`, `docs/asset-inventory.md` et `docs/vulnerability-matching.md`.

## Sentinel PME 2.0 — Phase 2 Vulnerability Intelligence — ✅ Terminée

- [x] Enrichissement automatique des CVE NVD avec l’API gratuite FIRST EPSS.
- [x] Corrélation avec le catalogue officiel CISA KEV.
- [x] Persistance des scores, percentiles, échéances et actions recommandées.
- [x] Bonus de score explicable pour EPSS et exploitation active connue.
- [x] Affichage EPSS/KEV dans le registre et la fiche détaillée d’une menace.
- [x] Migration Alembic et tests de non-régression.

Prochaine étape : automatiser le recalcul des correspondances actifs/CVE après collecte, puis enrichir les playbooks SOC.
