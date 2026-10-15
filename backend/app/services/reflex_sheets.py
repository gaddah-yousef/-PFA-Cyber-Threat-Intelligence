"""Procédures courtes de réponse à incident adaptées aux PME.

Les actions restent volontairement indépendantes des produits utilisés. Elles doivent
être adaptées au système d'information, aux contrats et aux obligations de l'entreprise.
"""

DGSSI_REFERENCE = {
    "label": "DGSSI — Référentiel de gestion des incidents de cybersécurité",
    "url": "https://www.dgssi.gov.ma/sites/default/files/publications/pdf/2023-06/referentiel_de_gestion_des_incidents.pdf",
}

NIST_REFERENCE = {
    "label": "NIST SP 800-61 Rev. 3 — Incident Response",
    "url": "https://csrc.nist.gov/pubs/sp/800/61/r3/final",
}

MACERT_REFERENCE = {
    "label": "DGSSI — maCERT, appui à la réponse aux incidents",
    "url": "https://www.dgssi.gov.ma/index.php/fr/macert",
}


REFLEX_SHEETS: dict[str, dict[str, object]] = {
    "phishing": {
        "title": "Réagir à une campagne de phishing",
        "summary": "Limiter le vol d’identifiants, stopper la diffusion du message et rechercher les comptes déjà compromis.",
        "priority": "élevée",
        "owner": "Responsable informatique ou prestataire IT",
        "reviewed_at": "2026-10-07",
        "actions": [
            "Conserver le message original et ses en-têtes",
            "Bloquer le domaine, l’URL et l’expéditeur malveillants",
            "Identifier les destinataires et les personnes ayant interagi",
            "Réinitialiser les identifiants compromis et révoquer les sessions",
            "Activer ou renforcer l’authentification multifacteur (MFA)",
        ],
        "sections": [
            {
                "title": "Actions immédiates",
                "timeframe": "0–15 min",
                "actions": [
                    "Demander au déclarant de ne plus cliquer et de ne pas supprimer le message.",
                    "Exporter le message original au format EML/MSG avec ses en-têtes complets.",
                    "Si un fichier a été ouvert, isoler le poste du réseau sans l’éteindre.",
                    "Si un mot de passe a été saisi, réinitialiser le compte depuis un poste sain et révoquer les sessions actives.",
                ],
            },
            {
                "title": "Qualifier et contenir",
                "timeframe": "15–60 min",
                "actions": [
                    "Rechercher le même objet, expéditeur, URL ou pièce jointe dans la messagerie.",
                    "Retirer le message des boîtes concernées et bloquer les indicateurs sur la messagerie, le DNS et le proxy.",
                    "Contrôler les connexions inhabituelles, règles de transfert, applications OAuth et changements MFA du compte.",
                    "Prévenir les collaborateurs avec une capture et des consignes simples, sans retransmettre le lien actif.",
                ],
            },
            {
                "title": "Éradiquer et surveiller",
                "timeframe": "Après confinement",
                "actions": [
                    "Analyser le poste si une pièce jointe ou une page malveillante a été ouverte.",
                    "Changer les secrets réutilisés sur d’autres services et vérifier les comptes à privilèges.",
                    "Surveiller pendant au moins 72 heures les connexions, règles email et nouvelles alertes liées aux indicateurs.",
                    "Documenter le scénario et ajuster les filtres ainsi que la sensibilisation interne.",
                ],
            },
        ],
        "evidence_to_preserve": [
            "Message original, en-têtes SMTP, URL et pièces jointes avec leurs empreintes.",
            "Journaux de connexion du compte, passerelle email, proxy, DNS et EDR/antivirus.",
            "Heure des clics, identités des destinataires et actions déjà réalisées.",
        ],
        "escalation_criteria": [
            "Un utilisateur a communiqué un mot de passe, validé une MFA ou ouvert une pièce jointe.",
            "Un compte administrateur, financier ou de direction est concerné.",
            "Des connexions anormales, règles de transfert ou envois frauduleux sont détectés.",
        ],
        "do_not": [
            "Ne pas supprimer le message avant d’en avoir conservé une copie exploitable.",
            "Ne pas demander à l’utilisateur de changer son mot de passe depuis le poste potentiellement compromis.",
        ],
        "references": [
            {
                "label": "Cybermalveillance.gouv.fr — Hameçonnage (phishing)",
                "url": "https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/hameconnage-phishing/2e844784-f440-418c-8d8e-ed5556bb2376",
            },
            DGSSI_REFERENCE,
            NIST_REFERENCE,
        ],
    },
    "malware": {
        "title": "Réagir à une infection par malware",
        "summary": "Empêcher la propagation, préserver les traces et reconstruire l’équipement à partir d’une source saine.",
        "priority": "élevée",
        "owner": "Support informatique ou prestataire de réponse à incident",
        "reviewed_at": "2026-10-07",
        "actions": [
            "Isoler l’équipement affecté sans l’éteindre",
            "Évaluer l’étendue de l’infection sur le réseau",
            "Bloquer les indicateurs et comptes associés",
            "Rechercher les mécanismes de persistance",
            "Reconstruire depuis une image ou sauvegarde saine",
        ],
        "sections": [
            {
                "title": "Actions immédiates",
                "timeframe": "0–15 min",
                "actions": [
                    "Débrancher le câble réseau et couper Wi-Fi/Bluetooth sans éteindre l’appareil.",
                    "Interdire toute saisie de mot de passe ou opération sensible sur l’équipement.",
                    "Noter l’heure, l’utilisateur, les symptômes et les alertes antivirus visibles.",
                    "Alerter le responsable informatique et ouvrir un journal chronologique de l’incident.",
                ],
            },
            {
                "title": "Qualifier et contenir",
                "timeframe": "15–60 min",
                "actions": [
                    "Identifier le fichier, processus, hash, domaine et adresse IP associés à la détection.",
                    "Rechercher ces indicateurs sur les autres postes, serveurs, journaux DNS, proxy et EDR.",
                    "Désactiver les comptes utilisés depuis la machine si un vol d’identifiants est possible.",
                    "Conserver une image disque et, si les compétences existent, une capture mémoire avant nettoyage.",
                ],
            },
            {
                "title": "Éradiquer et restaurer",
                "timeframe": "Après confinement",
                "actions": [
                    "Supprimer la cause initiale : logiciel vulnérable, pièce jointe, compte compromis ou service exposé.",
                    "Privilégier une réinstallation complète pour une infection confirmée plutôt qu’un simple nettoyage.",
                    "Restaurer uniquement des données vérifiées et appliquer les correctifs avant reconnexion.",
                    "Surveiller les indicateurs, comptes et flux réseau pendant la période définie par l’entreprise.",
                ],
            },
        ],
        "evidence_to_preserve": [
            "Image disque ou copie des fichiers suspects et empreintes cryptographiques.",
            "Alertes antivirus/EDR, liste des processus, connexions réseau et tâches planifiées.",
            "Journaux système, authentification, DNS, proxy et pare-feu autour de l’heure de détection.",
        ],
        "escalation_criteria": [
            "Plusieurs équipements, un serveur ou un compte privilégié sont touchés.",
            "Le malware vole des données, chiffre des fichiers ou communique encore avec l’extérieur.",
            "L’origine et la persistance ne peuvent pas être déterminées avec les moyens internes.",
        ],
        "do_not": [
            "Ne pas reconnecter un poste simplement parce que l’antivirus indique une suppression réussie.",
            "Ne pas détruire les fichiers suspects et journaux avant leur copie et leur horodatage.",
        ],
        "references": [
            {
                "label": "Cybermalveillance.gouv.fr — Virus informatique, que faire ?",
                "url": "https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/virus-informatiques",
            },
            DGSSI_REFERENCE,
            NIST_REFERENCE,
        ],
    },
    "ransomware": {
        "title": "Réagir à un ransomware",
        "summary": "Stopper le chiffrement et les mouvements latéraux, protéger les sauvegardes et organiser une reprise maîtrisée.",
        "priority": "critique",
        "owner": "Direction de crise et responsable informatique",
        "reviewed_at": "2026-10-07",
        "actions": [
            "Isoler immédiatement les systèmes et segments affectés",
            "Protéger les sauvegardes et infrastructures d’administration",
            "Préserver les preuves avant toute reconstruction",
            "Évaluer l’exfiltration de données et les obligations de notification",
            "Restaurer les services prioritaires sur un environnement sain",
        ],
        "sections": [
            {
                "title": "Actions immédiates",
                "timeframe": "0–15 min",
                "actions": [
                    "Déconnecter les machines touchées du réseau ; si la propagation est large, isoler les segments au niveau des commutateurs.",
                    "Couper les accès distants exposés et protéger immédiatement les consoles de sauvegarde, hyperviseurs et comptes d’administration.",
                    "Conserver les appareils allumés si l’isolement réseau est possible ; les éteindre seulement si aucun autre confinement n’est réalisable.",
                    "Déclencher la cellule de crise et utiliser un canal de communication hors du système potentiellement compromis.",
                ],
            },
            {
                "title": "Qualifier et contenir",
                "timeframe": "15–60 min",
                "actions": [
                    "Cartographier les systèmes chiffrés, comptes utilisés, données critiques et services encore opérationnels.",
                    "Collecter une note de rançon, un fichier chiffré exemple, les logs et une capture mémoire d’un échantillon de machines.",
                    "Rechercher l’accès initial, les outils de mouvement latéral, l’exfiltration et les comptes créés ou modifiés.",
                    "Prioriser la continuité des fonctions vitales et informer direction, assurance cyber et assistance spécialisée.",
                ],
            },
            {
                "title": "Éradiquer et restaurer",
                "timeframe": "Après confinement",
                "actions": [
                    "Reconstruire les systèmes dans un réseau sain, corriger le point d’entrée et renouveler les secrets compromis.",
                    "Tester les sauvegardes hors ligne avant restauration et rétablir les services selon leur criticité métier.",
                    "Reconnecter progressivement avec une surveillance renforcée et des critères de validation documentés.",
                    "Évaluer l’éventuelle violation de données et appliquer les obligations légales et contractuelles pertinentes.",
                ],
            },
        ],
        "evidence_to_preserve": [
            "Note de rançon, extensions de fichiers, échantillons chiffrés et binaires suspects.",
            "Images disque/mémoire, journaux EDR, Active Directory, VPN, pare-feu, proxy et sauvegardes.",
            "Chronologie des décisions, systèmes affectés et communications avec l’attaquant le cas échéant.",
        ],
        "escalation_criteria": [
            "Le chiffrement touche plusieurs systèmes, un serveur, les sauvegardes ou une fonction métier critique.",
            "Une exfiltration ou une divulgation de données est annoncée ou détectée.",
            "L’entreprise ne peut plus assurer un service essentiel ou restaurer seule dans ses délais acceptables.",
        ],
        "do_not": [
            "Ne pas payer ni contacter l’attaquant sans décision de crise, conseil juridique et autorités compétentes.",
            "Ne pas lancer une restauration massive avant d’avoir fermé le point d’entrée et assaini l’administration.",
        ],
        "references": [
            {
                "label": "Cybermalveillance.gouv.fr — Rançongiciel : que faire ?",
                "url": "https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/rancongiciels-ransomwares",
            },
            {
                "label": "CISA — StopRansomware Guide",
                "url": "https://www.cisa.gov/stopransomware/ransomware-guide",
            },
            DGSSI_REFERENCE,
        ],
    },
    "brute_force": {
        "title": "Réagir à une attaque par force brute",
        "summary": "Stopper les tentatives, déterminer si un compte a été utilisé et corriger la faiblesse d’authentification.",
        "priority": "élevée",
        "owner": "Administrateur systèmes et identités",
        "reviewed_at": "2026-10-07",
        "actions": [
            "Limiter ou bloquer la source des tentatives",
            "Protéger les comptes ciblés et révoquer les sessions suspectes",
            "Rechercher toute authentification réussie après les échecs",
            "Imposer la MFA et des règles de limitation adaptées",
            "Surveiller les connexions et changements de privilèges",
        ],
        "sections": [
            {
                "title": "Actions immédiates",
                "timeframe": "0–15 min",
                "actions": [
                    "Identifier le service, les comptes ciblés, la période et les adresses sources.",
                    "Appliquer une limitation temporaire ou un blocage ciblé sans rendre le service indisponible aux utilisateurs légitimes.",
                    "Verrouiller ou réinitialiser les comptes pour lesquels une connexion suspecte a réussi.",
                    "Révoquer les sessions et jetons actifs des comptes compromis.",
                ],
            },
            {
                "title": "Qualifier et contenir",
                "timeframe": "15–60 min",
                "actions": [
                    "Corréler les échecs avec les authentifications réussies, changements MFA et élévations de privilèges.",
                    "Vérifier si les mêmes identifiants sont utilisés sur VPN, messagerie, cloud ou applications métiers.",
                    "Rechercher les connexions depuis des pays, appareils ou horaires inhabituels.",
                    "Activer la MFA et ajuster les seuils de verrouillage, CAPTCHA ou rate limiting selon le service.",
                ],
            },
            {
                "title": "Corriger et surveiller",
                "timeframe": "Après confinement",
                "actions": [
                    "Supprimer les comptes inutiles et réduire les interfaces d’administration exposées à Internet.",
                    "Imposer des mots de passe uniques et rechercher les secrets exposés ou réutilisés.",
                    "Créer des alertes sur les rafales d’échecs suivies d’une réussite et sur les connexions à privilèges.",
                    "Documenter les sources, comptes touchés et mesures durables mises en place.",
                ],
            },
        ],
        "evidence_to_preserve": [
            "Journaux complets d’authentification, VPN, SSO, annuaire et application ciblée.",
            "Adresses IP, user-agents, identifiants visés et heures précises des tentatives.",
            "Historique des sessions, modifications MFA et changements de privilèges.",
        ],
        "escalation_criteria": [
            "Une authentification a réussi ou un compte privilégié est ciblé.",
            "Les tentatives proviennent de nombreuses sources ou contournent les protections.",
            "Des actions ont été réalisées après connexion : export, création de compte ou modification de règles.",
        ],
        "do_not": [
            "Ne pas bloquer une plage réseau entière sans vérifier l’impact métier.",
            "Ne pas considérer l’incident clos après le seul changement de mot de passe.",
        ],
        "references": [
            {
                "label": "Cybermalveillance.gouv.fr — Piratage de compte, que faire ?",
                "url": "https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/piratage-de-compte",
            },
            DGSSI_REFERENCE,
            NIST_REFERENCE,
        ],
    },
    "vulnerability": {
        "title": "Traiter une vulnérabilité critique",
        "summary": "Confirmer l’exposition, réduire immédiatement la surface d’attaque et corriger sans interrompre inutilement le métier.",
        "priority": "élevée",
        "owner": "Responsable infrastructure ou propriétaire de l’application",
        "reviewed_at": "2026-10-07",
        "actions": [
            "Identifier les versions et actifs réellement exposés",
            "Vérifier l’exploitation active et les mesures de contournement",
            "Isoler ou limiter l’accès si le correctif ne peut pas être immédiat",
            "Tester puis déployer le correctif de sécurité",
            "Rechercher des traces d’exploitation antérieures",
        ],
        "sections": [
            {
                "title": "Évaluer l’urgence",
                "timeframe": "0–4 h",
                "actions": [
                    "Confirmer le produit, la version, la configuration vulnérable et l’exposition Internet ou interne.",
                    "Vérifier les avis de l’éditeur, le catalogue CISA KEV et l’existence d’une exploitation connue.",
                    "Identifier les données, comptes et fonctions métier accessibles via l’actif.",
                    "Décider d’une mesure immédiate : filtrage, désactivation de fonction, restriction VPN ou isolement.",
                ],
            },
            {
                "title": "Corriger et contrôler",
                "timeframe": "Dans la journée",
                "actions": [
                    "Sauvegarder la configuration et tester le correctif sur un environnement représentatif si possible.",
                    "Déployer selon la priorité des actifs et vérifier la version effectivement installée.",
                    "Rechercher dans les journaux les requêtes, processus, comptes ou fichiers correspondant à une exploitation.",
                    "Conserver la mesure compensatoire jusqu’à la validation technique et métier.",
                ],
            },
            {
                "title": "Valider la remédiation",
                "timeframe": "Après correction",
                "actions": [
                    "Scanner de nouveau l’actif et confirmer que le service attendu fonctionne.",
                    "Si une exploitation est suspectée, traiter l’actif comme compromis et lancer une investigation complète.",
                    "Mettre à jour l’inventaire, la preuve de déploiement et les exceptions restantes.",
                    "Analyser pourquoi l’actif n’a pas été corrigé plus tôt et améliorer le processus de patch management.",
                ],
            },
        ],
        "evidence_to_preserve": [
            "Inventaire des versions, exposition réseau et configuration avant/après correction.",
            "Avis éditeur, CVE, score, statut KEV et date de disponibilité du correctif.",
            "Journaux applicatifs, WAF, proxy, système et EDR couvrant la période d’exposition.",
        ],
        "escalation_criteria": [
            "La vulnérabilité est exploitée activement, figure dans KEV ou permet une exécution de code distante.",
            "Un actif Internet, critique ou contenant des données sensibles est concerné.",
            "Aucun correctif ou contournement fiable n’est disponible.",
        ],
        "do_not": [
            "Ne pas se baser uniquement sur le score CVSS sans tenir compte de l’exposition et de l’exploitation active.",
            "Ne pas annoncer la correction sans vérifier la version déployée et l’absence de traces d’exploitation.",
        ],
        "references": [
            {
                "label": "CISA — Known Exploited Vulnerabilities Catalog",
                "url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
            },
            {
                "label": "CISA — Incident and Vulnerability Response Playbooks",
                "url": "https://www.cisa.gov/news-events/news/federal-government-cybersecurity-incident-and-vulnerability-response-playbooks",
            },
            DGSSI_REFERENCE,
        ],
    },
    "suspicious_ip": {
        "title": "Analyser une adresse IP suspecte",
        "summary": "Qualifier l’activité dans son contexte avant de bloquer, puis rechercher tous les actifs qui ont communiqué avec cette adresse.",
        "priority": "modérée",
        "owner": "Analyste sécurité ou administrateur réseau",
        "reviewed_at": "2026-10-07",
        "actions": [
            "Qualifier la réputation et le contexte de l’adresse IP",
            "Rechercher ses connexions dans les journaux",
            "Identifier les actifs internes concernés",
            "Bloquer temporairement si l’activité malveillante est confirmée",
            "Surveiller les indicateurs associés",
        ],
        "sections": [
            {
                "title": "Qualifier le signal",
                "timeframe": "0–30 min",
                "actions": [
                    "Vérifier la source du signal, sa date, sa confiance et le type d’activité rapporté.",
                    "Déterminer si l’adresse appartient à un service légitime partagé, un VPN, un CDN ou un scanner connu.",
                    "Rechercher l’adresse dans les flux pare-feu, proxy, DNS, VPN, serveur et EDR.",
                    "Identifier le sens, le volume, les ports, les comptes et les actifs associés aux communications.",
                ],
            },
            {
                "title": "Contenir si confirmé",
                "timeframe": "30–60 min",
                "actions": [
                    "Bloquer l’adresse avec une durée et un propriétaire définis, après vérification de l’impact.",
                    "Isoler les actifs ayant établi une communication suspecte et rechercher les indicateurs liés.",
                    "Vérifier si la communication correspond à un scan, une authentification, une commande distante ou une exfiltration.",
                    "Ajouter les domaines, URL ou empreintes associés aux règles de détection pertinentes.",
                ],
            },
            {
                "title": "Surveiller et clôturer",
                "timeframe": "Après confinement",
                "actions": [
                    "Surveiller les tentatives via d’autres adresses et les actifs déjà contactés.",
                    "Documenter les éléments confirmant ou infirmant le caractère malveillant.",
                    "Retirer le blocage à l’échéance s’il n’est plus justifié, afin d’éviter les règles permanentes oubliées.",
                    "Marquer le signal comme faux positif si le service est légitime et tracer la justification.",
                ],
            },
        ],
        "evidence_to_preserve": [
            "Événement source ayant signalé l’adresse, avec date et niveau de confiance.",
            "Flux réseau, journaux pare-feu/proxy/VPN et actifs internes correspondants.",
            "Résultats de réputation datés et liste des indicateurs associés.",
        ],
        "escalation_criteria": [
            "Une communication sortante persistante, un transfert de données ou une commande distante est observé.",
            "Un serveur critique, un compte privilégié ou plusieurs actifs sont concernés.",
            "L’adresse est liée à un ransomware, un serveur de commande et contrôle ou une exploitation active.",
        ],
        "do_not": [
            "Ne pas bloquer sur la seule base d’une réputation ancienne ou d’une source unique.",
            "Ne pas oublier qu’une adresse partagée peut héberger des services légitimes.",
        ],
        "references": [
            {
                "label": "ANSSI — Recommandations pour l’architecture d’un système de journalisation",
                "url": "https://messervices.cyber.gouv.fr/guides/recommandations-de-securite-pour-larchitecture-dun-systeme-de-journalisation",
            },
            DGSSI_REFERENCE,
            NIST_REFERENCE,
        ],
    },
    "account_compromise": {
        "title": "Traiter un compte compromis",
        "summary": "Reprendre le contrôle du compte, couper les accès persistants et mesurer les actions réalisées par l’attaquant.",
        "priority": "critique",
        "owner": "Administrateur des identités et propriétaire métier",
        "reviewed_at": "2026-10-07",
        "actions": [
            "Suspendre le compte ou bloquer les connexions",
            "Révoquer toutes les sessions et jetons actifs",
            "Réinitialiser le mot de passe depuis un appareil sain",
            "Contrôler MFA, délégations, règles et applications autorisées",
            "Examiner les actions réalisées pendant la compromission",
        ],
        "sections": [
            {
                "title": "Reprendre le contrôle",
                "timeframe": "0–15 min",
                "actions": [
                    "Suspendre temporairement le compte si l’impact métier le permet.",
                    "Révoquer sessions, jetons, mots de passe d’application et clés API liés au compte.",
                    "Réinitialiser le mot de passe depuis un appareil sain et imposer une nouvelle inscription MFA.",
                    "Prévenir le propriétaire du compte par un canal différent de celui qui est compromis.",
                ],
            },
            {
                "title": "Mesurer l’activité",
                "timeframe": "15–60 min",
                "actions": [
                    "Examiner les connexions, appareils, pays, applications OAuth et changements de sécurité.",
                    "Contrôler les règles email, délégations, transferts, exports et messages envoyés.",
                    "Rechercher les opérations réalisées avec ce compte sur les applications métiers et le cloud.",
                    "Identifier l’origine : phishing, mot de passe réutilisé, malware ou mauvaise configuration.",
                ],
            },
            {
                "title": "Restaurer la confiance",
                "timeframe": "Après confinement",
                "actions": [
                    "Supprimer les mécanismes de persistance et restaurer les paramètres légitimes.",
                    "Faire changer les secrets réutilisés et contrôler les appareils de l’utilisateur.",
                    "Réactiver le compte avec le minimum de privilèges et une surveillance renforcée.",
                    "Informer les destinataires si des messages frauduleux ont été envoyés depuis le compte.",
                ],
            },
        ],
        "evidence_to_preserve": [
            "Historique des connexions, sessions, appareils et événements MFA.",
            "Règles email, délégations, applications OAuth et modifications de privilèges.",
            "Messages ou transactions réalisés par l’attaquant et chronologie des actions de reprise.",
        ],
        "escalation_criteria": [
            "Le compte possède des droits d’administration, de paiement ou d’accès à des données sensibles.",
            "L’attaquant a créé une persistance, exporté des données ou compromis d’autres comptes.",
            "La compromission implique un appareil infecté ou un vol massif d’identifiants.",
        ],
        "do_not": [
            "Ne pas se limiter au changement du mot de passe sans révoquer les sessions et jetons.",
            "Ne pas utiliser la messagerie compromise pour coordonner la réponse.",
        ],
        "references": [
            {
                "label": "Cybermalveillance.gouv.fr — Piratage de compte",
                "url": "https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/piratage-de-compte",
            },
            DGSSI_REFERENCE,
            NIST_REFERENCE,
        ],
    },
    "data_breach": {
        "title": "Réagir à une fuite de données",
        "summary": "Stopper l’accès non autorisé, déterminer précisément les données concernées et préparer les notifications applicables.",
        "priority": "critique",
        "owner": "Direction, responsable sécurité et conseil juridique/DPO",
        "reviewed_at": "2026-10-07",
        "actions": [
            "Fermer l’accès non autorisé sans détruire les traces",
            "Identifier les données, personnes et systèmes concernés",
            "Préserver les preuves et établir une chronologie",
            "Évaluer les impacts métier, contractuels et humains",
            "Déclencher les notifications légales applicables",
        ],
        "sections": [
            {
                "title": "Contenir la fuite",
                "timeframe": "0–30 min",
                "actions": [
                    "Révoquer le lien, jeton, clé ou compte exposé et limiter l’accès à la ressource.",
                    "Conserver l’état et les journaux avant toute suppression ou modification importante.",
                    "Informer direction, sécurité et responsable juridique/DPO selon l’organisation.",
                    "Empêcher une nouvelle extraction tout en maintenant les preuves disponibles.",
                ],
            },
            {
                "title": "Qualifier l’impact",
                "timeframe": "30 min–4 h",
                "actions": [
                    "Déterminer les catégories, volumes, propriétaires et sensibilité des données.",
                    "Identifier qui a accédé, depuis où, pendant quelle période et quelles copies ont été réalisées.",
                    "Évaluer les conséquences pour les personnes, les clients, les partenaires et l’activité.",
                    "Consigner les faits connus, incertitudes, décisions et mesures prises dans un registre d’incident.",
                ],
            },
            {
                "title": "Notifier et corriger",
                "timeframe": "Selon obligations",
                "actions": [
                    "Vérifier les obligations auprès de l’autorité compétente, des clients, assureurs et partenaires.",
                    "Lorsque le RGPD s’applique et qu’un risque existe, préparer une notification initiale dans les 72 heures si possible.",
                    "Corriger la cause : droits excessifs, stockage public, secret exposé ou compte compromis.",
                    "Surveiller les usages frauduleux et informer les personnes concernées lorsque la réglementation ou le risque l’exige.",
                ],
            },
        ],
        "evidence_to_preserve": [
            "Journaux d’accès, exports, téléchargements, partages et changements de permissions.",
            "Copie de la configuration exposée et inventaire daté des données concernées.",
            "Chronologie, décisions, analyse de risque et communications envoyées.",
        ],
        "escalation_criteria": [
            "Des données personnelles, financières, de santé, d’authentification ou des secrets sont concernés.",
            "Le volume, la durée ou les destinataires de l’exposition ne sont pas connus.",
            "Une obligation réglementaire, contractuelle ou une communication publique est probable.",
        ],
        "do_not": [
            "Ne pas minimiser ou notifier publiquement avant d’avoir qualifié les faits avec les responsables compétents.",
            "Ne pas supprimer les journaux ou la configuration exposée avant leur conservation.",
        ],
        "references": [
            {
                "label": "CNIL — Notifier une violation de données personnelles",
                "url": "https://www.cnil.fr/fr/services-en-ligne/notifier-une-violation-de-donnees-personnelles",
            },
            DGSSI_REFERENCE,
            NIST_REFERENCE,
        ],
    },
    "unknown": {
        "title": "Qualifier une menace non classifiée",
        "summary": "Valider le signal, identifier les actifs concernés et prendre une mesure réversible avant toute action lourde.",
        "priority": "modérée",
        "owner": "Responsable informatique",
        "reviewed_at": "2026-10-07",
        "actions": [
            "Valider l’indicateur avec une seconde source",
            "Rechercher l’indicateur dans les journaux",
            "Identifier les actifs, comptes et données concernés",
            "Appliquer une mesure de confinement réversible",
            "Escalader si le périmètre ou l’impact reste incertain",
        ],
        "sections": [
            {
                "title": "Valider le signal",
                "timeframe": "0–30 min",
                "actions": [
                    "Conserver l’alerte originale, son horodatage, sa source et son niveau de confiance.",
                    "Vérifier l’indicateur auprès d’une seconde source récente et fiable.",
                    "Rechercher l’indicateur dans les journaux réseau, système, authentification et applications.",
                    "Identifier les actifs, comptes et fonctions métier potentiellement associés.",
                ],
            },
            {
                "title": "Réduire le risque",
                "timeframe": "30–60 min",
                "actions": [
                    "Choisir une mesure réversible et proportionnée : surveillance, filtrage ciblé ou isolement.",
                    "Comparer les événements avant et après l’apparition du signal pour établir une chronologie.",
                    "Rechercher des indicateurs connexes plutôt que de conclure à partir d’un seul événement.",
                    "Documenter les hypothèses confirmées, rejetées et encore ouvertes.",
                ],
            },
            {
                "title": "Décider et clôturer",
                "timeframe": "Après qualification",
                "actions": [
                    "Reclasser vers la procédure adaptée si la nature de l’incident devient claire.",
                    "Escalader vers un prestataire ou le maCERT si le risque dépasse les capacités internes.",
                    "Lever les mesures temporaires lorsqu’un faux positif est démontré et conserver la justification.",
                    "Créer une règle de détection ou un retour d’expérience si le signal était pertinent.",
                ],
            },
        ],
        "evidence_to_preserve": [
            "Alerte originale, source, score, date et contexte complet.",
            "Journaux recherchés, résultats positifs comme négatifs et plage temporelle utilisée.",
            "Décisions de confinement et identité des personnes ayant validé les actions.",
        ],
        "escalation_criteria": [
            "Un actif critique, un compte privilégié ou des données sensibles peuvent être touchés.",
            "L’activité se poursuit malgré la première mesure de confinement.",
            "Les compétences ou journaux nécessaires à la qualification ne sont pas disponibles.",
        ],
        "do_not": [
            "Ne pas bloquer largement ou réinstaller un système sur la base d’un indicateur isolé.",
            "Ne pas clôturer faute de preuve sans documenter les limites de l’investigation.",
        ],
        "references": [DGSSI_REFERENCE, MACERT_REFERENCE, NIST_REFERENCE],
    },
}


def get_reflex_sheet(threat_type: str) -> dict[str, object]:
    return REFLEX_SHEETS.get(threat_type, REFLEX_SHEETS["unknown"])


def get_recommended_action(threat_type: str) -> str:
    sheet = get_reflex_sheet(threat_type)
    return " ; ".join(str(action) for action in sheet["actions"])
