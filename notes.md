# Mes notes Docker

## ⭐ À RETENIR ABSOLUMENT
1. **Image = recette** (figée, lecture seule). **Conteneur = plat** préparé à partir de l'image. 1 image → plusieurs conteneurs.
2. **Un conteneur vit tant que son programme principal tourne** (bash → `exit` l'arrête ; nginx tourne en continu ; `app.py` s'arrête quand il a fini).
3. **`docker ps`** = conteneurs qui **tournent** ; **`docker ps -a`** = **tous** (même arrêtés). Erreur « name already in use » → regarder `ps -a`.
4. **`docker run`** = **nouveau** conteneur ; **`docker start`** = **rallumer** un conteneur existant.
5. **Ménage dans l'ordre** : `docker stop` → `docker rm` (conteneur) → `docker rmi` (image). Ou `docker run --rm` pour supprimer automatiquement.
6. **`-p` et `-v` = DEHORS : DEDANS** (`-p 8080:80`, `-v "$PWD/site:/usr/share/nginx/html:ro"`). Port extérieur unique sur le PC, port intérieur peut être le même partout.
7. **Fichiers** : dans le conteneur → **perdus** au `docker rm`. Dans un **volume** → **sur le PC**, ils survivent, et changent en direct.
8. **COPY = photocopie figée au build** ; **volume = tunnel en direct**. Modifier un fichier copié → refaire `build` + nouveau `run`.
9. **Dockerfile** : `FROM` (base) → `WORKDIR` (dossier) → `COPY` (fichiers) → `RUN` (**au build, une fois**) → `CMD` (**à chaque run**).
10. **`docker build -t nom .`** → ne jamais oublier le **`.`** (contexte de build = dossier avec le Dockerfile et les fichiers).
11. **Cache** : Docker ne refait que les étapes modifiées… et **toutes celles d'après**.
12. **Réflexes terminal** : ne jamais coller le prompt ni un message d'erreur ; une URL va dans le navigateur ou après `curl` ; nano = **Ctrl+O, Entrée, Ctrl+X** ; `-it` et nano → toujours dans un vrai terminal interactif.
13. **permission denied … docker.sock** → `sudo usermod -aG docker $USER` puis **se déconnecter/reconnecter**.
14. **Démarré ≠ prêt** : une base de données a un **healthcheck** + un **volume** ; l'appli attend avec `condition: service_healthy`. Un conteneur `unhealthy` reste `Up`.
15. **Réglages et secrets hors de l'image** : `environment:` + `${VAR}` lu dans `.env` ; **`.env` jamais sur GitHub** (`.gitignore`), on versionne un `.env.example`. Un healthcheck ne regarde que le **code de sortie**.
16. **Registre** : `docker tag` puis `docker push utilisateur/nom:version`. **`latest` ≠ la plus récente** (étiquette qui ne bouge pas toute seule) → toujours déployer une **version précise**.

## ⏸️ Où j'en suis (pause du 16/10/2026)
- Notions 1 à 8 validées. **TP 1 de révision validé ✅** (`tp1/SUJET.md`).
- Notions 9 (Docker Compose) et 10 (`build:` + volumes nommés) validées ✅.
- **TP 2 validé ✅** (`tp2/SUJET.md`), « Le livre d'or ».
- Notion 11 (base de données Redis + healthcheck) validée ✅.
- Notion 12 (variables d'environnement, `.env`, secrets) validée ✅.
- Notion 13 (tags et Docker Hub) validée ✅. Image publiée : `hhabchane/bonjour:v2`. Connecté à Docker Hub (`docker login`). **Prochaine étape : TP 3** (révision 11 à 13), puis Kubernetes avec minikube.
- Reprendre : `cd ~/docker-learning`.
- Aide-mémoire de toutes les commandes : `commandes-docker.md`.
- Corrigé du TP 1 : `tp1/CORRIGE.md`.
- Images d'autres projets (spark, cuda…) → **ne pas y toucher**.

---

## 0. Déjà vu (avant le tutorat)
- `docker run hello-world` : télécharge l'image `hello-world` (si absente) et lance un conteneur à partir d'elle.
- `docker images` : liste les images présentes sur ma machine.
- `docker ps` : liste les conteneurs **en cours d'exécution**.
- `docker ps -a` : liste **tous** les conteneurs, y compris ceux qui sont arrêtés.

## 1. Image vs conteneur
- **Image** = la recette (un modèle figé, en lecture seule).
- **Conteneur** = le plat préparé à partir de la recette (une instance qui tourne, qu'on peut arrêter, redémarrer, supprimer).
- Une même image peut servir à lancer plusieurs conteneurs.

## Erreur rencontrée : « permission denied ... docker.sock »
- **Cause** : mon utilisateur n'était pas dans le groupe `docker`, donc pas le droit de parler au démon Docker (le « cuisinier ») via `/var/run/docker.sock` (le « guichet »).
- **Correction** : `sudo usermod -aG docker $USER`, puis se déconnecter/reconnecter. Vérifier avec `groups`.
- Ensuite, plus besoin de `sudo` devant les commandes docker.

## Ce que fait `docker run` (les 4 étapes affichées par hello-world)
1. Le **client** (ma commande) contacte le **démon** (le cuisinier en arrière-plan).
2. Le démon **télécharge l'image** depuis Docker Hub si elle n'est pas déjà sur ma machine.
3. Il **crée un conteneur** à partir de l'image et le lance.
4. Le résultat est renvoyé et affiché dans mon terminal.

## Résultat de l'exercice : 1 image, plusieurs conteneurs
- Après 4 `docker run hello-world` : `docker images` montre **1 seule image**, `docker ps -a` montre **4 conteneurs**.
- Chaque `docker run` crée un **nouveau** conteneur (un nouveau plat), mais réutilise la même image (la recette déjà téléchargée).
- Colonnes utiles de `docker ps -a` :
  - `CONTAINER ID` : identifiant unique du conteneur.
  - `IMAGE` : la recette utilisée.
  - `STATUS` : `Exited (0)` = terminé, et le `0` veut dire « tout s'est bien passé » (un autre chiffre = erreur).
  - `NAMES` : nom donné au hasard par Docker (ex. `happy_rosalind`) si je n'en choisis pas un.
- Colonne `U` (In Use) dans `docker images` : l'image est utilisée par au moins un conteneur.

## 2. Supprimer conteneurs et images
- `docker rm <conteneur>` : supprime un conteneur. On peut donner son **nom** (ex. `goofy_cori`) **ou** son **ID** (les premiers caractères suffisent, ex. `a38`).
- `docker rmi <image>` : supprime une image.
- Ordre logique : d'abord supprimer les conteneurs (les plats), ensuite l'image (la recette).
- Sortie de `docker rmi` :
  - `Untagged: hello-world:latest` : l'étiquette (nom:tag) est retirée.
  - `Deleted: sha256:...` : les données de l'image sont effacées du disque.

## Erreur rencontrée : « No such image: hello-world:latest »
- **Cause** : l'image avait déjà été supprimée juste avant, donc Docker ne la trouve plus.
- **Correction** : rien à corriger. Vérifier avec `docker images` ce qui existe vraiment avant de supprimer.

## Erreur (bis) : « permission denied » revient après `usermod`
- **Cause** : `usermod -aG docker` modifie le compte, mais un terminal déjà ouvert garde les **anciens** groupes. Le changement ne s'applique qu'aux **nouvelles sessions**.
- **Diagnostic** : `groups` (groupes de ce terminal) vs `groups $USER` (groupes enregistrés pour le compte).
- **Correction** : se déconnecter/reconnecter d'Ubuntu (ou redémarrer). Dépannage temporaire, valable dans ce terminal seulement : `newgrp docker`.

## Erreur : « permission: command not found »
- **Cause** : j'ai collé un message d'erreur dans le terminal ; bash a pris le premier mot (`permission`) pour une commande.
- **Correction** : ne coller dans le terminal que des commandes, pas des messages de sortie.

## Erreur : « conflict: unable to delete hello-world:latest (must be forced) »
- Message complet : `container cbd380ba6ad8 is using its referenced image 5e2309035332`.
- **Cause** : un conteneur (même arrêté) utilise encore l'image. Docker refuse de jeter la recette tant qu'un plat préparé avec elle existe.
- **Correction** : supprimer d'abord le conteneur (`docker rm <id ou nom>`), puis l'image (`docker rmi hello-world`).
- `-f` (force) existe (`docker rmi -f`), mais à éviter quand on débute : mieux vaut faire le ménage dans l'ordre.
- ✅ Ma prédiction était juste : Docker refuse de supprimer une image utilisée par un conteneur.

## 3. Entrer dans un conteneur
- `docker pull ubuntu` : télécharge l'image **sans** lancer de conteneur (aller chercher la recette sans cuisiner).
  - `Using default tag: latest` : sans précision, Docker prend la version `latest`.
  - Les lignes `Pull complete` = l'image est faite de plusieurs **couches** (layers) téléchargées séparément.
- `docker run -it ubuntu bash` : lance un conteneur Ubuntu et ouvre un terminal **dedans**.
  - `-i` = interactif (le conteneur écoute ce que je tape), `-t` = donne un terminal, `bash` = programme lancé dans le conteneur.
- Le prompt change : `root@ebb9bdcda9a1:/#`
  - `root` = je suis administrateur **dans** le conteneur.
  - `ebb9bdcda9a1` = nom de la machine = **ID du conteneur**.
  - `/` = je suis à la racine du système de fichiers du conteneur ; `#` = prompt de root.
- Dedans : un mini-Ubuntu complet (`ls` montre bin, etc, home…), isolé de mon PC.
- `exit` : sortir du conteneur → le conteneur s'arrête (`Exited`).
- ⚠️ Les commandes `-it` doivent être tapées dans un vrai terminal interactif.
- Après `exit` : le conteneur est **arrêté** (`Exited`), mais **pas supprimé** → il apparaît dans `docker ps -a` mais pas dans `docker ps`.
- Pourquoi ? Un conteneur vit tant que son programme principal (ici `bash`) tourne. `exit` ferme bash → le conteneur s'arrête.
- Relancer `docker run -it ubuntu bash` crée un **nouveau** conteneur (nouvel ID, nouveau nom), il ne reprend pas l'ancien.

## Erreur : « bash: habchane@habchane-ThinkPad-T14-Gen-1:~/docker-learning$: No such file or directory »
- **Cause** : j'ai collé une ligne de prompt dans le terminal du conteneur ; bash l'a prise pour un chemin de fichier à exécuter (à cause du `/`), qui n'existe pas.
- **Correction** : ne taper que la commande, jamais le prompt (`user@machine:~$`) qui est devant.

## Révision autonome (sans aide) ✅
- `docker pull ubuntu` alors que l'image est déjà là → `Status: Image is up to date` : rien n'est retéléchargé.
- Nouveau `docker run -it ubuntu bash` → nouveau conteneur `b61919c4de00` (`gifted_bouman`) : confirme qu'un `run` = un nouveau conteneur.
- `docker rm` accepte **plusieurs** conteneurs d'un coup : `docker rm id1 id2`.
- Ménage complet dans le bon ordre : conteneurs (`rm`) puis image (`rmi`).

## 4. Nommer un conteneur et le rallumer
- `docker run --name mon-ubuntu -it ubuntu bash` : je choisis le nom du conteneur (au lieu d'un nom au hasard).
- `Unable to find image 'ubuntu:latest' locally` → `docker run` télécharge l'image tout seul si elle manque (pas besoin de `pull` avant).
- `docker start -ai mon-ubuntu` : **rallume** un conteneur arrêté et entre dedans (`-a` = attach, affiche sa sortie ; `-i` = interactif).
  - Même ID (`fc917e3fe29b`) → c'est **le même** conteneur, pas un nouveau.
- Les fichiers créés dans un conteneur **restent dans ce conteneur** : `/test.txt` est toujours là après `start`.
- Un **nouveau** conteneur (`docker run`) part de l'image **propre** : `/test.txt` n'existe pas.
  - Analogie : l'image est la recette d'origine (jamais modifiée) ; chaque plat a sa propre garniture.
- ⚠️ Si je supprime le conteneur (`docker rm`), ses fichiers disparaissent avec lui.

## Erreur : « cat: /test.txt: No such file or directory » (dans un nouveau conteneur)
- **Cause** : ce n'est pas un bug, c'est un nouveau conteneur créé depuis l'image d'origine, qui ne contient pas le fichier (il a été créé dans `mon-ubuntu` seulement).
- **Correction** : pour retrouver le fichier, rallumer le bon conteneur : `docker start -ai mon-ubuntu`.

## Erreur : « Conflict. The container name "/mon-ubuntu" is already in use »
- **Cause** : deux conteneurs ne peuvent pas avoir le même nom. `mon-ubuntu` existe déjà (arrêté, mais il existe).
- **Correction** (au choix) :
  - je veux le même conteneur → `docker start -ai mon-ubuntu` ;
  - je veux un nouveau conteneur avec ce nom → `docker rm mon-ubuntu` puis `docker run --name mon-ubuntu ...` ;
  - ou choisir un autre nom : `--name mon-ubuntu2`.
- Même **nom** ≠ même **conteneur** : après `docker rm mon-ubuntu` puis `docker run --name mon-ubuntu ...`, c'est un conteneur neuf (nouvel ID), sans `/test.txt`.
- Résumé : `docker run` = **nouveau** conteneur ; `docker start` = **rallumer** un conteneur existant.

## 5. Serveur web en arrière-plan (nginx)
- `docker run --name mon-site -d -p 8080:80 nginx`
  - `-d` (detached) : le conteneur tourne **en arrière-plan**, Docker me rend la main et affiche seulement l'**ID complet** du conteneur.
  - `-p 8080:80` : **dehors : dedans** → port 8080 de mon PC relié au port 80 du conteneur (où nginx écoute).
- `docker ps` → `STATUS: Up 42 seconds` (il tourne) et `PORTS: 0.0.0.0:8080->80/tcp` (la redirection de port).
- Navigateur : http://localhost:8080 → page « Welcome to nginx! ».
- `docker logs mon-site` : le journal du conteneur.
  - Les premières lignes = démarrage de nginx.
  - `"GET / HTTP/1.1" 200` = une visite ; **200** = succès.
  - `172.17.0.1` = l'adresse de mon PC vue depuis le conteneur (le « réseau Docker »).
- `docker stop mon-site` : arrête le conteneur → plus de serveur → le navigateur affiche **« Unable to connect »**.
  - Le conteneur n'est pas supprimé : `docker start mon-site` le rallume (sans `-ai`, il reste en arrière-plan).

## Erreur dans les logs : « open() "/usr/share/nginx/html/favicon.ico" failed » + `404`
- **Cause** : le navigateur demande automatiquement une petite icône d'onglet (`favicon.ico`) ; nginx n'en a pas → **404** = « pas trouvé ».
- **Correction** : rien à faire, c'est sans gravité (la page elle-même a bien répondu 200).
- Un conteneur reste `Up` tant que son **programme principal** tourne. nginx est un serveur qui ne s'arrête jamais tout seul → il reste allumé. `-d` ne le garde pas en vie, il me **rend juste la main**.
- Ports : chaque conteneur a son **propre réseau isolé** → plusieurs conteneurs peuvent utiliser le port 80 **dedans**. Mais sur mon PC, chaque port **extérieur** doit être **différent** (`-p 8080:80`, `-p 8081:80`… → http://localhost:8081).

## 6. Les volumes (partager un dossier PC ↔ conteneur)
- `docker run --name mon-site -d -p 8080:80 -v "$PWD/site:/usr/share/nginx/html:ro" nginx`
  - `-v dehors:dedans` : le dossier `site` de mon PC **est** le dossier `/usr/share/nginx/html` du conteneur (le même dossier, vu des deux côtés).
  - `$PWD` (ou `$(pwd)`) = chemin complet du dossier courant. Docker exige un chemin complet.
  - Les guillemets `"..."` protègent le chemin s'il contient des espaces.
  - `:ro` (read-only) = le conteneur peut **lire** le dossier mais pas le modifier. Bonne pratique pour un site web.
- `curl http://localhost:8080` : affiche la page dans le terminal (sans navigateur).
- Après `docker rm mon-site`, `site/index.html` est **toujours là** sur mon PC : les fichiers d'un volume survivent au conteneur.

## Erreur : « Conflict. The container name "/mon-site" is already in use » alors que `docker ps` est vide
- **Cause** : `docker ps` ne montre que les conteneurs **qui tournent**. `mon-site` était arrêté (`docker stop`) mais existait encore → visible seulement avec `docker ps -a`.
- Changer le port (`-p 8081:80`) ne change rien : c'est le **nom** qui pose problème, pas le port.
- **Correction** : `docker rm mon-site`, puis relancer. Réflexe : vérifier avec `docker ps -a`.
- ✅ Test en direct : modifier `site/index.html` sur mon PC → `curl` montre **immédiatement** la nouvelle version, **sans redémarrer** le conteneur (c'est le même dossier des deux côtés).

## Erreur : « bash: http://localhost:8080: No such file or directory »
- **Cause** : une adresse web n'est pas une commande. Bash a essayé de l'exécuter comme un fichier (à cause des `/`).
- **Correction** : l'adresse va dans la barre du navigateur, ou après `curl` dans le terminal : `curl http://localhost:8080`.

## 7. Le Dockerfile : créer sa propre image (dossier `exercices/07-dockerfile-nginx/`)
- **Dockerfile** = fichier texte nommé exactement `Dockerfile` = ma propre **recette**.
  ```
  FROM nginx                          # image de départ (toujours en 1re ligne)
  COPY site/ /usr/share/nginx/html/   # copie mes fichiers (PC → image)
  ```
- `docker build -t mon-site-image .`
  - `-t` = nom (tag) de l'image ; `:latest` est ajouté automatiquement.
  - `.` = le **contexte** : le dossier où se trouvent le Dockerfile et les fichiers à copier. Ne pas l'oublier !
  - Dans la sortie, `[1/2]`, `[2/2]` = une étape par instruction du Dockerfile.
- `docker run --name site-v1 -d -p 8080:80 mon-site-image` : on lance **ma** image comme n'importe quelle autre.
- **COPY vs volume** :
  - COPY = **photocopie** figée dans l'image au moment du `build`. Modifier le fichier sur le PC ensuite ne change **rien** (vérifié : j'ai écrit « Version 4 », le site affiche toujours « Version 3 »).
  - Volume = **tunnel** en direct vers le PC.
  - L'image avec COPY est **autonome** : elle peut tourner sur n'importe quel ordinateur, sans mon dossier `site/`.
- `echo '...' > fichier` écrase/crée ; `echo '...' >> fichier` **ajoute** une ligne à la fin.
- `curl -s` = mode silencieux (cache la barre de progression).

## Erreur : « cat: Dockerfile: No such file or directory »
- **Cause** : le fichier n'avait jamais été sauvegardé dans nano.
- **Correction** : dans nano, **Ctrl+O** puis **Entrée** (vérifier le message `[ Wrote N lines ]`), puis **Ctrl+X**. Ou créer le fichier avec `echo ... >` et `echo ... >>`.
- Attention : deux terminaux différents peuvent être dans des dossiers différents → vérifier avec `pwd`.
- Rebuild : `FROM ... CACHED` = Docker réutilise ce qui n'a pas changé (le **cache**) ; seul `COPY` est refait → beaucoup plus rapide.
- Après un rebuild, `mon-site-image:latest` a un **nouvel ID** : le nom est une **étiquette** déplacée sur la nouvelle image.
- Pour mettre à jour un site « image » : `build` → `stop` + `rm` l'ancien conteneur → `run` un nouveau. (Astuce : faire le `build` d'abord pour réduire la coupure.)

## Erreur : « 'docker buildx build' requires 1 argument ... PATH »
- **Cause** : j'ai oublié le `.` → Docker ne sait pas quel dossier utiliser comme **contexte de build**.
- **Contexte de build** = le dossier envoyé à Docker : il y trouve le `Dockerfile` **et** les fichiers que `COPY` va chercher (`site/`). Les chemins de `COPY` sont relatifs à ce dossier.
- `buildx` = le moteur de construction moderne derrière `docker build`.
- **Correction** : `docker build -t mon-site-image .`

## 8. Empaqueter une application Python (dossier `exercices/08-dockerfile-python/`)
```
FROM python:3.13-slim        # image de départ : un Python léger
WORKDIR /app                 # dossier de travail dans l'image (créé si besoin), comme un cd
COPY app.py .                # copie app.py dans /app (le . = le WORKDIR)
RUN date > build-info.txt    # exécuté UNE FOIS, pendant le build → résultat figé dans l'image
CMD ["python", "app.py"]     # exécuté à CHAQUE démarrage de conteneur
```
- **RUN = au build** (une fois) ; **CMD = au run** (à chaque fois).
- `CMD` s'écrit comme une liste : `["programme", "argument"]`, avec des guillemets doubles.
- Vérifié avec 2 lancements à ~2 min d'écart :
  - « Image construite le » = **identique** (11:09:15) → figé par `RUN` au build.
  - « Conteneur lancé le » = **change** (11:10 puis 11:12) → calculé par `CMD` à chaque run.
- `docker run --rm mon-app` : le conteneur est **supprimé automatiquement** à l'arrêt → `docker ps -a` ne le montre plus.
- Un conteneur qui exécute un programme court (comme `app.py`) s'arrête dès que le programme se termine (même règle que bash et hello-world).
- Dans la sortie du build, `[1/4] ... [4/4]` = une étape par instruction (FROM, WORKDIR, COPY, RUN). `CMD` n'est pas une étape : il ne fait rien au build, il est juste enregistré.
- Les conteneurs utilisent l'heure **UTC** par défaut (d'où le décalage avec mon horloge).
- Cache et `RUN` : modifier `app.py` casse le cache à partir de `COPY` → `RUN date` est refait → nouvelle date. Rebuild **sans rien changer** → tout `CACHED` → la date **ne change pas**.

## TP 1 (révision) : corrigé et leçons
- ✅ Réussi : conteneur persistant + `start -ai`, conflit de nom, volume `:ro` en direct, fichiers qui survivent au `rm`, Dockerfile commenté, tags `portfolio:v1` / `portfolio:v2`, 2 nginx en même temps (8080 / 8081), cache `CACHED`, rebuild Bonjour → Salut, ménage `stop` / `rm` / `rmi` sur plusieurs éléments d'un coup.
- **alpine** : Linux minuscule (13 MB contre 162 MB pour ubuntu). Pas de `bash` → on utilise **`sh`** (`docker run -it alpine sh`). Prompt : `/ #`.
- `#` dans un Dockerfile = **commentaire** (ignoré par Docker).
- `sed -i 's/ancien/nouveau/' fichier` : remplace un texte dans un fichier, directement.
- **Piège `curl -s`** : en mode silencieux, curl cache **aussi les erreurs**. Une réponse **vide** = souvent « aucun serveur sur ce port » → vérifier avec `docker ps`. (`build` crée une image, il ne lance **aucun** conteneur !)
- Le cache est partagé entre projets : `CACHED [2/4] WORKDIR /app` vient d'un build précédent (`mon-app`) qui avait exactement la même étape.

## TP 1 : validé ✅
- Toutes les parties faites : alpine ×3 + `rmi` refusé (prédiction juste), conteneur persistant, volume + logs (9000), comparaison volume (9000) / image (9001), appli Python `appli:1.0` / `appli:2.0`, ménage complet.
- Questions finales : 8/8 après complément. Points à retenir de la correction :
  - Toujours **aller jusqu'au bout** de l'explication : la règle **et** son application à l'exemple.
  - `WORKDIR` fixe le dossier où `CMD` s'exécute (`os.getcwd()` → `/app`).
  - Conflit de nom → `docker ps -a`, puis `start` (réutiliser), `rm` (recréer) ou **un autre nom**.

## 9. Docker Compose (dossier `exercices/09-docker-compose/`)
- **Compose = un menu** : on décrit tous les conteneurs (services) dans un fichier `compose.yaml`, puis une seule commande lance tout.
- Squelette :
  ```yaml
  services:
    web:
      image: nginx
      ports:
        - "8080:80"
      volumes:
        - ./site:/usr/share/nginx/html:ro
  ```
- YAML : **espaces uniquement** (jamais de tabulations), 2 espaces par niveau, `-` devant chaque élément de liste.
- Dans `volumes`, `./` = à côté du `compose.yaml` (plus besoin de `$PWD`).
- Commandes (à lancer dans le dossier du `compose.yaml`) :
  - `docker compose up -d` : crée et lance tous les services en arrière-plan.
  - `docker compose ps` : conteneurs du projet.
  - `docker compose logs` : logs de tous les services.
  - `docker compose down` : arrête **et supprime** les conteneurs du projet.
- `mkdir -p a/b/c` : crée tous les dossiers du chemin d'un coup.
- ✅ Exercice 1 réussi : ma commande `docker run -d -p 8080:80 -v ... nginx` traduite en `compose.yaml` (service `web`).
- **Nom du conteneur** : `<projet>-<service>-<numéro>` → `09-docker-compose-web-1`. Le **projet** = nom du dossier qui contient le `compose.yaml`.
- Compose crée automatiquement un **réseau** pour le projet (`09-docker-compose_default`) : c'est pour ça que l'adresse dans les logs est `172.21.0.1` (et plus `172.17.0.1`, le réseau Docker par défaut).
- `docker compose logs` préfixe chaque ligne par le service (`web-1 |`), pratique quand il y a plusieurs services.
- `docker compose down` → `Container ... Removed` **et** `Network ... Removed` : supprime conteneurs + réseau du projet. Mes fichiers (`site/`) restent sur le PC (prédiction confirmée).
- ✅ Exercice 2 réussi : 2 services `web` (nginx) + `client` (alpine) dans le même `compose.yaml`.
  - `command:` = remplace la commande par défaut de l'image (comme `docker run image commande`, ou `CMD`).
  - `depends_on:` = ordre de **démarrage** (web avant client). ⚠️ Ne garantit pas que web est **prêt** à répondre (sans `sleep`, ça a marché ici car nginx démarre très vite, mais ce n'est pas garanti).
  - `client` affiche ma page avec `wget -qO- http://web` → **le nom du service sert d'adresse** sur le réseau du projet (DNS interne de Compose).
  - `client` → `Exited (0)` : son programme principal (`wget`) a fini → le conteneur s'arrête. `web` → `Up` (nginx tourne en continu).
  - Un service sans `ports:` n'est pas joignable depuis le PC, mais il peut appeler les autres services.

## Erreur : « curl: (6) Could not resolve host: web » (depuis le PC)
- **Cause** : le nom `web` n'existe que **dans le réseau Compose**. Mon PC ne le connaît pas.
- **Correction** : depuis le PC, passer par le port publié : `curl http://localhost:8080`.

## Piège : `wget -qO- http://web` sur le PC n'affiche rien
- `-q` (quiet) cache **aussi les erreurs** (comme `curl -s`). Une sortie vide ≠ succès.
- **À retenir** : service → service = **pas besoin de `ports:`** (nom du service + port **interne**, ex. `http://web` = port 80) ; PC → conteneur = **besoin de `ports:`** (`localhost:8080` → `web:80`).

## 10. `build:` et volumes nommés (mini-projet compteur, dossier `exercices/10-compose-volume/`)
- `build: .` dans `compose.yaml` = Compose construit l'image avec le Dockerfile du dossier (au lieu de `image:`). Image nommée `<projet>-<service>` (ex. `09-docker-compose-compteur`).
- `docker compose up -d --build` : reconstruit les images avant de lancer (le cache sert si rien n'a changé).
- **Volume nommé** = casier **géré par Docker** (pas un dossier de mon PC). Syntaxe : `donnees:/data` (pas de `./`), et **déclaration obligatoire** en bas :
  ```yaml
  volumes:
    donnees:
  ```
  Nom réel : `<projet>_<volume>` → `09-docker-compose_donnees` (`docker volume ls`).
- Partagé entre services : `compteur` écrit dans `/data`, `web` lit le **même** volume dans `/usr/share/nginx/html:ro`.
- `depends_on` avec `condition: service_completed_successfully` : `web` attend que `compteur` soit **terminé avec succès** (`Exited (0)`). Résout le problème « démarré ≠ prêt ».
- `docker compose start compteur` : relance le service arrêté → compteur 3, puis 4.
- Résultats vérifiés :
  - `down` puis `up` → compteur **continue** (1 → 2) : `down` supprime conteneurs + réseau, **pas** les volumes nommés.
  - `down -v` → `Volume ... Removed` → au prochain `up`, nouveau volume vide → compteur **repart à 1**. ⚠️ `-v` efface les données !
- Rangement : le projet a d'abord été fait par erreur dans `09-docker-compose/` (d'où les noms `09-docker-compose_*` ci-dessus). Déplacé ensuite dans `10-compose-volume/` → le projet s'appelle maintenant `10-compose-volume` (volume `10-compose-volume_donnees`).
- ⚠️ Toujours vérifier `pwd` avant de créer des fichiers : un `compose.yaml` écrit dans le mauvais dossier **remplace** celui qui y était.
- `docker compose down -v` doit être lancé **dans le dossier du projet**, et ne pas être suivi d'un `up` si on veut que tout reste arrêté.

## TP 2 : « Le livre d'or » (dossier `tp2/`)
- 3 services : `generateur` (mon image Python, `build: .`), `web` (nginx, seul à publier un port), `testeur` (alpine, appelle `http://web`).
- Deux types de stockage dans le même projet :
  - `./entree:/entree:ro` (**bind mount**) = mes messages, sur mon PC → survivent à tout, même à `down -v`.
  - `pages:/pages` (**volume nommé**) = fichiers produits par l'appli (`index.html`, `compteur.txt`) → effacés par `down -v`.
- Ajouter un message ne change pas la page tout seul : le générateur a fini son travail. Il faut le relancer : `docker compose start generateur`.
- Persistance vérifiée : `up` → 1 ; `down` + `up` → 2 (pas de `Volume Created`) ; `down -v` + `up` → 1 (`Volume Removed` puis `Created`).
- `down` arrête les services dans l'**ordre inverse** du démarrage (testeur → web → generateur).

## Panne volontaire : « service "generateur" didn't complete successfully: exit 1 »
- **Provoquée** en renommant `entree/messages.txt` → Python : `FileNotFoundError: ... '/entree/messages.txt'`.
- États : `generateur` → `Exited (1)` ; `web` et `testeur` → **`Created`** (créés mais **jamais démarrés**, ≠ `Exited`).
- Lire un traceback Python **de bas en haut** : dernière ligne = la cause ; ligne `File "/app/generateur.py", line 12` = l'endroit dans mon code.
- **Correction** : remettre le fichier, puis `docker compose up -d` (relance les conteneurs existants).
- `condition: service_completed_successfully` empêche nginx de servir une ancienne page ou une page vide : la panne devient **visible**.
- Le compteur n'a pas bougé pendant la panne : Python a planté **avant** d'écrire le compteur.

## Ménage complet
- `docker compose down -v` dans **le dossier du projet** (`cd ../exercices/10-compose-volume && docker compose down -v`), puis `docker rmi` des images construites.
- Garder les images de base (`alpine`, `nginx`, `ubuntu`) évite de les retélécharger.

## TP 2 : validé ✅ (questions finales)
- On met dans l'image **le code** (change rarement) et on laisse dehors **les données** (changent souvent) → `messages.txt` en bind mount, pas en `COPY`.
- Compose = tous les services lancés/arrêtés en **une commande**, configuration écrite dans un fichier, réseau créé automatiquement.
- Nom du projet = nom du **dossier** du `compose.yaml` (`docker-learning` à la racine, `tp2` dans `tp2/`).
- `image:` = image existante ; `build:` = construite avec mon Dockerfile (nom `<projet>-<service>`).
- `depends_on` attend le **démarrage** ; `service_completed_successfully` attend la **réussite**.
- Partie 4 : seul le générateur devait refaire la page → `docker compose start generateur` suffit ; `web` tourne toujours et lit le même volume.

## 11. Base de données + healthcheck (dossier `exercices/11-healthcheck-redis/`)
- Problème : **démarré ≠ prêt**. Une base de données met quelques secondes à se préparer ; une appli qui s'y connecte trop tôt plante (erreur de connexion).
- **Redis** = base de données « clé → valeur », très simple. Image `redis`, port **6379**, données dans **`/data`** → volume nommé. `redis-cli ping` répond `PONG` quand elle est prête.
- L'appli (`app.py`) : `redis.Redis(host="db", port=6379)` (nom du **service**, DNS interne) ; `r.incr("visites")` = +1 dans Redis et renvoie la nouvelle valeur.
- **Healthcheck** = un test lancé régulièrement **dans** le conteneur :
  ```yaml
  db:
    image: redis
    volumes:
      - donnees:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]   # réussit = en bonne santé
      interval: 2s                         # un test toutes les 2 s
      timeout: 2s                          # test trop long = échec
      retries: 5                           # 5 échecs de suite = unhealthy
  ```
  États visibles dans `docker compose ps` : `(health: starting)` → `(healthy)` 💚 ou `(unhealthy)` 💔.
- Côté appli : `depends_on: db: condition: service_healthy` → `app` démarre seulement quand `db` est **healthy** (Compose affiche `Waiting` puis `Healthy`). Vérifié **à chaque démarrage**, même pour un `docker compose start app`.
- Analogie : un serveur passe régulièrement en cuisine demander « prêts ? » et ne fait entrer les clients qu'après un « oui ».
- Dockerfile : `RUN pip install redis` **avant** `COPY app.py .` → si je modifie seulement mon code, Docker réutilise l'installation en cache. En haut ce qui change rarement (et prend du temps), en bas ce qui change souvent.
- `PORTS` = `6379/tcp` **sans flèche** → port ouvert seulement dans le réseau du projet, pas vers le PC.
- Résultats vérifiés :
  - `up` → visite 1 ; deux `start app` → 2, 3 (même conteneur → les logs **s'accumulent**).
  - `down` + `up` → **4**, sur une seule ligne de logs : nouveau conteneur (logs neufs), mais données gardées dans le **volume**.
  - Conteneur supprimé → logs perdus ; volume conservé → données conservées. C'est pour ça qu'une base a toujours un volume.
  - Modifier la config d'un service → `Recreate` de **ce** service seulement ; un service inchangé est juste rallumé (il garde ses logs : 4 puis 5).
  - `down -v` → `Volume ... Removed` → compteur perdu, on repartirait à 1.

## Panne volontaire : « dependency failed to start: container 11-healthcheck-redis-db-1 is unhealthy »
- **Provoquée** en changeant le test : `["CMD", "redis-cli", "-p", "9999", "ping"]` (mauvais port, Redis écoute sur 6379).
- **Cause** : 5 échecs × 2 s ≈ **10 s** → `db` déclaré `unhealthy` → Compose refuse de démarrer `app`.
- États : `db` → **`Up (unhealthy)`** (un healthcheck **n'arrête pas** le conteneur, il pose juste une étiquette ; ce sont Compose, et plus tard Kubernetes, qui décident quoi en faire) ; `app` → pas démarré (`Exited (0)` s'il existait déjà, `Created` s'il est neuf).
- **Correction** : remettre `["CMD", "redis-cli", "ping"]`, puis `docker compose up -d`.
- Modifier un fichier sans éditeur : `sed -i 's/ANCIEN/NOUVEAU/' fichier` (rechercher / remplacer).

## Erreurs de la notion 11
- `cat: app.py: No such file or directory` → le fichier n'était **pas encore créé** : `cat` **lit**, il ne crée pas. D'abord créer (nano, `printf`…), ensuite vérifier.
- `app.py` créé à la racine `~/docker-learning/` au lieu du dossier de l'exercice → le terminal Ubuntu n'était pas dans le bon dossier. Correction : `mv ~/docker-learning/app.py ~/docker-learning/exercices/11-healthcheck-redis/`. Chaque terminal a **son propre** dossier courant → `pwd` avant de créer un fichier.
- `nano` : « Standard input is not a terminal » → nano est interactif, il lui faut un **vrai terminal interactif**. Sinon : `printf '%s\n' 'ligne 1' 'ligne 2' > fichier`.
- Modification de `compose.yaml` pas prise en compte → fichier non sauvegardé (vérifiable avec `ls -l` : l'heure de modification n'avait pas changé).
- Commande écrite comme un simple message au lieu d'être exécutée → rien ne se passe : vérifier le résultat (`docker ps -a`, `ls`) quand une commande n'affiche rien d'attendu.

## Notion 11 : validée ✅
- `depends_on` simple attend que le conteneur **démarre** ; `service_healthy` attend que son **healthcheck réussisse**. Sans lui, l'appli peut se connecter à Redis trop tôt et recevoir une erreur de connexion.
- `RUN pip install` avant `COPY` → profiter du cache : modifier seulement `app.py` ne refait pas l'installation.

## 12. Variables d'environnement, `.env` et secrets (dossier `exercices/12-variables-env/`)
- Problème : un réglage écrit **en dur** dans le code (`host="db"`) oblige à modifier le code **et** reconstruire l'image pour le changer.
- **Variable d'environnement** = paire `NOM=valeur` donnée au conteneur **au démarrage** (pas au build). Analogie : l'image = la **recette**, les variables = les **réglages du four** ; une seule recette, réglée différemment selon la cuisine.
- `docker run --rm -e PRENOM=Hicham alpine env` → `PRENOM=Hicham` apparaît dans la liste. Sans `-e`, il disparaît. Docker ajoute toujours `PATH`, `HOME` et `HOSTNAME` (= l'ID du conteneur, différent à chaque `run`).
- En Python : `os.environ.get("NOM_APP", "Sans nom")` lit la variable (valeur par défaut si elle est absente ; sans défaut → `None`).
- Dans Compose :
  ```yaml
  app:
    environment:
      REDIS_HOST: db
      NOM_APP: Mon super compteur
      REDIS_PASSWORD: ${REDIS_PASSWORD}   # valeur lue dans le fichier .env
  ```
- Changer `NOM_APP` puis `docker compose up -d` (**sans** `--build`) → **pas de reconstruction**, seul `app` est recréé (sa config a changé), `db` est inchangé. Même image, autre réglage.
- **`.env`** : fichier à côté du `compose.yaml`, lu **automatiquement** par Compose. Une ligne `REDIS_PASSWORD=motdepasse123` (pas d'espaces autour du `=`). Dans `compose.yaml`, `${REDIS_PASSWORD}` est remplacé par sa valeur.
- Fichier qui commence par un point = **caché** : `ls` ne le montre pas, `ls -a` oui. Caché ≠ protégé.
- Redis avec mot de passe : `command: ["redis-server", "--requirepass", "${REDIS_PASSWORD}"]`.
- **Ne jamais versionner `.env`** : protégé par la règle `*.env` du `.gitignore` (`git check-ignore -v .env` → `.gitignore:9:*.env`). On versionne à la place un **`.env.example`** avec des valeurs bidon (`REDIS_PASSWORD=change-moi`) : il se termine par `.example`, donc il n'est pas ignoré.
- `.env` protège contre la **fuite sur GitHub**, **pas** contre quelqu'un qui a accès à Docker : `docker compose config` (le fichier après remplacement des `${...}`) et `docker inspect` affichent le mot de passe en clair. → Contrôler qui est dans le groupe `docker` ; dans Kubernetes : les **Secrets**.

## Piège : le healthcheck qui ment 🤥
- Mot de passe ajouté à Redis, mais healthcheck resté `["CMD", "redis-cli", "ping"]` → `db` **`(healthy)`** quand même, et `app` plante.
- Preuve : `docker compose exec db redis-cli ping; echo $?` → `NOAUTH Authentication required.` **et** code `0`.
  - `docker compose exec <service> <commande>` = lancer une commande **dans** un conteneur qui tourne.
  - `$?` = code de sortie de la **dernière** commande (0 = réussite).
- **Cause** : un healthcheck ne lit pas la réponse, il regarde **seulement le code de sortie**. `redis-cli` renvoie 0 même quand Redis refuse.
- **Correction** : `test: ["CMD-SHELL", "redis-cli -a ${REDIS_PASSWORD} ping | grep PONG"]` → `grep` renvoie 0 **seulement** s'il trouve `PONG`. `CMD-SHELL` est nécessaire pour le tuyau `|` (fonction du shell).
- Leçon (valable aussi pour Kubernetes) : un test de santé doit vérifier que le service fait **vraiment** son travail, pas seulement qu'il répond quelque chose.

## Erreur : `redis.exceptions.AuthenticationError: HELLO must be called with the client already authenticated...`
- **Cause** : Redis exige un mot de passe et `app` n'en a pas reçu → `Exited (1)`.
- **Correction** : ajouter `REDIS_PASSWORD: ${REDIS_PASSWORD}` dans `environment:` de `app`. Après `up -d` : `db` et `app` recréés, `Exited (0)`, visite 3 (le volume a gardé le compteur).

## Erreurs de la notion 12
- `bash: cd: /exercices: No such file or directory` → un chemin qui commence par `/` est **absolu** (part de la racine du système). `cd exercices` = chemin **relatif** (part d'où je suis).
- `cp: cannot stat '../11-healthcheck-redis/Dockerfile'` → commande lancée depuis le mauvais dossier : `..` dépend du dossier courant. Réflexe : `pwd`.
- `❯ cp: command not found` → symbole de prompt `❯` collé avec la commande. Ne copier que la commande.
- `cat: dockerfile: No such file or directory` → Linux distingue majuscules et minuscules : `Dockerfile` ≠ `dockerfile`.
- `no configuration file provided: not found` → `docker compose` lancé dans un dossier sans `compose.yaml`.
- `no such service: app.` → le point final faisait partie du nom du service.
- Dans un vrai terminal bash, `!` en début de ligne **inverse le résultat** d'une commande : `! cd dossier && docker compose up -d` → le `cd` réussit, devient un « échec », et `&&` saute la suite.
- `docker compose ps -q` → n'affiche que les **ID** des conteneurs qui **tournent**.
- Nom du fichier : `compose.yaml` (pas `compose.yml` ni `yaml.compose`). Deux fichiers Compose dans le même dossier → Compose n'en lit qu'un.

## Notion 12 : validée ✅
- Variable d'environnement plutôt qu'en dur : on change la configuration sans modifier le code ni reconstruire l'image ; le code reste séparé des réglages propres à chaque environnement.
- `.env` n'empêche pas quelqu'un qui a accès à Docker ou à la machine de lire le secret ; il évite de l'écrire dans le code et de l'envoyer sur GitHub, **à condition** qu'il soit dans `.gitignore`.

## 13. Tags et Docker Hub (dossier `exercices/13-docker-hub/`)
- Problème : mes images n'existent que **sur mon PC**. Les autres machines (et Kubernetes, même minikube) doivent les **télécharger** depuis un **registre**.
- Analogie : mon PC = mon **cahier de recettes** perso ; **Docker Hub** = une **bibliothèque publique** de recettes. `push` = déposer, `pull` = emprunter. C'est de là que viennent `nginx`, `redis`, `python`…
- **Nom complet** d'une image : `registre/utilisateur/nom:tag` → `docker.io/hhabchane/bonjour:v2`.
  - `nginx` = `docker.io/library/nginx:latest` (`library` = le rayon des images **officielles**) ;
  - `apache/spark` = image d'un **compte** Docker Hub ; `gcr.io/k8s-minikube/kicbase` = image d'un **autre registre** (Google).
- **Tag = étiquette** collée sur une image. `docker build -t bonjour:v1 .` → seulement `v1` (pas de `latest` ajouté). `docker images bonjour` → filtre par nom.
- `docker tag <existante> <nouvelle>` → ajoute une étiquette : **même ID**, pas de place en plus (un seul pot de confiture, deux étiquettes).
- ⚠️ **Le piège de `latest`** : c'est juste l'étiquette **par défaut**, **pas** « la plus récente ». Elle ne bouge que si je la déplace.
  - Vu en vrai : `latest` collé sur v1 → build de `bonjour:v2` → `docker run bonjour` affiche **« version 1 »** alors que la v2 existait !
  - `docker tag bonjour:v2 bonjour:latest` → l'étiquette saute sur la v2 ; la v1 n'est **pas** supprimée (on peut revenir en arrière).
  - → Avec Kubernetes : **toujours une version précise** (`hhabchane/bonjour:v2`), jamais `latest`.
- Cache : changer une seule lettre de `app.py` → `COPY` refait (le cache compare le **contenu**).
- **Connexion** : `docker login` dans un **vrai terminal interactif** (« cannot perform an interactive login from a non-TTY device » sinon). Méthode simple : `docker login` sans `-u` → code + validation dans le navigateur → `Login Succeeded`. Sinon : jeton d'accès (Personal Access Token) plutôt que le mot de passe. Jamais de mot de passe/jeton écrit ailleurs que dans le terminal.
  - Warning « credentials are stored unencrypted in ~/.docker/config.json » → le badge de connexion est lisible par qui accède à ma session (même leçon que `.env`). `docker logout` pour se déconnecter.
  - `docker info | grep Username` → le compte connecté.
- **Publier** : étiqueter à mon nom, puis pousser :
  ```bash
  docker tag bonjour:v2 hhabchane/bonjour:v2
  docker push hhabchane/bonjour:v2
  ```
  - `Pushed` = couche envoyée ; `Mounted from library/redis` = Docker Hub avait déjà cette couche (base Debian partagée), simple lien ; le **digest** `sha256:d88686db…` = l'empreinte de l'image (même début que l'ID local).
  - Seule l'étiquette poussée est en ligne : sur Docker Hub, uniquement `v2` (ni `v1`, ni `latest`).
- **Preuve** : `docker rmi` de toutes les étiquettes → `Untagged` (étiquette décollée) puis `Deleted` (plus aucune étiquette → image effacée). Puis `docker run --rm hhabchane/bonjour:v2` → `Unable to find image locally` → `Pulling from hhabchane/bonjour` → seules les couches manquantes sont téléchargées (`Already exists` pour les autres) → « version 2 ». C'est ce que fera Kubernetes.
- Supprimer l'image en local **ne la supprime pas** de Docker Hub.

## Erreur : « push access denied, repository does not exist or may require authorization: ... insufficient_scope »
- **Cause** : `docker push bonjour:v2` → `The push refers to repository [docker.io/library/bonjour]` = le rayon des images **officielles**. Connecté, mais pas le droit d'y écrire.
- **Correction** : étiqueter à mon nom (`hhabchane/bonjour:v2`) et pousser celle-là.

## Erreurs de la notion 13
- `unauthorized: incorrect username or password` (au `docker login -u`) → mauvais mot de passe : compte créé via Google (pas de mot de passe), ou collage raté (dans le terminal Ubuntu : **Ctrl+Shift+V**, et rien ne s'affiche). Solution : `docker login` par le navigateur, ou un jeton.
- `cat` tout seul → attend du texte au clavier ; toujours lui donner un fichier.
- Fichier nommé `nano` créé par `cp ... nano` : le dernier mot de `cp` est le **nom de destination**. Corrigé avec `mv`/`rm`.
- `echo 'première ligne' > app.py` → il faut écrire le **code**, pas la description. `>` écrase, `>>` ajoute.
- Supprimer une ligne sans éditeur : `sed -i '/MOT/d' fichier`. `rm` supprime **définitivement** (pas de corbeille).

## Notion 13 : validée ✅
- `latest` est dangereux : avec `latest`, j'ai eu la version 1 alors que la v2 existait (l'étiquette n'avait pas bougé). → Toujours une version précise.
- `docker push bonjour:v2` refusé : sans nom d'utilisateur, c'est le rayon `library` des images officielles, je n'ai pas le droit. `hhabchane/bonjour:v2` est dans **mon** rayon.
