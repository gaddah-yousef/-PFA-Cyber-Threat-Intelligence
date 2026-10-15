# Architecture Sentinel PME 2.0

## Positionnement

Sentinel PME est une plateforme de Threat Intelligence et de SOC léger pour PME. Elle centralise des signaux externes, les priorise, les relie au parc informatique déclaré et aide un analyste à décider. Elle ne remplace pas un SIEM chargé d’ingérer tous les journaux internes.

## Flux de données

```text
NVD / OTX / URLhaus / AbuseIPDB / démo
                  │
                  ▼
       Collecteurs et normalisation
                  │
                  ▼
  Menaces + score explicable + données CPE NVD
                  │
         ┌────────┴────────┐
         ▼                 ▼
 Alertes / workflow SOC    Matching actifs ↔ logiciels ↔ CVE
         │                 │
         └────────┬────────┘
                  ▼
      API FastAPI authentifiée
                  │
                  ▼
       Dashboard React / export SIEM
```

## Modules backend

- `collectors/` interroge les sources externes et produit un `ThreatInput` commun.
- `services/threat_service.py` déduplique, calcule le score et déclenche les alertes.
- `models/asset.py` porte les actifs et logiciels installés.
- `services/vulnerability_matching.py` interprète prudemment les configurations CPE NVD.
- `api/routes_assets.py` expose l’inventaire, l’import CSV et les résultats de matching.
- `audit_logs` conserve les actions sensibles, sans stocker de secret.

## Contrôle d’accès

Les trois rôles existants sont conservés :

| Action | Admin | Analyste | Viewer |
|---|---:|---:|---:|
| Lire actifs, logiciels et correspondances CVE | Oui | Oui | Oui |
| Créer/modifier/supprimer/importer des actifs | Oui | Oui | Non |
| Ajouter un logiciel | Oui | Oui | Non |
| Lire le journal d’audit | Oui | Non | Non |

Le backend applique ces règles ; le masquage des boutons dans React n’est qu’une aide d’interface.

## État des phases

- Phase 1 — Asset Inventory, Software Inventory et CVE Matching : implémentée.
- Phase 2 — EPSS, CISA KEV et scoring contextuel : planifiée, non implémentée.
- Phase 3 — intégration Wazuh et corrélation d’événements : planifiée.
- Phase 4 — rapports et durcissement final : planifiée.

Les ajouts de phase 1 sont additifs : les routes Threat Intelligence, alertes SOC, collecteurs, audit et fiches réflexes restent compatibles.
