# Sources Threat Intelligence — V1

Pour la première version du MVP, la collecte est limitée à trois sources afin de garantir une intégration simple, fiable et correctement normalisée.

| Source | Données collectées | Pourquoi |
|---|---|---|
| NVD / CVE | Vulnérabilités, scores CVSS et sévérité | Identifier les vulnérabilités critiques |
| URLhaus | URLs associées à des malwares | Détecter les liens et ressources malveillants |
| AlienVault OTX | Adresses IP, domaines et autres IOCs | Identifier les infrastructures malveillantes |

## Choix pour la V1

AlienVault OTX est retenu à la place d’AbuseIPDB, car il permet de collecter à la fois des adresses IP et des domaines malveillants. AbuseIPDB pourra être ajouté dans une version ultérieure pour enrichir la réputation des adresses IP.

## Principe de mise en œuvre

L’objectif de la V1 n’est pas de multiplier les intégrations, mais de construire trois collecteurs propres, testables et robustes. Toutes les données devront être validées, dédupliquées et converties dans un format commun avant leur analyse.
