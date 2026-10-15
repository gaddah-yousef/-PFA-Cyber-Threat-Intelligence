# Inventaire des actifs

## Objectif

L’inventaire répond à une question opérationnelle : « Cette vulnérabilité concerne-t-elle réellement un équipement de la PME ? » Un actif décrit un serveur, poste, équipement réseau, application ou service cloud. Chaque actif peut contenir plusieurs logiciels.

## Données d’un actif

- hostname unique, adresse IPv4 ou IPv6 optionnelle ;
- type, système d’exploitation et environnement ;
- criticité métier et exposition à Internet ;
- responsable et description optionnels ;
- compteurs de logiciels et de correspondances CVE.

Les logiciels contiennent au minimum un nom et une version. L’éditeur, le CPE 2.3 et le Package URL sont optionnels. Un CPE exact améliore fortement la confiance du matching.

## API

Toutes les routes exigent un JWT. Les écritures exigent le rôle `admin` ou `analyst`.

| Méthode | Route | Usage |
|---|---|---|
| GET | `/api/assets` | Liste filtrable ; total dans `X-Total-Count` |
| GET | `/api/assets/stats` | Indicateurs synthétiques |
| POST | `/api/assets` | Création d’un actif |
| GET | `/api/assets/{id}` | Détail d’un actif |
| PATCH | `/api/assets/{id}` | Mise à jour partielle |
| DELETE | `/api/assets/{id}` | Suppression de l’actif et de son inventaire enfant |
| GET | `/api/assets/{id}/software` | Logiciels installés |
| POST | `/api/assets/{id}/software` | Ajout d’un logiciel |
| GET | `/api/assets/{id}/vulnerabilities` | Matching recalculé avec les CVE NVD stockées |
| POST | `/api/assets/import` | Import CSV contrôlé |

Filtres de liste : `search`, `asset_type`, `environment`, `criticality`, `internet_exposed`, `limit`, `offset`.

## Import CSV

En-têtes obligatoires :

```csv
hostname,ip_address,asset_type,operating_system,environment,criticality,internet_exposed,owner,description
```

Garde-fous : fichier CSV UTF-8, taille maximale 1 Mio, 500 lignes au maximum, validation indépendante de chaque ligne, adresses IP validées et doublons de hostname ignorés. Le rapport indique `created`, `skipped`, `error_count` et le numéro de chaque ligne invalide.

## Audit

Les actions `asset.create`, `asset.update`, `asset.delete`, `asset.import` et `software.create` sont journalisées. Les détails ne contiennent ni jeton JWT ni clé API.

## Dataset de démonstration entreprise

Un générateur déterministe permet de préparer une démonstration plus volumineuse sans présenter les données comme réelles :

```powershell
cd backend
.\.venv\Scripts\python.exe -m scripts.seed_enterprise_demo
```

Il ajoute, sans doublons, 112 actifs et 406 logiciels répartis entre serveurs, postes, équipements réseau, applications et ressources cloud. Chaque description porte explicitement la mention `Donnée synthétique de démonstration`. Les CVE et alertes ne sont jamais inventées par ce générateur.
