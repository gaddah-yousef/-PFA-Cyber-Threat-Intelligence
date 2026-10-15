# Sources de Threat Intelligence

| Source | Type de données | Utilisation | Statut MVP |
|---|---|---|---|
| NVD / CVE | Vulnérabilités et scores CVSS | Identifier les failles critiques | Collecteur disponible |
| CISA KEV | Vulnérabilités exploitées | Prioriser les CVE dangereuses | Évolution prévue |
| URLhaus | URLs associées à des malwares | Identifier les liens malveillants | Collecteur disponible |
| AlienVault OTX | IP, domaines, hashes et pulses | Corréler plusieurs IOCs | Évolution prévue |
| AbuseIPDB | Réputation d’adresses IP | Détecter les IP suspectes | Évolution prévue |
| PhishTank | URLs de phishing | Détecter les faux sites | Évolution prévue |
| MISP | Partage structuré de menaces | Échanger et corréler les IOCs | Intégration future |

## Sources retenues

La V1 privilégie trois flux propres plutôt qu’un grand nombre d’intégrations fragiles : le jeu d’exemples local pour les démonstrations reproductibles, URLhaus pour les URLs malware et NVD pour les CVE. AlienVault OTX est le prochain connecteur prioritaire afin d’ajouter les domaines et IP malveillants.

## Règles d’intégration

Chaque collecteur implémente le même contrat et retourne des objets `ThreatInput`. Les secrets éventuels sont fournis par variables d’environnement, les erreurs réseau ne bloquent pas le démarrage, et aucune collecte externe n’est exécutée automatiquement au lancement du MVP.

## Limites

La qualité d’un indicateur dépend de sa source, de sa fraîcheur et de son contexte. Une présence dans un flux ne prouve pas à elle seule une compromission ; le score facilite la priorisation mais une validation humaine reste recommandée.
