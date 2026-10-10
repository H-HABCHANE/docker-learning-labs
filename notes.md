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
12. **Réflexes terminal** : ne jamais coller le prompt ni un message d'erreur ; une URL va dans le navigateur ou après `curl` ; nano = **Ctrl+O, Entrée, Ctrl+X** ; `-it` et nano → vrai terminal, pas le `!` de Claude Code.
13. **permission denied … docker.sock** → `sudo usermod -aG docker $USER` puis **se déconnecter/reconnecter**.

## ⏸️ Où j'en suis (pause du 10/10/2026)
- Notions 1 à 8 validées. **En cours : TP 1 de révision (`tp1/SUJET.md`)**, puis **notion 9. Docker Compose** (plusieurs conteneurs, un seul fichier, `docker compose up`).
- Reprendre : `cd ~/docker-learning` puis `claude -c`.
- Aide-mémoire de toutes les commandes : `commandes-docker.md`.
- Corrigé du TP 1 : `tp1/CORRIGE.md`.
- ⚠️ `site-v1` tourne peut-être encore (port 8080) → `docker stop site-v1`.
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
- ⚠️ Les commandes `-it` doivent être tapées dans le vrai terminal, pas avec `!` dans Claude Code.
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
- Attention : le `!` de Claude Code et mon terminal Ubuntu peuvent être dans des dossiers différents → vérifier avec `pwd`.
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
