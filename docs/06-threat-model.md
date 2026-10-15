# Modèle de données Threat

Chaque menace doit respecter le même format. Ce modèle constitue le contrat de données partagé entre le backend, la base de données, le dashboard et le système d’alertes.

## Exemple

```json
{
  "id": "threat-001",
  "indicator": "malicious-domain.com",
  "indicator_type": "domain",
  "threat_type": "phishing",
  "source": "OTX",
  "severity": "high",
  "risk_score": 85,
  "description": "Suspicious phishing domain targeting business users",
  "recommended_action": "Block domain and alert employees",
  "created_at": "2026-07-08"
}
```

## Définition des champs

| Champ | Type | Description | Exemple |
|---|---|---|---|
| `id` | chaîne | Identifiant unique de la menace | `threat-001` |
| `indicator` | chaîne | Valeur de l’indicateur détecté | `malicious-domain.com` |
| `indicator_type` | chaîne | Nature de l’indicateur | `domain` |
| `threat_type` | chaîne | Catégorie de la menace | `phishing` |
| `source` | chaîne | Source Threat Intelligence | `OTX` |
| `severity` | chaîne | Niveau de sévérité | `high` |
| `risk_score` | entier | Score de risque compris entre 0 et 100 | `85` |
| `description` | chaîne | Description lisible de la menace | `Suspicious phishing domain...` |
| `recommended_action` | chaîne | Action de protection recommandée | `Block domain...` |
| `created_at` | date | Date de création au format ISO `YYYY-MM-DD` | `2026-07-08` |

## Valeurs normalisées

- `indicator_type` : `ip`, `domain`, `url`, `hash` ou `cve`.
- `severity` : `low`, `medium`, `high` ou `critical`.
- `risk_score` : entier de `0` à `100`.
- `created_at` : date au format ISO 8601 `YYYY-MM-DD`.

## Utilisation

Le backend valide et expose les menaces selon ce modèle, tandis que la base de données en conserve les champs. Le dashboard les affiche sans transformation incompatible et le système d’alertes utilise notamment `severity`, `risk_score` et `recommended_action` pour générer les notifications.
