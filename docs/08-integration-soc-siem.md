# Intégration SOC / SIEM

## Positionnement

Sentinel PME reste un système d'alerte précoce « SIEM-light », pas un SIEM
complet. Cette page documente la couche SOC additive construite au-dessus du
MVP : elle rend les alertes exploitables par un analyste et interopérables
avec un SIEM externe, sans remplacer un outil comme Wazuh, Elastic Security
ou Splunk, et sans collecter les journaux internes de l'entreprise.

```text
Collecteurs Threat Intelligence
        ↓
Moteur de scoring (explicable, facteur par facteur)
        ↓
Alertes (score ≥ 70)
        ├── Mini-workflow SOC : statut, assignation, notes d'analyste
        ├── Webhook SOC optionnel, signé HMAC (SOAR, relais Slack/Teams, n8n)
        └── Export SIEM JSON (GET /api/alerts/{id}/siem-event)
                ↓
        SIEM / SOAR externe (Wazuh, Elastic Security, Splunk, Microsoft Sentinel…)
```

## Mini-workflow SOC sur les alertes

Chaque alerte se comporte comme un mini-incident :

- `status` : `new` → `investigating` → `resolved` ou `false_positive`.
- `assigned_to` : identifiant ou email de l'analyste en charge.
- `resolution_notes` : notes libres de l'analyste.

`PATCH /api/alerts/{id}` accepte une mise à jour partielle de ces trois
champs. L'ancien endpoint `PATCH /api/alerts/{id}/acknowledge` reste
disponible pour compatibilité : il marque l'alerte comme acquittée et la
fait passer au statut `resolved`.

## Export SIEM

`GET /api/alerts/{id}/siem-event` renvoie un évènement JSON stable :

```json
{
  "schema_version": "1.0",
  "event_type": "sentinel_pme.threat_alert",
  "generated_at": "2026-10-05T10:00:00Z",
  "alert": { "id": "...", "level": "critical", "status": "new", "...": "..." },
  "threat": { "indicator": "...", "risk_score": 92, "...": "..." },
  "recommended_action": "..."
}
```

Ce format peut être relayé tel quel vers :

- **Wazuh** : via son API HTTP (`/events` d'un intégrateur personnalisé) ou
  un script d'intégration qui lit cet endpoint périodiquement.
- **Elastic Security** : via un pipeline d'ingestion HTTP (Fleet/Elastic
  Agent avec un module HTTP, ou Logstash `http` input) qui transforme ce
  JSON en document `ecs`-like.
- **Splunk** : via un HTTP Event Collector (HEC), en postant ce JSON sur
  `/services/collector/event`.

Deux représentations directement normalisées sont également exposées :

- `GET /api/alerts/{id}/siem-event/elastic` pour Elastic ECS ;
- `GET /api/alerts/{id}/siem-event/wazuh` pour un intégrateur Wazuh.

## Webhook SOC sortant (push)

En complément du mode « pull » ci-dessus, Sentinel PME peut pousser chaque
nouvelle alerte vers un webhook externe (configuré via `WEBHOOK_URL` et,
optionnellement, `WEBHOOK_SECRET` dans `.env`). La charge utile est signée en
HMAC-SHA256 dans l'en-tête `X-Sentinel-Signature` lorsque `WEBHOOK_SECRET`
est défini, afin que le récepteur puisse vérifier l'authenticité de l'envoi.
C'est le point d'entrée le plus simple pour brancher un SOAR interne, un
relais Slack/Teams (via n8n ou Zapier) ou un webhook Wazuh.

Slack, Telegram et SMTP peuvent aussi être configurés directement. Chaque
canal échoue indépendamment afin de ne jamais bloquer la création d'une
alerte. Voir `backend/.env.example` pour les variables.

## Scoring explicable

`GET /api/threats/{id}/explain` renvoie le détail du calcul du score
(sévérité, type d'indicateur, type de menace, fiabilité de la source, bonus
CVE, exploitation active connue, ciblage PME, récence, et bonus de
corrélation multi-sources). Les facteurs sont persistés avec la menace
(`score_factors`) pour rester consultables sans recalcul, et affichés dans le
dashboard sur la page de détail d'une menace.

Le bonus de corrélation multi-sources récompense un indicateur rapporté par
plusieurs sources de veille indépendantes (ex. une IP vue à la fois par
AbuseIPDB et AlienVault OTX), ce qui augmente la confiance dans la menace
sans dupliquer les entrées (la déduplication par `(indicateur, source)` est
conservée).

## Journal d'audit

Les actions sensibles sont journalisées dans la table `audit_logs` :
connexion (`auth.login`), création de compte (`auth.create_user`),
changement de statut d'une alerte (`alert.update`, `alert.acknowledge`) et
déclenchement manuel d'une collecte (`collector.run`). `GET
/api/audit-logs` (réservé à l'administrateur) expose ce journal pour la
traçabilité, exigée par le cahier des charges (séparation des rôles, pas
d'action anonyme sur une ressource sensible).

## Extensions possibles

- Corrélation plus fine (fenêtre temporelle, règles multi-indicateurs).
- Playbooks SOC enrichis générés automatiquement à partir des fiches
  réflexes et du type de menace.
- Règles de corrélation sur les journaux internes d'un SIEM externe.
- Authentification du webhook sortant par mutual TLS en plus de la
  signature HMAC, pour les déploiements les plus exigeants.
