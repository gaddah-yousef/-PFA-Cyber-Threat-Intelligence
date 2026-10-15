# Pipeline CI/CD DevSecOps

Cette pipeline automatise les contrôles de qualité et de sécurité de Sentinel PME. Elle ne déploie pas directement sur un serveur : une version validée est publiée sous forme de deux images Docker traçables dans GitHub Container Registry (GHCR).

## Flux de livraison

```text
Branche de travail
       │
       ▼
Pull request
       │
       ├── tests backend + migration Alembic vierge
       ├── lint, tests et build frontend
       ├── audit Python (pip-audit) + SAST (Bandit)
       ├── audit npm des dépendances de production
       ├── détection de secrets (Gitleaks)
       ├── scan dépôt/IaC (Trivy)
       ├── contrôle des nouvelles dépendances
       └── build et scan des images Docker
       │
       ▼
Revue puis fusion dans main
       │
       ▼
Tag vX.Y.Z
       │
       ├── nouvelle barrière qualité/sécurité
       ├── build et scan des images candidates
       ├── SBOM + provenance
       └── publication GHCR avec attestation
```

## Fichiers

- `.github/workflows/ci.yml` : intégration continue à chaque push et pull request.
- `.github/workflows/release.yml` : livraison continue lors d'un tag sémantique, par exemple `v1.2.0`.
- `.github/dependabot.yml` : propositions hebdomadaires de mise à jour pour Python, npm, Docker et GitHub Actions.

Les actions utilisées dans les workflows sont épinglées par SHA. Dependabot propose ensuite leur mise à jour de manière visible et révisable.

## Barrières de sécurité

La CI échoue lorsqu'elle détecte :

- un test, une migration, un lint ou un build en erreur ;
- une vulnérabilité Python connue ;
- une vulnérabilité npm élevée ou critique dans les dépendances livrées au navigateur ;
- un problème Bandit de sévérité et confiance moyennes ou supérieures ;
- un secret présent dans l'historique Git ;
- une vulnérabilité élevée/critique corrigée dans le dépôt ou une image Docker ;
- une nouvelle dépendance vulnérable élevée/critique dans une pull request.

Les dépendances npm de développement sont surveillées par Dependabot, mais ne bloquent pas une livraison tant qu'elles ne sont pas embarquées dans `dist`. Cette séparation évite qu'une alerte sur un outil local impose une migration majeure non maîtrisée, tout en gardant le risque visible.

## Réglages GitHub recommandés

Dans **Settings > Actions > General** :

1. définir les permissions par défaut du `GITHUB_TOKEN` sur **Read repository contents** ;
2. autoriser les actions GitHub et les actions vérifiées utilisées par ces workflows ;
3. ne pas autoriser GitHub Actions à approuver des pull requests.

Dans **Settings > Branches** ou **Rulesets**, protéger `main` et exiger une pull request ainsi que les contrôles suivants :

- `Backend / tests + migration` ;
- `Frontend / lint + tests + build` ;
- `Python / dependencies + SAST` ;
- `Frontend / production dependencies` ;
- `Repository / secret scan` ;
- `Repository / vulnerabilities + misconfigurations` ;
- `Dependency Review / new risks` ;
- `Containers / build + vulnerability scan`.

Pour un dépôt privé, la fonctionnalité GitHub Dependency Review peut nécessiter GitHub Code Security. Si elle n'est pas disponible dans l'offre du dépôt, garder `pip-audit`, `npm audit`, Trivy et Dependabot comme contrôles principaux.

## Publier une version

Créer le tag uniquement depuis une révision validée de `main` :

```powershell
git checkout main
git pull --ff-only
git tag -a v1.0.0 -m "Sentinel PME v1.0.0"
git push origin v1.0.0
```

Le workflow publie alors :

- `ghcr.io/<propriétaire>/<dépôt>-backend:1.0.0` ;
- `ghcr.io/<propriétaire>/<dépôt>-frontend:1.0.0` ;
- les tags `1.0` et `latest` correspondants.

Il utilise uniquement le `GITHUB_TOKEN` temporaire et ne nécessite aucune clé Docker Hub. Aucun token NVD, OTX, AbuseIPDB ou URLhaus n'est lu pendant la CI/CD.

## Étape de déploiement future

Quand la cible sera connue (VPS, Render, Azure, Kubernetes, etc.), ajouter un job distinct avec un environnement GitHub `production`, une approbation obligatoire et des secrets limités à cet environnement. La publication GHCR reste ainsi indépendante du fournisseur d'hébergement.
