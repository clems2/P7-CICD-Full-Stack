# MicroCRM — Pipeline CI/CD

[![CI/CD](https://github.com/clems2/P7-CICD-Full-Stack/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/clems2/P7-CICD-Full-Stack/actions/workflows/ci-cd.yml)
[![Quality Gate Back](https://sonarcloud.io/api/project_badges/measure?project=clems2_P7-CICD-Full-Stack_Back&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=clems2_P7-CICD-Full-Stack_Back)
[![Quality Gate Front](https://sonarcloud.io/api/project_badges/measure?project=clems2_P7-CICD-Full-Stack_Front&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=clems2_P7-CICD-Full-Stack_Front)

**MicroCRM** est une application interne de gestion de la relation client. Elle expose une API REST
sur deux entités — les personnes et les organisations — servie par une interface Angular. Les
départements technique et commercial l'utilisent pour consulter et tenir à jour ces deux
répertoires.

Ce dépôt contient l'application **et la chaîne d'industrialisation construite autour d'elle** :

- **intégration continue** — chaque modification est construite, testée et analysée avant de
  pouvoir rejoindre la branche principale, qui exige quatre contrôles au vert ;
- **qualité et sécurité** — analyse statique des deux composants et mesure de la couverture de
  tests à chaque exécution ;
- **livraison** — deux images de conteneurs publiées automatiquement à chaque intégration, chacune
  identifiée par le commit dont elle est issue ;
- **exploitation** — centralisation des logs applicatifs et d'accès, tableau de bord de supervision,
  sauvegarde et restauration de la base, mesure des indicateurs de performance de la chaîne.

Projet 7 du parcours Développeur Full-Stack Java & Angular d'OpenClassrooms, **Option B, scénario
Orion**.

---

## Par où commencer

| Vous voulez… | Lisez |
|---|---|
| **Faire tourner l'application** sans rien installer d'autre que Docker | [Ce qu'il faut installer](#ce-quil-faut-installer), puis [Lancer l'application](#lancer-lapplication) |
| **Contribuer au code** : construire, tester, ouvrir une pull request | [Développer et tester](#développer-et-tester), puis [Contribuer](#contribuer) |
| **Comprendre les décisions prises** et leurs contreparties | [Choix techniques](#choix-techniques) |
| **Comprendre la chaîne d'intégration** : déclencheurs, jobs, commandes exécutées | [Le pipeline](#le-pipeline) |
| **Réutiliser ce dépôt** pour votre propre projet | [Forker ce dépôt](#forker-ce-dépôt) |
| **Déployer ailleurs** que sur un poste de développement | [Déploiement](#déploiement) |
| **Superviser l'application** et consulter ses logs | [Lancer la supervision](#lancer-la-supervision) |

Les analyses, mesures et plans d'exploitation figurent dans la **documentation technique**, déposée
avec les livrables du projet. Ce README décrit comment faire fonctionner le projet et pourquoi il
est construit ainsi ; la documentation technique explique ce qui a été mesuré et analysé.

---

## Sommaire

- [Stack technique](#stack-technique)
- [Ce qu'il faut installer](#ce-quil-faut-installer)
- [Lancer l'application](#lancer-lapplication)
- [Lancer la supervision](#lancer-la-supervision)
- [Développer et tester](#développer-et-tester)
- [Exécuter les scripts](#exécuter-les-scripts)
- [Sauvegarder et restaurer](#sauvegarder-et-restaurer)
- [Structure du dépôt](#structure-du-dépôt)
- [Configuration](#configuration)
- [Forker ce dépôt](#forker-ce-dépôt)
- [Déploiement](#déploiement)
- [Le pipeline](#le-pipeline)
- [Choix techniques](#choix-techniques)
- [Contribuer](#contribuer)
- [Dépannage](#dépannage)
- [Documentation](#documentation)

---

## Stack technique

| Domaine | Technologie | Version |
|---|---|---|
| Back-end | Spring Boot, Java, Gradle | 3.2.5, 21, 8.7 |
| Front-end | Angular, TypeScript, Node | 17.3, 5.4, 20 |
| Serveur web du front | Caddy | 2 |
| Base de données | HSQLDB, en mode fichier sur volume | — |
| Tests back-end | JUnit 5, couverture JaCoCo | 0.8.13 |
| Tests front-end | Karma, ChromeHeadless, couverture LCOV | — |
| Intégration continue | GitHub Actions | — |
| Qualité et sécurité | SonarQube Cloud | — |
| Conteneurisation | Docker multi-stage, Docker Compose | — |
| Registre d'images | GitHub Container Registry | — |
| Supervision | Elasticsearch, Logstash, Kibana | 8.11.0 |
| Logs applicatifs | Logback, logstash-logback-encoder | 7.4 |
| Surveillance des dépendances | Dependabot | — |

Le dépôt est organisé en **monorepo** : le back-end, le front-end et la configuration de
conteneurisation cohabitent dans un seul dépôt, et le pipeline traite les deux chaînes de
construction dans un même flux.

Angular 17, Node 20 et Spring Boot 3.2 sont hors support. Ce constat est assumé et documenté —
voir [Stack applicative gelée](#stack-applicative-gelée).

---

## Ce qu'il faut installer

### Pour lancer l'application

Un seul outil suffit. Ni Java, ni Node, ni base de données à installer : tout est dans les images.

| Outil | Version | Téléchargement |
|---|---|---|
| Docker Desktop, ou Docker Engine et Compose | 24 ou supérieure | [docker.com](https://www.docker.com/products/docker-desktop/) |

Sous Windows, Docker Desktop doit être configuré avec le moteur WSL2.

### Pour développer

| Outil | Version | Téléchargement | Sert à |
|---|---|---|---|
| JDK Temurin | 21 | [adoptium.net](https://adoptium.net/temurin/releases/?version=21) | Construire et tester le back-end |
| Node.js | 20 | [nodejs.org](https://nodejs.org/en/about/previous-releases) | Construire et tester le front-end |
| Chrome ou Chromium | récente | [google.com/chrome](https://www.google.com/chrome/) | Exécuter les tests front-end |

Node 20 n'est plus la version courante. Pour l'installer sans écraser une autre version déjà
présente sur le poste, [nvm](https://github.com/nvm-sh/nvm) est le moyen le plus simple :

```bash
nvm install 20
nvm use 20
```

Gradle et la CLI Angular n'ont pas besoin d'être installés : le wrapper `./gradlew` récupère Gradle,
et `npx ng` utilise la CLI fournie par les dépendances du projet.

### Ressources nécessaires

| Ressource | Besoin |
|---|---|
| Ports libres | 80 et 8080 pour l'application ; 5601, 9200, 5044 et 5045 pour la supervision |
| Mémoire | environ 1 Go pour l'application seule, 4 Go avec la supervision |
| Accès au registre | aucun identifiant, les images publiées sont publiques |

### Vérifier son installation

```bash
docker --version
docker compose version
java -version              # doit afficher 21
node --version             # doit afficher v20.x
```

---

## Lancer l'application

> **Prérequis** : Docker démarré. Rien d'autre.

```bash
git clone https://github.com/clems2/P7-CICD-Full-Stack.git
cd P7-CICD-Full-Stack
docker compose up -d --build
```

La commande construit les deux images puis démarre les services. Le premier lancement prend
quelques minutes, les suivants quelques secondes grâce au cache.

| Accès | URL |
|---|---|
| Application | http://localhost |
| API, par le serveur web | http://localhost/persons |
| API, accès direct pour le diagnostic | http://localhost:8080/persons |

Le front-end appelle l'API par des chemins relatifs. Le serveur web les relaie vers le back-end.
Toutes les requêtes passent donc par un point d'entrée unique, et le port 8080 ne sert qu'au
diagnostic.

L'orchestration attend que la sonde de santé du back-end réponde avant de démarrer le front-end.
L'interface n'est donc jamais servie avant que l'API ne soit prête.

### Vérifier que tout fonctionne

Trois contrôles, du plus rapide au plus complet.

```bash
docker compose ps
```

Les deux services doivent apparaître avec l'état **healthy**. Un service bloqué en `starting` plus
d'une minute signale un problème de démarrage : `docker compose logs` donnera la cause.

```bash
curl -s "http://localhost/persons?size=1"
```

La réponse est un document JSON contenant un champ `totalElements`. S'il vaut zéro, la base est
vide ; s'il est supérieur à zéro, les données de démonstration ont bien été chargées.

Enfin, ouvrir http://localhost : l'interface affiche la liste des personnes. Des listes vides
signifient que l'API ne répond pas — voir [Dépannage](#dépannage).

En cas de doute, les journaux des deux services :

```bash
docker compose logs -f
```

### Arrêter l'application

```bash
docker compose down        # arrêter, en conservant les données
docker compose down -v     # arrêter et supprimer le volume de données
```

Après un `down -v`, les données de démonstration sont régénérées au démarrage suivant.

---

## Lancer la supervision

> **Prérequis** : l'application doit tourner. La supervision rejoint le réseau `microcrm-net`, que
> l'orchestration applicative crée au démarrage. Sans lui, les conteneurs ELK ne démarrent pas.

La stack ELK centralise les logs des deux composants. Elle est décrite dans un fichier
d'orchestration distinct, pour que l'application reste démarrable sans elle.

```bash
docker compose up -d                                # l'application d'abord
docker compose -f docker-compose-elk.yml up -d      # puis la supervision
```

| Service | URL |
|---|---|
| Kibana | http://localhost:5601 |
| Elasticsearch | http://localhost:9200 |

Compter une à deux minutes avant que Kibana ne réponde.

**Importer le tableau de bord** — dans Kibana, *Stack Management → Saved Objects → Import*, puis
sélectionner `elk/kibana-dashboard.ndjson`. L'import installe quatre visualisations et les deux vues
de données associées.

**Alimenter le tableau de bord** — lancer `./scripts/generate-traffic.sh`, puis élargir la fenêtre
temporelle en haut à droite de Kibana.

| Source collectée | Contenu | Index |
|---|---|---|
| Logs d'accès du serveur web | chemin, code de statut, durée de chaque requête | `microcrm-front-AAAA.MM.JJ` |
| Logs applicatifs du back-end | fonctionnement interne de l'API | `microcrm-back-AAAA.MM.JJ` |

Les deux sources envoient leurs logs à Logstash en TCP, au format JSON, sur deux ports distincts. Si
Logstash ne répond pas, les émetteurs continuent sans lui : l'application fonctionne même sans
supervision.

```bash
docker compose -f docker-compose-elk.yml down       # arrêter la supervision
```

---

## Développer et tester

### Back-end

> **Prérequis** : JDK 21. Docker n'est pas nécessaire — le back-end démarre avec sa propre base,
> écrite sur le disque.

```bash
cd back

./gradlew build          # compile, exécute les tests, génère le rapport de couverture
./gradlew test           # tests seuls
./gradlew bootRun        # démarre l'application sur le port 8080
```

Le rapport de couverture est produit dans `back/build/reports/jacoco/test/` — en HTML pour la
lecture, en XML pour l'analyse. Sa génération est chaînée à la tâche de test par `finalizedBy`, donc
un simple `./gradlew build` suffit à l'obtenir. Cette liaison rend l'oubli impossible en CI.

**Où sont écrites les données en local ?** Dans `back/data/`, et non dans le volume Docker. Les deux
emplacements sont indépendants :

| Mode de lancement | Emplacement de la base | Effet d'une suppression |
|---|---|---|
| `./gradlew bootRun` | `back/data/`, sur le disque | Les données saisies en local sont perdues, les données de démonstration reviennent au démarrage suivant |
| `docker compose up` | Volume Docker nommé | Sans effet sur `back/data/` |

La variable `MICROCRM_DB_PATH` explique cette différence : le conteneur la définit sur `/data`, qui
est monté sur le volume ; en local, elle n'est pas définie, donc la valeur par défaut
d'`application.properties` s'applique et pointe sur `back/data/`.

Dans les deux cas, la base contient les mêmes choses : les personnes et les organisations, chargées
au premier démarrage par les données de démonstration, puis tout ce que l'on crée ensuite. Supprimer
`back/data/` revient donc à repartir d'une base neuve en local, sans toucher aux données du
conteneur.

### Front-end

> **Prérequis** : Node 20 et un navigateur Chrome ou Chromium. Pour `ng serve` avec des données, le
> back-end doit tourner, en local ou en conteneur.

```bash
cd front

npm ci                   # installation stricte depuis le fichier de verrouillage
npx ng serve             # serveur de développement sur le port 4200
npx ng build             # construction de production dans dist/
```

Tests dans les mêmes conditions que la chaîne d'intégration :

```bash
npx ng test --watch=false --browsers=ChromeHeadlessNoSandbox
```

Les deux paramètres sont nécessaires hors interface graphique. Sans `--watch=false`, la commande
attend indéfiniment de nouvelles modifications et ne se termine jamais. La couverture est activée
par défaut et produite dans `front/coverage/microcrm/`.

Le serveur de développement reproduit le relais de l'API grâce à `proxy.conf.json`. Les appels vers
`/persons` et `/organizations` sont transmis au back-end, exactement comme le fait Caddy en
conteneur.

Si Karma ne trouve pas le navigateur, lui indiquer son chemin :

```bash
export CHROME_BIN=$(which google-chrome)
```

### Construire une image isolément

> **Prérequis** : Docker démarré.

Ces commandes ne sont pas nécessaires pour lancer l'application : `docker compose up --build` s'en
charge. Elles servent à construire un seul composant, pour vérifier un Dockerfile après
modification ou diagnostiquer un échec de build.

```bash
docker build -t microcrm-back ./back
docker build -t microcrm-front ./front
```

Chaque composant possède son propre contexte de build, limité à son répertoire.

---

## Exécuter les scripts

Trois scripts sous `scripts/`. Ils ne font pas partie du pipeline : ils servent à la supervision, à
la mesure et à l'exploitation locale. Aucune dépendance à installer — le Python se limite à sa
bibliothèque standard.

### Générer du trafic

> **Prérequis** : l'application doit tourner. La supervision aussi, sinon le trafic ne sera pas
> enregistré.

```bash
./scripts/generate-traffic.sh          # 30 cycles par défaut
./scripts/generate-traffic.sh 10       # 10 cycles
```

Chaque cycle interroge la page d'accueil et les deux collections de l'API. Un cycle sur cinq ajoute
deux erreurs 404 et une erreur 405, pour que les visualisations d'erreurs aient de la matière.

Les appels passent par le serveur web, donc par le même chemin qu'un navigateur. Ils apparaissent
dans les logs d'accès.

| Variable | Rôle | Défaut |
|---|---|---|
| `FRONT_URL` | Adresse de l'application | `http://localhost` |
| `API_URL` | Adresse de l'API | `http://localhost` |

### Mesurer le pipeline

> **Prérequis** : Python 3 et un accès à Internet. Ni l'application ni la supervision n'ont besoin
> de tourner : le script interroge l'API de GitHub, pas l'application.

```bash
./scripts/collect-metrics.py
```

Le script calcule les quatre métriques DORA et cinq indicateurs de pipeline à partir de l'historique
des exécutions. Le dépôt et l'API étant publics, n'importe qui peut relancer la commande et vérifier
les valeurs de la documentation technique.

| Variable | Rôle | Défaut |
|---|---|---|
| `GITHUB_TOKEN` | Jeton d'accès à l'API, facultatif | aucun |
| `GITHUB_REPOSITORY` | Dépôt analysé | `clems2/P7-CICD-Full-Stack` |

**En cas d'erreur de limite de requêtes.** GitHub autorise soixante appels par heure sans
authentification. Passé ce seuil, le script échoue. S'authentifier avec un jeton de **son propre
compte GitHub** porte la limite à cinq mille appels par heure. Ce jeton n'est jamais nécessaire au
fonctionnement du projet : il ne sert qu'à contourner cette limite, et seulement si on la rencontre.

Le plus simple, avec la ligne de commande GitHub installée, est de ne jamais manipuler le jeton :

```bash
GITHUB_TOKEN=$(gh auth token) ./scripts/collect-metrics.py
```

Sinon, créer un jeton personnel depuis *Settings → Developer settings → Personal access tokens* de
son compte, **sans cocher aucune portée** — lire un dépôt public n'en demande aucune. Puis le saisir
sans qu'il apparaisse dans l'historique du shell :

```bash
read -rs GITHUB_TOKEN && export GITHUB_TOKEN     # saisie masquée
./scripts/collect-metrics.py
```

### Analyser la qualité en local

> **Réservé aux mainteneurs du dépôt.** Cette commande envoie l'analyse vers l'organisation
> SonarQube Cloud du projet. Un contributeur externe n'a ni à la lancer ni à en avoir les accès : la
> chaîne d'intégration analyse automatiquement chaque pull request.

```bash
cd back && ./gradlew sonar
```

Le jeton se crée depuis SonarQube Cloud, dans *My Account → Security*. Le déclarer dans le fichier
de propriétés personnel de Gradle, qui n'appartient pas au dépôt :

```properties
# ~/.gradle/gradle.properties
systemProp.sonar.token=<le jeton>
```

```bash
chmod 600 ~/.gradle/gradle.properties
```

Gradle le lit alors automatiquement. La variable d'environnement `SONAR_TOKEN` reste une solution de
repli, à exporter dans le shell plutôt qu'à écrire devant la commande : un secret tapé sur une ligne
de commande reste dans l'historique.

---

## Sauvegarder et restaurer

> **Prérequis** : l'application doit tourner, ou avoir tourné au moins une fois — le script agit sur
> le volume Docker, qui n'existe qu'à partir du premier démarrage.

Les données applicatives sont le seul élément du projet qui n'existe nulle part ailleurs. Le code
est dans Git, les images dans le registre, les rapports se régénèrent en relançant le pipeline. Si
ces données disparaissent, rien ne permet de les reconstituer.

```bash
./scripts/backup-database.sh backup             # crée une archive horodatée
./scripts/backup-database.sh list               # liste les archives, la plus récente en tête
./scripts/backup-database.sh restore <archive>  # restaure l'archive indiquée
```

La base est stockée dans un volume Docker, pas dans les fichiers du projet. Le script ne peut donc
pas y accéder directement : il démarre un conteneur temporaire qui monte à la fois le volume et le
répertoire de sauvegarde, puis copie les données de l'un vers l'autre. Les archives sont déposées
dans un répertoire exclu du suivi de version.

**Le service est arrêté pendant l'opération**, quelques secondes. La base répartit ses données sur
plusieurs fichiers. Si on les copiait pendant que l'application écrit, ils ne correspondraient pas
au même instant et l'archive serait inutilisable. Cette courte indisponibilité est le prix d'une
sauvegarde dont on sait qu'elle est restaurable.

Après une restauration, deux vérifications. D'abord le volume de données :

```bash
curl -s "http://localhost/persons?size=1"       # lire le champ totalElements
```

Ensuite l'écriture, en créant un enregistrement de test. L'application ne s'exécute pas avec les
privilèges d'administration : si les droits sur les fichiers n'avaient pas été préservés, elle
pourrait lire mais plus écrire.

Le script ne pose aucune question et renvoie un code de sortie explicite. Il peut donc être planifié
tel quel, même si son déclenchement reste manuel dans le cadre du projet.

**Revenir à une version antérieure de l'application** relève d'un autre mécanisme. Chaque image
publiée porte le SHA de son commit : il suffit de démarrer l'image correspondante.

---

## Structure du dépôt

```
.
├── back/                            API Spring Boot
│   ├── Dockerfile                   Image du back-end, multi-stage
│   ├── build.gradle                 Toolchain Java 21, JaCoCo, SonarQube
│   └── src/main/resources/
│       ├── application.properties   Source de données, JPA
│       └── logback-spring.xml       Logs JSON vers Logstash, profil "container"
│
├── front/                           Interface Angular
│   ├── Dockerfile                   Image du front-end, multi-stage
│   ├── Caddyfile                    Serveur web : fichiers statiques et relais de l'API
│   ├── proxy.conf.json              Même relais pour le serveur de développement
│   ├── sonar-project.properties     Paramètres d'analyse
│   └── karma.conf.js                Tests et couverture
│
├── elk/
│   ├── logstash.conf                Réception des logs, un index par source et par jour
│   └── kibana-dashboard.ndjson      Tableau de bord et vues de données, à importer
│
├── scripts/
│   ├── generate-traffic.sh          Génération de trafic applicatif
│   ├── collect-metrics.py           Métriques DORA et KPI du pipeline
│   └── backup-database.sh           Sauvegarde et restauration de la base
│
├── .github/
│   ├── workflows/ci-cd.yml          Intégration et déploiement continus
│   └── dependabot.yml               Surveillance des dépendances
│
├── docker-compose.yml               Orchestration de l'application
└── docker-compose-elk.yml           Orchestration de la supervision
```

---

## Configuration

### Variables d'environnement de l'application

| Variable | Composant | Rôle | Valeur en conteneur |
|---|---|---|---|
| `MICROCRM_DB_PATH` | back | Emplacement des fichiers de la base | `/data`, monté sur un volume nommé |
| `SPRING_PROFILES_ACTIVE` | back | Profil actif | `container` — active l'envoi des logs vers Logstash |

Hors du profil `container`, les logs restent lisibles sur la console et ne sont envoyés nulle part.
Le développement local n'a donc pas besoin de la stack de supervision.

### Correspondances de ports

| Service | Conteneur | Hôte |
|---|---|---|
| back | 8080 | 8080 |
| front | 8080 | 80 |
| Elasticsearch | 9200 | 9200 |
| Kibana | 5601 | 5601 |
| Logstash | 5044 (back), 5045 (front) | — |

Pour libérer le port 80, modifier la correspondance du service front dans `docker-compose.yml`, par
exemple `"8081:8080"`.

### Réseau et volume

Les deux services de l'application rejoignent le réseau `microcrm-net`, que la supervision rejoint à
son tour. Un volume nommé porte les fichiers de la base : les données survivent à la suppression des
conteneurs.

### Ce qui demande des accès, et à qui

Le projet se clone, se lance, se développe et se teste **sans aucun compte ni jeton**. Deux
opérations font exception.

| Opération | Qui | Accès requis |
|---|---|---|
| Lancer, développer, tester, sauvegarder | Tout le monde | Aucun |
| Mesurer le pipeline au-delà de 60 appels par heure | Tout le monde | Un jeton de son propre compte GitHub, sans portée |
| Analyser la qualité en local | Mainteneurs du dépôt | Un accès à l'organisation SonarQube Cloud du projet |

La dernière ligne mérite une précision. L'analyse de qualité en local remonte vers les projets
`clems2_P7-CICD-Full-Stack_Back` et `_Front`, qui appartiennent à l'organisation du dépôt. Un
contributeur extérieur ne peut donc pas y écrire, et n'en a pas besoin : la chaîne d'intégration
analyse automatiquement chaque pull request.

Les modalités de chaque jeton sont décrites dans [Exécuter les scripts](#exécuter-les-scripts).

### Secrets du pipeline

Le pipeline n'utilise **qu'un seul secret**, le jeton d'analyse de qualité. Il est enregistré deux
fois dans les paramètres du dépôt, dans deux espaces que la plateforme cloisonne : celui des
exécutions ordinaires, et celui réservé aux mises à jour automatiques de dépendances.

Cette séparation n'est pas une redondance. Les workflows déclenchés par la surveillance des
dépendances manipulent du code venu de bibliothèques tierces. Leur refuser l'accès aux secrets
ordinaires limite ce qu'une dépendance compromise pourrait atteindre.

La publication d'images ne demande aucun secret : le jeton fourni automatiquement à chaque exécution
suffit à s'authentifier auprès du registre.

**Aucun secret ne figure en clair dans le dépôt.**

### Projets SonarQube

Deux projets distincts sont rattachés au même dépôt, en mode monorepo :

| Projet | Clé | Périmètre |
|---|---|---|
| MicroCRM Back | `clems2_P7-CICD-Full-Stack_Back` | `back/`, Java |
| MicroCRM Front | `clems2_P7-CICD-Full-Stack_Front` | `front/`, TypeScript et HTML |

Les paramètres du back sont déclarés dans le bloc `sonar` de `back/build.gradle`, ceux du front dans
`front/sonar-project.properties`.

---

## Forker ce dépôt

Le projet se clone et se lance sans aucune modification. En revanche, un fork hérite de références
qui pointent vers le dépôt d'origine. Six éléments sont à reprendre.

| À modifier | Où | Sinon |
|---|---|---|
| Les trois badges en tête de ce fichier | `README.md` | Ils affichent l'état du pipeline du dépôt d'origine, pas du vôtre |
| L'URL de clone | `README.md` | — |
| Les références d'images `ghcr.io/clems2/…` | `README.md`, votre orchestration de déploiement | Vous déployez les images du dépôt d'origine |
| Les clés et l'organisation SonarQube | bloc `sonar` de `back/build.gradle`, `front/sonar-project.properties` | L'analyse échoue : vous n'avez pas accès à l'organisation d'origine |
| Le dépôt par défaut du script de mesure | `REPOSITORY` dans `scripts/collect-metrics.py` | Le script mesure le pipeline du dépôt d'origine |
| Le secret d'analyse | Paramètres de votre dépôt | Le job d'analyse échoue |

Trois points de configuration ne se recopient pas avec le code et sont à refaire dans les
paramètres de votre dépôt :

**Activer les Actions.** GitHub désactive les workflows sur les forks et demande une confirmation
explicite au premier passage dans l'onglet *Actions*.

**Enregistrer le secret d'analyse deux fois.** Dans *Settings → Secrets and variables → Actions*,
puis dans l'onglet *Dependabot* de la même page. Les deux espaces sont cloisonnés : un secret
enregistré dans le premier reste invisible aux mises à jour automatiques.

**Recréer la protection de branche.** Elle n'est pas versionnée. Dans *Settings → Rules*, exiger une
pull request et les quatre contrôles décrits dans [Le pipeline](#le-pipeline).

Si vous forkez pour un autre usage que l'analyse de qualité, supprimez simplement l'étape `sonar`
des deux jobs et les badges correspondants : le reste de la chaîne fonctionne sans elle.

---

## Déploiement

### Images publiées

Chaque fusion sur `main` construit et publie deux images sur GitHub Container Registry :

```bash
docker pull ghcr.io/clems2/microcrm-back:latest
docker pull ghcr.io/clems2/microcrm-front:latest
```

| Étiquette | Rôle |
|---|---|
| `sha-<commit>` | Identifie précisément la version publiée — permet de revenir à un état antérieur |
| `latest` | Dernière version publiée depuis `main` |

### Déployer depuis le registre

> **Prérequis** : Docker démarré. Le dépôt n'a pas besoin d'être cloné, seul le fichier
> d'orchestration est nécessaire.

Les images publiées s'utilisent telles quelles, sans reconstruction. Remplacer la directive `build`
de chaque service par la référence de l'image souhaitée :

```yaml
services:
  back:
    image: ghcr.io/clems2/microcrm-back:latest
  front:
    image: ghcr.io/clems2/microcrm-front:latest
```

C'est ce mode qui correspond à un déploiement réel : l'artefact déployé est exactement celui que la
chaîne d'intégration a validé. Pour un déploiement reproductible, préférer une étiquette
`sha-<commit>` à `latest`.

### Ordre de démarrage

1. Le réseau et le volume de données sont créés s'ils n'existent pas.
2. Le back-end démarre, monte le volume et initialise le schéma.
3. Sa sonde de santé est interrogée jusqu'à ce qu'elle réponde.
4. Le front-end démarre alors seulement, et relaie l'API.
5. La supervision, facultative, est démarrée séparément.

Cet ordre est décrit dans le fichier d'orchestration et appliqué automatiquement.

### Vers un déploiement distant

Il ne manque qu'une **cible d'exécution** : une machine accessible depuis Internet et un nom de
domaine pointant vers elle. Les deux autres prérequis identifiés à l'analyse initiale ont été levés
par le relais de l'API — l'URL de l'API n'est plus figée à la compilation, et le mélange des
protocoles HTTP et HTTPS a disparu.

Quatre modifications sont alors nécessaires.

**1. Faire écouter Caddy sur le nom de domaine.** Le Caddyfile est copié dans l'image au moment du build : le modifier directement imposerait de reconstruire et republier l'image du front, ce qui contredirait le principe « construire une fois, déployer partout » retenu pour l'URL de l'API. Mieux vaut le paramétrer.

```caddy
{
	http_port 8080
	https_port 8443
}

{$SITE_ADDRESS::8080} {
	handle /persons* {
		reverse_proxy back:8080
	}
	handle /organizations* {
		reverse_proxy back:8080
	}
	handle {
		root * /srv
		encode gzip
		try_files {path} /index.html
		file_server
	}
	log {
		output net logstash:5045 {
			soft_start
		}
		format json
	}
}
```

Sans variable définie, Caddy applique :8080 et le comportement local reste identique. Avec SITE_ADDRESS=crm.exemple.fr, il sert ce domaine et demande automatiquement un certificat Let's Encrypt. Les deux directives globales le font écouter sur des ports supérieurs à 1024, compatibles avec l'exécution sous utilisateur non privilégié, tandis que l'orchestration les expose sur 80 et 443.

Le double : de {$SITE_ADDRESS::8080} n'est pas une coquille : le premier sépare la variable de sa valeur par défaut, le second appartient à :8080.

**2. Créer un enregistrement DNS de type A** pour ce domaine, pointant vers l'adresse IP publique de
la machine. Sans lui, Let's Encrypt ne peut pas vérifier que le domaine vous appartient et refuse le
certificat.

**3. Exposer les ports et persister les certificats** dans l'orchestration du serveur :
```yaml
services:
  front:
    image: ghcr.io/clems2/microcrm-front:latest
    environment:
      SITE_ADDRESS: crm.exemple.fr
    ports:
      - "80:8080"
      - "443:8443"
    volumes:
      - caddy-data:/data
```
Le volume porte les certificats émis. Let's Encrypt plafonne le nombre de demandes par domaine et par semaine : sans lui, un conteneur recréé plusieurs fois finirait par se voir refuser un nouveau certificat.

**4. Ajouter un job de déploiement** au workflow, dépendant du job de publication : connexion à la
machine par clé SSH enregistrée en secret, puis `docker compose pull && docker compose up -d`.

Les trois premiers points relèvent de la configuration de l'hébergement. Seul le quatrième modifie
la chaîne d'intégration — et c'est le seul endroit où elle s'arrête aujourd'hui.

---

## Le pipeline

Un fichier de workflow unique, `.github/workflows/ci-cd.yml`.

| Déclencheur | Traitements | Effet en cas d'échec |
|---|---|---|
| Pull request vers `main` | Build, tests et couverture des deux composants, analyse de qualité | Fusion bloquée |
| Push sur `main` | Idem, puis construction et publication des images | Publication annulée |
| Planification quotidienne | Build, tests complets et analyse | Notification, sans blocage |
| Déclenchement manuel | Idem, à la demande | — |

L'exécution planifiée répond à un risque que les autres déclencheurs ne couvrent pas. Certaines
dégradations surviennent sans qu'aucune ligne de code ne change : une dépendance transitive publie
une version incompatible, un jeton expire, un test dont le résultat dépend d'un état non
déterministe finit par échouer.

### Trois jobs

```
back   ─┐
        ├─→  publish  (uniquement sur main, matrice back + front)
front  ─┘
```

Les deux jobs de build s'exécutent en parallèle sur des machines distinctes. La durée totale
correspond donc à celle du job le plus lent, et l'échec d'un composant n'empêche pas d'obtenir le
diagnostic de l'autre. La publication n'intervient qu'après la réussite des deux : aucune image
n'est publiée à partir d'un code non validé.

### Ce que chaque job exécute

| Commande | Ce qu'elle fait | Définie dans | Job |
|---|---|---|---|
| `./gradlew build` | Compile, exécute les tests JUnit et produit le rapport de couverture | `back/build.gradle` | back |
| `./gradlew sonar` | Envoie le code et la couverture à l'analyse de qualité | `back/build.gradle` | back |
| `npm ci` | Installe les dépendances à l'identique du fichier de verrouillage | `front/package-lock.json` | front |
| `npx ng test --watch=false --browsers=ChromeHeadlessNoSandbox` | Exécute les tests Karma et produit la couverture | Workflow | front |
| `npx ng build` | Vérifie que l'application se construit en mode production | `front/angular.json` | front |
| Action de scan SonarQube | Analyse le code TypeScript et transmet la couverture | Workflow | front |
| Action de construction et publication | Construit les deux images et les pousse sur le registre | Workflow | publish |

Une seule commande couvre la compilation, les tests et la couverture du back-end : la tâche `build`
de Gradle inclut `test`, et le rapport JaCoCo y est chaîné par `finalizedBy`. Côté front-end, les
tests et la construction sont deux commandes distinctes — un projet dont les tests passent peut
échouer à se construire en mode production, d'où la vérification séparée.

**Ce sont exactement les commandes utilisables en local.** Un échec de la chaîne d'intégration se
reproduit donc sur le poste de travail, sans avoir à deviner ce que fait le pipeline.

### Protection de la branche principale

Des règles de dépôt appliquent la stratégie de branches, qui n'est donc pas qu'une convention :

- toute modification passe par une pull request — un envoi direct sur `main` est rejeté ;
- **quatre contrôles doivent réussir** avant la fusion : les deux jobs de build et les deux
  contrôles de qualité ;
- les branches doivent être à jour avec `main`, pour que les contrôles portent sur le résultat de la
  fusion et non sur un état antérieur.

Aucune approbation par un relecteur n'est exigée, le projet étant mené par un seul développeur.

### Relancer le pipeline

Trois moyens : le bouton de déclenchement manuel dans l'onglet *Actions*, la relance d'une exécution
complète ou d'un job isolé depuis l'interface, ou un nouveau commit sur une branche ouverte en pull
request.

---

## Choix techniques

### Java 21

Le projet déclarait un niveau de langage 17, alors que son image d'exécution installait déjà un
runtime 21. La construction et l'exécution ne s'accordaient donc pas. L'outil d'analyse refuse par
ailleurs les analyses exécutées sur un runtime inférieur à 21. La toolchain est déclarée dans
`build.gradle` et non héritée de la machine : le poste de développement, la machine d'exécution et
l'image compilent avec la même version.

### Un workflow unique

Les consignes demandent de centraliser la logique d'automatisation dans le workflow d'intégration,
et décrivent le livrable au singulier. Techniquement, plusieurs déclencheurs n'imposent pas
plusieurs fichiers : la plateforme accepte plusieurs événements dans un même workflow, et des
conditions au niveau des jobs suffisent. Séparer les fichiers aurait en revanche introduit une vraie
complexité, celle du passage d'artefacts entre workflows.

### Le serveur web comme point d'entrée unique

Caddy sert les fichiers statiques et relaie `/persons` et `/organizations` vers le back-end. Le
navigateur n'appelle plus l'API sur un port distinct, et l'URL de l'API devient relative.

Ce schéma, standard pour une application web, lève trois problèmes d'un coup. L'URL de l'API n'est
plus figée à la compilation, donc une même image se redéploie ailleurs sans reconstruction. Le CORS
devient inutile, puisque front-end et API partagent la même origine. Et toutes les requêtes
apparaissent dans les logs d'accès, ce qui rend la supervision exploitable : sans ce relais, les
appels à l'API contournaient le serveur web et n'apparaissaient dans aucun log.

### HTTP en local plutôt que HTTPS

La configuration d'origine déclarait un site générique, ce qui activait le chiffrement automatique
avec un certificat émis par une autorité locale. Aucun navigateur ne reconnaissait ce certificat, il
fallait contourner un avertissement à chaque ouverture, et il était régénéré à chaque recréation du
conteneur. Le port 443 exige en outre des privilèges d'administration, incompatibles avec
l'exécution non privilégiée retenue.

Le serveur écoute donc en clair sur un port supérieur à 1024. Ce choix supprime aussi le risque de
contenu mixte. La trajectoire vers un déploiement distant reste directe : Caddy obtient
automatiquement un certificat valide dès qu'un nom de domaine remplace le port d'écoute.

### Un Dockerfile par composant

Le dépôt fournissait un Dockerfile unique à la racine, exposant trois cibles dont une réunissait les
deux composants derrière un superviseur de processus. Le découpage donne à chaque composant un
contexte de build autonome : une modification du front-end n'invalide plus le cache du back-end, et
chaque composant se redémarre indépendamment.

Les deux images suivent le même schéma en deux étapes. La première compile, avec l'outillage complet
— JDK et Gradle d'un côté, Node et la CLI Angular de l'autre. La seconde ne conserve que l'artefact
produit, sur une image d'exécution minimale. Dans les deux cas, les descripteurs de dépendances sont
copiés **avant** les sources : la couche d'installation n'est invalidée que lorsque les dépendances
changent réellement.

Les images s'exécutent sous un utilisateur non privilégié, depuis des images de base officielles et
étiquetées, et portent chacune une sonde de santé.

### Tests hors du build d'image

La construction des images n'exécute pas les tests. La chaîne d'intégration les a déjà validés, et
aucune image n'est publiée sans qu'ils soient passés. **Contrepartie** : une construction manuelle
d'image ne vérifie plus rien par elle-même.

### Base en mode fichier

L'application utilisait par défaut une base en mémoire, dont les données étaient régénérées à chaque
démarrage. Aucune démonstration de sauvegarde ni de restauration n'était possible. La bascule en
mode fichier sur volume nommé ajoute une ligne de configuration, sans service supplémentaire.

### Couverture exigée sur le code nouveau

L'exigence de couverture porte sur le code nouveau ou modifié, non sur l'ensemble du projet. Un
seuil global bloquant aurait interdit toute évolution tant qu'un effort de rattrapage n'aurait pas
été mené. Cette approche fait progresser la couverture globale à mesure que le code évolue, sans
blocage initial.

### Deux fichiers d'orchestration

L'application et la supervision sont décrites séparément, pour que l'application reste démarrable
sans les 4 Go de la stack ELK. **Contrepartie** : la supervision suppose que le réseau de
l'application existe, et un arrêt complet impose d'arrêter les deux ensembles.

### Pas de filtrage par chemins

Les deux jobs s'exécutent même lorsqu'un seul composant est modifié. Le dispositif inverse
supposerait un job de détection, une action tierce et un job d'agrégation pour éviter que les
contrôles obligatoires ne restent en attente. Tout cela pour gagner environ une minute sur des
builds qui en durent moins de deux, et dont le cache absorbe déjà une partie. **Contrepartie
assumée** : une image peut être republiée sous une nouvelle étiquette alors que son contenu n'a pas
changé.

### Stack applicative gelée

Angular 17, Node 20 et Spring Boot 3.2 sont tous sortis de leur période de support. Aucun correctif
de sécurité ne sera publié pour ces versions. La migration représenterait une refonte majeure, hors
du périmètre d'une mission d'industrialisation. Le constat est assumé comme dette technique, avec
une trajectoire de mise à jour décrite dans la documentation technique.

Les montées majeures et mineures d'Angular, de TypeScript et de leur outillage sont donc gelées dans
la configuration de surveillance des dépendances. Les correctifs Angular sont regroupés en une seule
proposition, car ces paquets se verrouillent mutuellement au niveau du correctif.

---

## Contribuer

Modèle **trunk-based** : branches courtes, intégration par pull request, aucune branche
intermédiaire. Les versions sont identifiées par étiquette SemVer, sans branche de publication
dédiée.

```bash
git checkout main && git pull
git checkout -b feat/ma-fonctionnalite
# développement
git push -u origin feat/ma-fonctionnalite
```

Messages de commit au format **Conventional Commits** :

```
<type>(<portée>): <description à l'impératif>

<corps expliquant le pourquoi>
```

Types utilisés : `feat`, `fix`, `refactor`, `build`, `chore`, `docs`, `test`, `ci`.

Avant d'ouvrir une pull request, vérifier en local que `./gradlew build` et les tests front-end
passent. Les mêmes contrôles s'appliqueront automatiquement et bloqueront la fusion en cas d'échec.

---

## Dépannage

**Le port 80 est déjà utilisé.** Modifier la correspondance du service front-end dans
`docker-compose.yml`, par exemple `"8081:8080"`, et accéder à l'application sur
http://localhost:8081.

**Le front-end affiche des listes vides.** L'API n'est probablement pas joignable. Vérifier
`docker compose ps` — le service back-end doit apparaître en *healthy*. L'application ne traite pas
les erreurs de l'API : une panne du back-end se manifeste par des listes vides, sans message. Ce
défaut est recensé dans la documentation technique.

**Les données ne persistent pas.** Vérifier que le volume est bien monté avec
`docker compose config`. Un `docker compose down -v` supprime délibérément les données.

**Kibana ne répond pas.** Compter une à deux minutes après le démarrage. Si l'attente se prolonge,
vérifier la mémoire disponible : la stack ELK en réclame environ 4 Go.

**La supervision ne démarre pas, réseau introuvable.** Le réseau `microcrm-net` est créé par
l'orchestration applicative. Démarrer l'application avant la supervision.

**Le tableau de bord Kibana est vide.** Aucun log n'a encore été reçu, ou la fenêtre temporelle est
trop étroite. Générer du trafic avec `./scripts/generate-traffic.sh`, puis élargir la plage en haut
à droite.

**Les tests front-end ne trouvent pas de navigateur.** Installer Chrome ou Chromium, puis exporter
`CHROME_BIN`.

**Le wrapper Gradle n'est pas exécutable.** Sous Linux après certaines copies de fichiers :
`chmod +x back/gradlew`.

**`collect-metrics.py` échoue sur une limite de requêtes.** GitHub restreint les appels anonymes à
soixante par heure. Fournir un jeton de son propre compte, comme décrit dans
[Mesurer le pipeline](#mesurer-le-pipeline).

---

## Documentation

La **documentation technique** du projet est déposée avec les livrables. Elle couvre les étapes de
mise en œuvre du pipeline, les plans de conteneurisation et de déploiement, de testing périodique,
de sécurité, de sauvegarde et de mise à jour, ainsi que les métriques DORA, les KPI et l'analyse du
monitoring.
