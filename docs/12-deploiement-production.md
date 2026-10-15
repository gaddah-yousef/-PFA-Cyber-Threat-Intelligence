# Runbook de déploiement production

## Préconditions

- serveur Linux avec Docker Engine et Compose ;
- nom DNS et reverse proxy TLS ;
- secrets générés et jamais copiés dans Git ;
- stockage de sauvegarde distinct du serveur.

## Configuration

Copier `.env.example` vers `.env` sur le serveur et remplacer au minimum
`PUBLIC_ORIGIN`, `POSTGRES_PASSWORD`, `JWT_SECRET_KEY`, `ADMIN_EMAIL` et
`ADMIN_PASSWORD`. Ajouter uniquement les clés des collecteurs et canaux
réellement utilisés. Le backend refuse les secrets et le mot de passe
administrateur de démonstration en production.

## Démarrage et contrôle

```bash
docker compose -f docker-compose.prod.yml config
docker compose -f docker-compose.prod.yml build --pull
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
curl --fail http://127.0.0.1/health/ready
```

Le frontend écoute sur `HTTP_PORT` (80 par défaut) et relaie `/api` vers le
backend. PostgreSQL et Redis ne sont pas publiés sur l'hôte.

## Sauvegarde PostgreSQL

```bash
mkdir -p backups
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U sentinel -d sentinel -Fc > backups/sentinel-$(date -u +%Y%m%dT%H%M%SZ).dump
```

Copier ensuite le fichier vers un stockage chiffré distinct. Tester la
restauration dans une base isolée avec `pg_restore`.

## Mise à jour et retour arrière

1. sauvegarder PostgreSQL ;
2. récupérer une version Git étiquetée ;
3. reconstruire puis lancer `up -d` ;
4. vérifier readiness, connexion et collecte `sample` ;
5. en cas d'échec applicatif, redéployer l'étiquette précédente.

Une validation publique exige encore un serveur, un domaine/TLS et les comptes
externes. Ces accès ne peuvent pas être inventés dans le dépôt.
