# Compréhension du projet

## Contexte

Les PME disposent souvent de moins de budget, de personnel spécialisé et de temps pour surveiller les menaces que les grandes organisations. Elles restent pourtant exposées aux mêmes campagnes de phishing, rançongiciels, vols d’identifiants et vulnérabilités, avec une capacité de reprise généralement plus faible.

## Problème traité

Les flux de Threat Intelligence sont nombreux, hétérogènes et difficiles à exploiter directement. Le projet transforme une sélection de ces flux en indicateurs normalisés, scores compréhensibles, alertes et actions immédiatement utilisables par une PME.

## Positionnement

Le système est une plateforme de Threat Intelligence et d’alerte précoce avec des fonctions SIEM-light. Contrairement à un SIEM complet, il ne collecte pas en continu tous les événements internes, ne fournit pas un moteur général de corrélation de logs et ne remplace pas un SOC.

## Périmètre du MVP

Le MVP couvre la collecte NVD et URLhaus, un jeu d’exemples local, un modèle de menace commun, un scoring à règles, une base SQL, une API, un dashboard, des alertes simples et des fiches réflexes. Les intégrations OTX, AbuseIPDB, les notifications externes et l’apprentissage automatique sont prévues après validation du socle.

## Critères de réussite

- Une menace suit le même format de bout en bout.
- Le score est reproductible, borné et explicable.
- Les scores élevés déclenchent une alerte persistée.
- Le dashboard rend l’information lisible sans expertise SOC avancée.
- Le projet démarre localement et ses fonctions critiques sont testées.
