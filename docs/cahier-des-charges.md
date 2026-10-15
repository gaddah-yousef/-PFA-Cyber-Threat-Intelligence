# Cahier des charges

## Projet : Système de détection et d'alerte précoce des cybermenaces ciblant les PME

---

## 1. Contexte du projet

Les petites et moyennes entreprises, appelées PME, sont aujourd'hui fortement exposées aux cybermenaces. Elles utilisent souvent des services numériques comme les emails professionnels, les sites web, les outils cloud, les applications de gestion et les plateformes de paiement, mais elles ne disposent pas toujours d'une équipe cybersécurité complète.

Contrairement aux grandes entreprises, beaucoup de PME n'ont pas de SOC, pas de SIEM avancé, pas de surveillance continue et parfois pas de procédure claire en cas d'incident. Cela les rend vulnérables face à des attaques comme le phishing, les ransomwares, les malwares, l'exploitation de vulnérabilités, les attaques par brute force ou encore les fuites de données.

Le projet vise donc à concevoir une plateforme légère, accessible et utile pour les PME, capable de collecter des informations de Threat Intelligence, d'analyser les menaces, de calculer un score de risque, de générer des alertes et de proposer des fiches réflexes adaptées.

---

## 2. Problématique

Les PME ont besoin d'un système simple qui leur permet de répondre aux questions suivantes :

* Quelles sont les cybermenaces actuelles qui peuvent me concerner ?
* Est-ce qu'une adresse IP, un domaine, une URL ou une CVE représente un danger ?
* Quelle est la priorité de traitement de chaque menace ?
* Que dois-je faire concrètement en cas de phishing, ransomware, brute force ou vulnérabilité critique ?
* Comment recevoir rapidement une alerte lorsqu'une menace importante est détectée ?

Le problème principal est donc l'absence d'un outil léger de veille, d'analyse et d'alerte précoce adapté aux capacités techniques et financières des PME.

---

## 3. Objectif général

L'objectif du projet est de développer une plateforme web de **détection et d'alerte précoce des cybermenaces ciblant les PME**.

La plateforme devra collecter des données depuis différentes sources de Threat Intelligence, les normaliser, les analyser, leur attribuer un score de risque, puis afficher les résultats dans un tableau de bord clair.

Elle devra également générer des alertes et proposer des recommandations pratiques sous forme de fiches réflexes.

---

## 4. Objectifs spécifiques

Le projet doit permettre de :

1. Mettre en place un moteur de veille cyber.
2. Collecter des indicateurs de compromission : IP, domaines, URLs, CVE, hashes.
3. Normaliser les données collectées.
4. Classifier les menaces selon leur type : phishing, malware, ransomware, brute force, vulnérabilité, etc.
5. Calculer automatiquement un score de risque.
6. Détecter les menaces critiques.
7. Afficher les résultats dans un dashboard.
8. Générer des alertes.
9. Fournir des fiches réflexes adaptées aux PME.
10. Préparer une base extensible vers une future intégration SIEM-light ou IA avancée.

---

## 5. Périmètre du projet

### 5.1 Ce que le projet va faire

Le projet va construire une plateforme de type :

**Threat Intelligence Early Warning System for SMEs**

C'est-à-dire un système de veille, détection, scoring et alerte.

La plateforme va gérer :

* les menaces externes ;
* les indicateurs suspects ;
* les vulnérabilités critiques ;
* le scoring de risque ;
* les alertes ;
* les recommandations ;
* la visualisation dans un dashboard.

### 5.2 Ce que le projet ne va pas faire dans la première version

Le projet ne sera pas un SIEM complet comme Splunk, QRadar ou Wazuh.

Il ne va pas, dans la première version :

* collecter massivement les logs internes de toutes les machines ;
* faire une corrélation SIEM avancée ;
* gérer des agents installés sur les postes ;
* faire du forensic complet ;
* remplacer une équipe SOC ;
* déployer une architecture Kubernetes complexe ;
* utiliser du deep learning lourd dès le départ.

La bonne approche est de construire d'abord un **MVP propre**, puis d'ajouter des fonctionnalités avancées.

---

## 6. Description générale de la solution

La solution sera composée de plusieurs modules :

```txt
Sources Threat Intelligence
        ↓
Moteur de collecte
        ↓
Normalisation des données
        ↓
Moteur d'analyse et scoring
        ↓
Base de données
        ↓
API Backend
        ↓
Dashboard Web
        ↓
Alertes + Fiches réflexes
```

---

## 7. Acteurs du système

### 7.1 Administrateur

L'administrateur peut :

* consulter toutes les menaces ;
* gérer les sources de données ;
* consulter les alertes ;
* voir les statistiques ;
* gérer les paramètres du système.

### 7.2 Analyste cybersécurité

L'analyste peut :

* consulter les menaces détectées ;
* filtrer par type, source ou criticité ;
* analyser le score de risque ;
* consulter les fiches réflexes ;
* valider ou ignorer certaines alertes.

### 7.3 Responsable PME

Le responsable PME peut :

* consulter le dashboard global ;
* voir les alertes importantes ;
* lire les recommandations simples ;
* suivre l'état général des risques.

---

## 8. Fonctionnalités fonctionnelles

### 8.1 Module de collecte Threat Intelligence

Le système doit collecter des données depuis différentes sources.

Sources possibles :

| Source         | Type de données  | Utilisation                              |
| -------------- | ----------------- | ----------------------------------------- |
| NVD / CVE      | Vulnérabilités    | Identifier les failles critiques          |
| CISA KEV       | CVE exploitées    | Prioriser les vulnérabilités dangereuses  |
| URLhaus        | URLs malware       | Détecter les liens malveillants           |
| AbuseIPDB      | IP malveillantes  | Identifier les IP suspectes               |
| AlienVault OTX | IOCs               | Collecter IP, domaines, hashes            |
| PhishTank      | URLs phishing      | Détection du phishing                     |
| MISP           | Threat sharing     | Corrélation future des indicateurs        |

Dans la première version, tu peux commencer par :

* sample collector local ;
* URLhaus ;
* NVD/CVE ;
* AbuseIPDB ou AlienVault OTX si API key disponible.

### 8.2 Module de normalisation

Comme chaque source donne des données dans un format différent, il faut les transformer en format unique.

Exemple de format normalisé :

```json
{
  "indicator": "fake-office365-login.com",
  "indicator_type": "domain",
  "threat_type": "phishing",
  "source": "sample",
  "severity": "high",
  "risk_score": 85,
  "risk_level": "high",
  "description": "Suspicious phishing domain targeting business users",
  "recommended_action": "Block domain and alert employees"
}
```

### 8.3 Module de scoring de risque

Le système doit calculer un score entre 0 et 100.

#### Niveaux de risque

| Score    | Niveau   |
| -------- | -------- |
| 0 - 39   | Low      |
| 40 - 69  | Medium   |
| 70 - 89  | High     |
| 90 - 100 | Critical |

Le score peut être calculé selon :

* le type d'indicateur : IP, domaine, URL, CVE, hash ;
* le type de menace : phishing, malware, ransomware, brute force, vulnérabilité ;
* la sévérité ;
* la fiabilité de la source ;
* la récence de la menace ;
* l'existence d'exploitation active ;
* l'impact potentiel sur une PME.

Exemple :

```txt
Domaine phishing + sévérité high + source fiable
= risk_score 85
= risk_level high
```

### 8.4 Module de classification des menaces

Le système doit classifier chaque menace selon son type :

* phishing ;
* malware ;
* ransomware ;
* brute force ;
* vulnerability ;
* suspicious IP ;
* data leak ;
* malicious domain ;
* unknown.

Dans la première version, la classification peut être basée sur des règles simples.

Dans une version avancée, on peut ajouter un modèle Machine Learning avec Scikit-learn.

### 8.5 Module d'alertes

Le système doit générer une alerte lorsqu'une menace dépasse un certain seuil.

Règles proposées :

```txt
risk_score >= 90 → alerte critique
risk_score >= 70 → alerte élevée
risk_score < 70 → pas d'alerte urgente
```

Canaux d'alerte pour le MVP :

* alerte affichée dans le dashboard ;
* historique des alertes ;
* endpoint API pour tester les alertes.

Canaux futurs :

* email ;
* Telegram ;
* Slack ;
* webhook ;
* SMS.

### 8.6 Module fiches réflexes

Pour chaque type de menace, le système doit proposer des actions concrètes.

#### Exemple : phishing

Actions recommandées :

* bloquer le domaine ou l'URL ;
* alerter les employés ;
* vérifier les emails suspects ;
* changer les mots de passe compromis ;
* activer MFA ;
* analyser les logs de messagerie.

#### Exemple : ransomware

Actions recommandées :

* isoler les machines touchées ;
* vérifier les sauvegardes ;
* ne pas payer directement la rançon ;
* lancer une procédure de réponse à incident ;
* analyser les mouvements latéraux ;
* restaurer depuis backup propre.

#### Exemple : brute force

Actions recommandées :

* bloquer l'adresse IP suspecte ;
* activer MFA ;
* vérifier les logs d'authentification ;
* appliquer du rate limiting ;
* désactiver les comptes compromis.

#### Exemple : CVE critique

Actions recommandées :

* identifier les systèmes vulnérables ;
* appliquer le patch ;
* désactiver temporairement le service exposé ;
* vérifier les tentatives d'exploitation ;
* surveiller les logs.

### 8.7 Dashboard web

Le dashboard doit permettre à l'utilisateur de visualiser rapidement l'état des menaces.

Pages proposées :

1. Overview
2. Liste des menaces
3. Détails d'une menace
4. Alertes critiques
5. Fiches réflexes
6. Sources de Threat Intelligence
7. À propos du projet

Le dashboard doit afficher :

* nombre total de menaces ;
* nombre de menaces critiques ;
* nombre de menaces high ;
* nombre de menaces medium ;
* nombre de menaces low ;
* dernières alertes ;
* menaces par type ;
* menaces par source ;
* tableau des indicateurs.

---

## 9. Exigences techniques

### Backend

Technologies proposées :

* Python ;
* FastAPI ;
* Pydantic ;
* SQLAlchemy ;
* SQLite pour développement local ;
* PostgreSQL pour version évoluée ;
* pytest pour les tests.

### Frontend

Technologies proposées :

* React ;
* TypeScript ;
* Vite ;
* Tailwind CSS ;
* Axios ;
* React Router.

### Base de données

Première version :

* SQLite.

Version plus professionnelle :

* PostgreSQL.

Option future :

* Elasticsearch pour la recherche et l'analyse de données cyber.

### DevOps

À prévoir :

* Dockerfile backend ;
* Dockerfile frontend ;
* docker-compose.yml ;
* `.env.example` ;
* README ;
* GitHub Actions CI ;
* tests automatiques.

---

## 10. Architecture technique proposée

```txt
Frontend React
    |
    | HTTP / Axios
    ↓
Backend FastAPI
    |
    ├── Threat API
    ├── Alert API
    ├── Reflex Sheets API
    ├── Stats API
    |
    ↓
Services internes
    |
    ├── Risk Scoring Engine
    ├── Alert Service
    ├── Collector Service
    ├── Reflex Sheet Service
    |
    ↓
Database SQLite/PostgreSQL
```

---

## 11. Modèle de données principal

### Entité Threat

```txt
Threat
- id
- indicator
- indicator_type
- threat_type
- source
- severity
- risk_score
- risk_level
- description
- recommended_action
- first_seen
- last_seen
- created_at
```

### Entité Alert

```txt
Alert
- id
- threat_id
- title
- message
- level
- status
- created_at
```

### Entité ReflexSheet

```txt
ReflexSheet
- id
- threat_type
- title
- description
- actions
- prevention_tips
```

---

## 12. API backend proposée

Endpoints principaux :

```txt
GET /
GET /health
GET /api/threats
GET /api/threats/{id}
POST /api/threats/analyze
POST /api/threats/manual
GET /api/threats/critical
GET /api/stats
GET /api/alerts
GET /api/alerts/{id}
POST /api/alerts/test
GET /api/reflex-sheets
GET /api/reflex-sheets/{threat_type}
POST /api/collectors/sample/run
POST /api/collectors/urlhaus/run
POST /api/collectors/nvd/run
```

---

## 13. Exigences non fonctionnelles

### 13.1 Sécurité

Le système doit respecter les bonnes pratiques suivantes :

* pas de secrets hardcodés ;
* utilisation d'un fichier `.env` ;
* validation des inputs avec Pydantic ;
* gestion propre des erreurs ;
* CORS limité ;
* logs sans données sensibles ;
* séparation configuration développement/production.

### 13.2 Performance

Le système doit être capable de :

* charger rapidement la liste des menaces ;
* filtrer les menaces ;
* afficher les statistiques ;
* analyser une menace en temps raisonnable.

### 13.3 Maintenabilité

Le code doit être :

* clair ;
* modulaire ;
* documenté ;
* testé ;
* organisé par services.

### 13.4 Évolutivité

Le projet doit permettre d'ajouter plus tard :

* nouvelles sources Threat Intelligence ;
* modèles Machine Learning ;
* intégration SIEM ;
* alertes email/Telegram ;
* authentification ;
* rôles utilisateurs ;
* Elasticsearch/Kibana.

---

## 14. Tests et validation

Tests à réaliser :

### Tests backend

* test endpoint `/health` ;
* test création/analyse d'une menace ;
* test calcul risk score ;
* test récupération des menaces critiques ;
* test fiches réflexes ;
* test génération d'alerte.

### Tests frontend

* affichage dashboard ;
* affichage liste des menaces ;
* filtres ;
* page détails ;
* affichage alertes ;
* affichage fiches réflexes.

### Tests fonctionnels

Scénario 1 :

```txt
Ajouter une menace phishing high
→ Le système calcule risk_score
→ Le système affiche risk_level high
→ Le système propose actions phishing
```

Scénario 2 :

```txt
Ajouter une CVE critical
→ Le système calcule risk_score >= 90
→ Une alerte critique est générée
→ La menace apparaît dans Critical Alerts
```

Scénario 3 :

```txt
Collecter données sample
→ Les menaces sont normalisées
→ Elles sont stockées
→ Elles sont affichées dans le dashboard
```

---

## 15. Livrables attendus

À la fin du projet, tu dois livrer :

1. Application backend fonctionnelle.
2. Dashboard frontend fonctionnel.
3. Moteur de scoring.
4. Module d'alertes.
5. Module fiches réflexes.
6. Module de collecte Threat Intelligence.
7. Base de données.
8. Tests.
9. Documentation technique.
10. Rapport de stage.
11. Présentation finale.

Ces livrables correspondent à l'esprit de la fiche CMRPI : moteur de détection opérationnel, tableau de bord, modèles d'analyse/IA et documentation.

---

## 16. Planning proposé sur 8 semaines

### Semaine 1 — Analyse et cadrage

* Lire la fiche technique.
* Comprendre la problématique PME.
* Étudier les menaces principales.
* Identifier les sources Threat Intelligence.
* Rédiger l'état de l'art.
* Proposer l'architecture MVP.

### Semaine 2 — Cahier des charges et conception

* Finaliser le cahier des charges.
* Définir le modèle de données.
* Définir les endpoints API.
* Définir le scoring.
* Préparer le backlog.
* Préparer la structure du projet.

### Semaine 3 — Backend MVP

* Créer FastAPI.
* Créer modèles et schemas.
* Créer base de données.
* Créer endpoints `/threats`, `/stats`, `/alerts`.
* Ajouter risk scoring.

### Semaine 4 — Collecte Threat Intelligence

* Créer sample collector.
* Ajouter URLhaus ou NVD.
* Normaliser les données.
* Stocker les menaces.
* Générer les premières alertes.

### Semaine 5 — Dashboard frontend

* Créer React/Vite.
* Créer page Overview.
* Créer tableau des menaces.
* Créer filtres.
* Connecter frontend à backend.

### Semaine 6 — Alertes et fiches réflexes

* Créer page alertes.
* Créer fiches réflexes.
* Ajouter détails d'une menace.
* Ajouter recommandations.

### Semaine 7 — Tests et amélioration

* Ajouter tests backend.
* Corriger bugs.
* Améliorer UI.
* Ajouter Docker.
* Préparer documentation API.

### Semaine 8 — Documentation et présentation

* Finaliser README.
* Finaliser rapport.
* Préparer slides.
* Préparer démonstration.
* Préparer soutenance.

---

## 17. Critères d'acceptation

Le projet sera considéré comme réussi si :

* l'API backend fonctionne ;
* le dashboard affiche les menaces ;
* le système calcule un risk score ;
* les alertes critiques sont générées ;
* les fiches réflexes sont disponibles ;
* au moins une source de Threat Intelligence est intégrée ou simulée proprement ;
* le projet est documenté ;
* le projet peut être lancé localement ;
* une démonstration claire peut être présentée.

---

## 18. Limites du MVP

La première version aura certaines limites :

* pas de SIEM complet ;
* pas de corrélation avancée de logs internes ;
* pas de deep learning avancé ;
* dépendance à certaines sources publiques ;
* qualité des données variable ;
* alertes simples ;
* pas encore d'authentification avancée.

Ces limites sont acceptables pour un MVP PFA, à condition de les expliquer dans le rapport.

---

## 19. Évolutions futures

Après le MVP, le projet peut évoluer vers :

* intégration Elasticsearch/Kibana ;
* intégration MISP ;
* intégration Wazuh ou SIEM-light ;
* analyse de logs internes ;
* Machine Learning avec Scikit-learn ;
* anomaly detection ;
* alertes Telegram/email ;
* authentification et rôles ;
* scoring plus avancé ;
* déploiement cloud ;
* génération automatique de rapports PDF ;
* playbooks de réponse à incident.

---

## 20. Résumé final

Ce projet est une plateforme de **veille cyber, analyse, scoring et alerte précoce** destinée aux PME.

Il ne s'agit pas d'un SIEM complet, mais d'un système plus léger qui aide les PME à :

* détecter les menaces importantes ;
* comprendre leur niveau de risque ;
* recevoir des alertes ;
* savoir quoi faire grâce aux fiches réflexes ;
* visualiser l'état des menaces dans un dashboard.

**Nom conseillé pour ton projet :**

```txt
PME Cyber Threat Early Warning System
```

ou en français :

```txt
Plateforme de détection et d'alerte précoce des cybermenaces ciblant les PME
```
