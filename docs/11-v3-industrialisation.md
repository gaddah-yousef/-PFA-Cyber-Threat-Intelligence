# Sentinel PME V3 — interopérabilité et industrialisation

## Ce qui est livré

La V3 reste une plateforme de Threat Intelligence et de SOC léger. Elle ne
devient pas un collecteur généraliste de journaux, mais elle peut échanger ses
indicateurs et alertes avec les outils d'entreprise :

- export STIX 2.1 : `GET /api/intelligence/export/stix` ;
- export MISP JSON : `GET /api/intelligence/export/misp` ;
- serveur TAXII 2.1 en lecture seule : découverte `/taxii2/`, API Root `/api/taxii2/` ;
- événements Elastic ECS : `GET /api/alerts/{id}/siem-event/elastic` ;
- événements Wazuh : `GET /api/alerts/{id}/siem-event/wazuh` ;
- corrélations multi-sources : `GET /api/intelligence/correlations` ;
- anomalies de score explicables : `GET /api/intelligence/anomalies`.

Les exports nécessitent un JWT. STIX utilise des identifiants déterministes.
Les CVE deviennent des objets `vulnerability`, les IP/domaines/URL/hash des
objets `indicator`. L'export MISP reste non publié et en distribution locale
(`0`) : un analyste doit le relire avant partage.

## Corrélation et analyse expérimentale

La corrélation groupe le même indicateur observé par plusieurs sources. Elle
retourne les sources, les menaces liées, le score maximal et une confiance
bornée. Il ne s'agit pas d'une corrélation de logs SIEM.

La détection d'anomalies applique la médiane et le MAD aux scores stockés. Un
résultat contient le score observé, la médiane, le MAD, le score-z robuste et
une explication. Elle aide au tri sans prendre de décision automatique.

## Notifications

Chaque alerte de score supérieur ou égal à 70 peut être envoyée sur les canaux
configurés : webhook HMAC, Slack, Telegram, email SMTP, passerelle Wazuh et
endpoint d'ingestion Elastic. Les variables sont
documentées dans `backend/.env.example`. Les canaux sont indépendants : une
panne externe n'annule ni l'alerte ni les autres envois, et aucun secret n'est
inclus dans les logs.

## Exploitation

- `GET /health` : liveness ;
- `GET /health/ready` : vérifie aussi la base ;
- `GET /metrics` : métriques HTTP Prometheus ;
- logs JSON hors développement et `X-Request-ID` sur chaque réponse ;
- `scripts/backup_database.py` : sauvegarde SQLite cohérente avec rotation ;
- Redis/RQ : `POST /api/collectors/{name}/enqueue`, puis
  `GET /api/collectors/jobs/{job_id}`.

Le profil [`docker-compose.prod.yml`](../docker-compose.prod.yml) utilise
PostgreSQL, Redis, un worker RQ, FastAPI et Nginx. La CI vérifie le backend sur
SQLite et PostgreSQL.

## Références

- [STIX 2.1 — OASIS](https://docs.oasis-open.org/cti/stix/v2.1/os/)
- [MISP core format](https://www.misp-project.org/datamodels/)
- [Elastic Common Schema](https://www.elastic.co/guide/en/ecs/current/)
- [Slack Incoming Webhooks](https://api.slack.com/incoming-webhooks)
- [Telegram Bot API](https://core.telegram.org/bots/api)
