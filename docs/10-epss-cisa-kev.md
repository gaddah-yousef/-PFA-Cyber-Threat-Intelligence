# Enrichissement EPSS et CISA KEV

## Objectif

Deux CVE avec un score CVSS proche ne présentent pas forcément la même urgence pour une PME. Sentinel PME complète donc les informations techniques de la NVD avec deux signaux gratuits et publics :

- **EPSS** estime la probabilité qu’une CVE soit exploitée dans les 30 prochains jours ;
- **CISA KEV** recense les vulnérabilités dont l’exploitation dans la nature est confirmée.

Ces signaux servent à prioriser. Ils ne prouvent pas, à eux seuls, qu’un actif précis est vulnérable : cette décision reste liée à l’inventaire logiciel et au matching CPE/version.

## Flux de données

```text
Collecteur NVD
    │
    ├── CVE + CVSS + configurations CPE
    │
    ├── FIRST EPSS API ── probabilité + percentile + date
    │
    └── CISA KEV JSON ─── exploitation connue + échéance + action
              │
              ▼
       ThreatInput normalisé
              │
              ▼
        Scoring explicable
              │
              ▼
       SQLite/PostgreSQL + API + React
```

L’enrichissement est exécuté pour les éléments renvoyés par le collecteur NVD. Les deux appels externes sont indépendants : si EPSS ou CISA est temporairement indisponible, les CVE NVD sont quand même enregistrées.

## Données persistées

| Champ | Signification |
|---|---|
| `epss_score` | Probabilité EPSS entre 0 et 1 |
| `epss_percentile` | Position de la CVE dans la distribution EPSS |
| `epss_updated_at` | Date du calcul EPSS |
| `known_exploited` | Présence dans CISA KEV |
| `kev_date_added` | Date d’ajout au catalogue |
| `kev_due_date` | Échéance de remédiation publiée par CISA |
| `kev_required_action` | Action demandée par CISA |
| `kev_ransomware_use` | Usage connu dans une campagne rançongiciel |

## Politique de scoring Sentinel PME

La politique locale ajoute :

- **+15 points** si la CVE est dans CISA KEV ;
- **+10 points** si le percentile EPSS est supérieur ou égal à 90 % ;
- **+5 points** si le percentile EPSS est supérieur ou égal à 75 %.

Le score total reste plafonné à 100. Les seuils sont volontairement simples et expliqués dans `GET /api/threats/{id}/explain`. Ils représentent une règle de priorisation du projet, pas une recommandation officielle de FIRST ou de CISA.

## Configuration

Aucune nouvelle clé API n’est nécessaire. `NVD_API_KEY` reste facultative mais améliore le quota NVD. Les URLs utilisées sont :

- [API FIRST EPSS](https://api.first.org/epss/)
- [Catalogue CISA Known Exploited Vulnerabilities](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)

Après mise à jour du code, appliquez la migration :

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

Une nouvelle collecte NVD enrichira ensuite les CVE reçues. Les enregistrements plus anciens seront actualisés lorsqu’ils seront à nouveau renvoyés par la fenêtre récente de la NVD.
