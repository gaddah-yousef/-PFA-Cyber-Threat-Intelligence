# Méthodologie de Risk Scoring

## Objectif

Le score ordonne les menaces selon leur urgence. Il est déterministe, explicable et compris entre 0 et 100 ; il ne prétend pas calculer une probabilité scientifique d’incident.

## Facteurs

| Facteur | Contribution maximale |
|---|---:|
| Sévérité déclarée | 50 |
| Type de menace | 18 |
| Fiabilité de la source | 12 |
| Type d’indicateur | 12 |
| Exploitation connue | 15 |
| Ciblage PME | 10 |
| Récence | 8 |
| Bonus CVE | 5 |

La somme est plafonnée à 100. Une information récente obtient 8 points si elle date de moins de 7 jours, 5 points jusqu’à 30 jours, 2 points jusqu’à 90 jours, puis 0.

## Niveaux

| Score | Niveau | Traitement attendu |
|---:|---|---|
| 0–39 | Faible | Conserver et surveiller |
| 40–69 | Moyen | Vérifier dans le cycle normal |
| 70–89 | Élevé | Créer une alerte et traiter rapidement |
| 90–100 | Critique | Créer une alerte et agir immédiatement |

## Exemple

Une CVE critique NVD, récente, connue comme exploitée et visant des technologies courantes en PME dépasse 100 points bruts. Le score final est plafonné à 100 et classé critique.

## Évolution ML

Un futur module Scikit-learn pourra apprendre à partir des validations analystes. Il devra compléter le score à règles, conserver une explication compréhensible et être comparé au moteur actuel avant toute activation.
