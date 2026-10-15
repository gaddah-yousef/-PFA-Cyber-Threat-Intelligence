# Documentation de l’API

L’API FastAPI est accessible par défaut sur `http://localhost:8000`. Swagger est disponible sur `/docs` et le schéma OpenAPI sur `/openapi.json`.

## Endpoints

| Méthode | Chemin | Description |
|---|---|---|
| GET | `/` | Informations générales |
| GET | `/health` | État du service |
| GET | `/api/threats` | Liste filtrable des menaces |
| GET | `/api/threats/{id}` | Détail d’une menace |
| POST | `/api/threats/analyze` | Analyse, enrichissement et sauvegarde |
| POST | `/api/threats/manual` | Ajout manuel forcé à la source `manual` |
| GET | `/api/threats/critical` | Menaces dont le score est au moins 90 |
| GET | `/api/stats` | Compteurs du dashboard |
| GET | `/api/reflex-sheets` | Toutes les fiches réflexes |
| GET | `/api/reflex-sheets/{type}` | Fiche d’un type de menace |
| GET | `/api/alerts` | Alertes récentes |
| POST | `/api/alerts/test` | Alerte de test |

## Exemple d’analyse

```bash
curl -X POST http://localhost:8000/api/threats/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "indicator": "malicious-domain.example",
    "indicator_type": "domain",
    "threat_type": "phishing",
    "source": "otx",
    "severity": "high",
    "description": "Domaine de phishing ciblant des comptes professionnels",
    "targets_smes": true
  }'
```

La réponse ajoute `id`, `risk_score`, `risk_level`, `recommended_action` et les dates. Les erreurs de validation utilisent le format standard FastAPI avec le statut HTTP 422.

## Filtres

`GET /api/threats` accepte `risk_level`, `threat_type`, `source`, `search`, `limit` et `offset`. Les limites sont validées côté serveur et le nombre maximal de résultats par requête est 500.
