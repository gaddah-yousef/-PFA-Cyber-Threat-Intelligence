# État de l’art

## Pourquoi les PME sont ciblées

Les attaquants recherchent le meilleur rapport entre effort et gain. Une PME peut avoir des correctifs en retard, peu de segmentation réseau, des sauvegardes insuffisamment testées ou une MFA incomplète. Elle peut aussi servir de point d’entrée vers des clients et partenaires plus importants.

## Menaces principales

| Menace | Vecteur courant | Impact possible |
|---|---|---|
| Phishing | Email, faux site, QR code | Vol d’identifiants, fraude |
| Ransomware | Pièce jointe, accès distant, faille | Indisponibilité et perte de données |
| Malware | Téléchargement, document piégé | Espionnage, vol ou destruction |
| Brute force | Services exposés | Compromission de comptes |
| Credential stuffing | Identifiants déjà divulgués | Prise de contrôle de comptes |
| Vulnérabilité critique | Système non corrigé | Exécution de code, intrusion |
| Domaine ou IP malveillant | Infrastructure de commande | Phishing, malware, exfiltration |

## Approches existantes

Les antivirus et EDR protègent les postes, les pare-feu filtrent les communications, les scanners recherchent les vulnérabilités et les SIEM agrègent les événements internes. Les plateformes Threat Intelligence enrichissent ce dispositif avec des informations externes sur l’infrastructure et les tactiques des attaquants.

## Choix du projet

Le projet se place avant et autour de l’incident : il sélectionne des indicateurs publics, les normalise, les priorise et recommande une réponse. Ce positionnement limite la complexité tout en apportant une valeur démontrable à une PME qui ne possède pas de SOC.
