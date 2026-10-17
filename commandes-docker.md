# Aide-mémoire : les commandes Docker

> Toutes les commandes vues pendant le cours, avec leur rôle.
> `<...>` = à remplacer (sans les chevrons). Exemple : `docker rm <conteneur>` → `docker rm mon-site`.
> **Analogie** : image = **recette** 📄, conteneur = **plat** 🍽️, démon Docker = **cuisinier** 👨‍🍳.

---

## 1. Les images (les recettes)

```bash
docker images                     # Liste les images présentes sur ma machine
docker image ls                   # Même chose (forme longue)

docker pull <image>               # Télécharge une image depuis Docker Hub, SANS lancer de conteneur
docker pull ubuntu                #   → sans tag, Docker prend "ubuntu:latest" (la plus récente)
docker pull <image>:<tag>         #   → télécharge une version précise (ex. python:3.13-slim)

docker rmi <image>                # Supprime une image (rmi = remove image)
                                  #   ⚠️ refusé si un conteneur (même arrêté) l'utilise → supprimer le conteneur d'abord
docker rmi <image1> <image2>      # Supprime plusieurs images d'un coup
docker rmi -f <image>             # Force la suppression (⚠️ à éviter quand on débute)
```

**Nom d'une image** : `nom:tag`, par exemple `nginx:latest` ou `python:3.13-slim`. Le **tag** = la version. S'il est absent, Docker utilise `latest`.
**Nom complet** : `registre/utilisateur/nom:tag` → `nginx` = `docker.io/library/nginx:latest` (`library` = images officielles).

### Tags et Docker Hub (le registre = la bibliothèque publique de recettes)
```bash
docker images <nom>                       # N'affiche que les images de ce nom (ex. docker images bonjour)
docker tag <existante> <nouvelle>         # Colle une ÉTIQUETTE de plus sur une image (même ID, pas de place en plus)
docker tag bonjour:v2 bonjour:latest      #   → déplace "latest" sur la v2 (la v1 n'est pas supprimée)
docker tag bonjour:v2 hhabchane/bonjour:v2  # → étiquette à MON nom, obligatoire pour publier

docker login                              # Connexion à Docker Hub (vrai terminal interactif ; code + navigateur)
docker login -u <utilisateur>             #   → variante : coller un jeton d'accès (Ctrl+Shift+V, rien ne s'affiche)
docker logout                             # Déconnexion
docker push <utilisateur>/<nom>:<tag>     # ENVOIE l'image sur Docker Hub (seulement ce tag-là)
docker rmi <tag1> <tag2>                  # Untagged = étiquette décollée ; Deleted = plus aucune étiquette → image effacée
```
⚠️ **`latest` ≠ la plus récente** : c'est juste l'étiquette par défaut, elle ne bouge que si on la déplace. Toujours déployer une **version précise**.
⚠️ `docker push bonjour:v2` (sans nom d'utilisateur) → `push access denied ... insufficient_scope` : c'est le rayon `library` des images officielles.

---

## 2. Créer et lancer un conteneur : `docker run`

`docker run` = **préparer un NOUVEAU plat** à partir d'une recette. Si l'image manque, Docker la télécharge tout seul.

```bash
docker run <image>                     # Crée + lance un nouveau conteneur (ex. docker run hello-world)
docker run <image> <commande>          # Lance le conteneur avec une autre commande que celle par défaut
```

### Les options de `docker run`
| Option | Rôle | Exemple |
|---|---|---|
| `--name <nom>` | Donne un **nom** au conteneur (sinon nom au hasard, ex. `happy_rosalind`). Le nom doit être **unique**. | `--name mon-site` |
| `-i` | **Interactif** : le conteneur écoute ce que je tape | |
| `-t` | Donne un **terminal** | |
| `-it` | Les deux ensemble → **entrer dans le conteneur** (⚠️ dans un vrai terminal interactif) | `docker run -it ubuntu bash` |
| `-d` | **Détaché** : tourne en arrière-plan, me rend la main (affiche juste l'ID) | `-d` |
| `-p <PC>:<conteneur>` | Relie un **port** de mon PC à un port du conteneur. **DEHORS : DEDANS** | `-p 8080:80` |
| `-v <dossier PC>:<dossier conteneur>` | **Volume** : partage un dossier PC ↔ conteneur, en direct. **DEHORS : DEDANS**. Chemin complet obligatoire. | `-v "$PWD/site:/usr/share/nginx/html"` |
| `:ro` (à la fin de `-v`) | Volume en **lecture seule** pour le conteneur | `-v "$PWD/site:/usr/share/nginx/html:ro"` |
| `--rm` | **Supprime automatiquement** le conteneur quand il s'arrête | `docker run --rm mon-app` |
| `-e NOM=valeur` | **Variable d'environnement** donnée au démarrage (réglage du four, pas dans la recette) | `-e PRENOM=Hicham` |

### Exemples complets vus en cours
```bash
docker run hello-world                                        # Test : affiche un message puis s'arrête
docker run -it ubuntu bash                                    # Entre dans un mini-Ubuntu (exit pour sortir)
docker run --name mon-ubuntu -it ubuntu bash                  # Pareil, avec un nom choisi
docker run --name mon-site -d -p 8080:80 nginx                # Serveur web en arrière-plan → http://localhost:8080
docker run --name mon-site -d -p 8080:80 \
  -v "$PWD/site:/usr/share/nginx/html:ro" nginx               # Serveur web qui sert MON dossier site/ (en direct)
docker run --name site-v1 -d -p 8080:80 mon-site-image        # Lance MA propre image
docker run --rm mon-app                                       # Lance mon appli, puis supprime le conteneur à l'arrêt
docker run --rm -e PRENOM=Hicham alpine env                   # Affiche les variables d'environnement (PRENOM en fait partie)
docker run --rm hhabchane/bonjour:v2                          # Image absente → téléchargée depuis Docker Hub, puis lancée
```

---

## 3. Voir et gérer les conteneurs (les plats)

```bash
docker ps                         # Liste les conteneurs qui TOURNENT (STATUS: Up)
docker ps -a                      # Liste TOUS les conteneurs, même arrêtés (STATUS: Exited)
                                  #   → réflexe en cas d'erreur « name already in use »

docker start <conteneur>          # RALLUME un conteneur arrêté (en arrière-plan)
docker start -ai <conteneur>      # Rallume ET entre dedans (-a = attach : affiche sa sortie, -i = interactif)
docker stop <conteneur>           # ARRÊTE un conteneur qui tourne (il existe toujours)

docker rm <conteneur>             # SUPPRIME un conteneur arrêté (avec ses fichiers internes !)
docker rm <c1> <c2> <c3>          # Supprime plusieurs conteneurs d'un coup

docker logs <conteneur>           # Affiche le journal du conteneur (démarrage, visites, erreurs…)
docker logs --tail 5 <conteneur>  # Seulement les 5 dernières lignes (la « queue » du journal)

docker exec <conteneur> <cmd>     # Lance une commande DANS un conteneur qui tourne (passer la tête en cuisine)
docker inspect <conteneur>        # Fiche détaillée (config, variables d'env — mots de passe visibles !)
docker info                       # Infos sur Docker ; docker info | grep Username → compte Docker Hub connecté

docker volume ls                  # Liste les volumes (nom réel d'un volume Compose : <projet>_<volume>)
```

`<conteneur>` = son **nom** (`mon-site`) **ou** son **ID**. Les premiers caractères de l'ID suffisent (`docker rm 825`).

### `run` ou `start` ?
- `docker run` → **nouveau** conteneur (nouvel ID, part de l'image propre)
- `docker start` → **le même** conteneur rallumé (garde ses fichiers)

### Lire `docker ps -a`
| Colonne | Signification |
|---|---|
| `CONTAINER ID` | Identifiant unique |
| `IMAGE` | La recette utilisée |
| `COMMAND` | Le programme principal lancé dedans |
| `STATUS` | `Up ...` = tourne · `Exited (0)` = arrêté normalement (0 = OK, autre chiffre = erreur) · `Created` = créé mais jamais démarré · `(healthy)` / `(unhealthy)` / `(health: starting)` = résultat du healthcheck |
| `PORTS` | Ex. `0.0.0.0:8080->80/tcp` = port 8080 du PC → port 80 du conteneur · `6379/tcp` **sans flèche** = port seulement interne |
| `NAMES` | Le nom du conteneur |

---

## 4. Construire sa propre image : Dockerfile + `docker build`

### Le Dockerfile (fichier nommé exactement `Dockerfile`)
```dockerfile
FROM <image>                 # Image de DÉPART (toujours la 1re ligne). Ex. FROM nginx
WORKDIR <dossier>            # Dossier de travail dans l'image (créé si besoin), comme un cd. Ex. WORKDIR /app
COPY <source PC> <dest>      # PHOTOCOPIE des fichiers du PC dans l'image (figée au build). Ex. COPY app.py .
RUN <commande>               # Exécutée UNE FOIS, pendant le BUILD → résultat figé dans l'image
CMD ["prog", "arg"]          # Exécutée à CHAQUE démarrage de conteneur (RUN). Guillemets doubles + crochets
```

### Construire l'image
```bash
docker build -t <nom> .           # Construit une image à partir du Dockerfile du dossier courant
docker build -t <nom>:<tag> .     # Pareil, avec une version (ex. portfolio:v1)
                                  #   -t  = nom (tag) de l'image
                                  #   .   = CONTEXTE de build : le dossier avec le Dockerfile + les fichiers à COPY
                                  #   ⚠️ oublier le . → erreur « requires 1 argument »
```

### À retenir
- **Cache** : au rebuild, les étapes inchangées affichent `CACHED`. Une étape modifiée est refaite, **et toutes celles d'après aussi**.
- **Mettre à jour une appli « image »** : modifier les fichiers → `docker build` → `docker stop` + `docker rm` l'ancien conteneur → `docker run` un nouveau.
- **COPY** = photocopie figée (image autonome) · **volume `-v`** = tunnel en direct vers le PC.
- **Ordre pour le cache** : `RUN pip install ...` (change rarement, long) **avant** `COPY app.py .` (change souvent).
  ```dockerfile
  FROM python:3.13-slim
  WORKDIR /app
  RUN pip install --no-cache-dir redis flask   # plusieurs bibliothèques séparées par un espace
  COPY app.py .
  CMD ["python", "app.py"]
  ```

---

## 5. Docker Compose : plusieurs services en une commande

Toutes ces commandes se lancent **dans le dossier qui contient `compose.yaml`** (sinon : `no configuration file provided`).
Nom du projet = nom du **dossier**. Conteneurs : `<projet>-<service>-1` · volumes : `<projet>_<volume>` · images construites : `<projet>-<service>`.

```bash
docker compose up -d              # Crée et lance tous les services en arrière-plan (recrée ceux dont la config a changé)
docker compose up -d --build      # Pareil, en RECONSTRUISANT les images (après une modif du code)
docker compose ps                 # État des services qui tournent
docker compose ps -a              # État de TOUS les services, même arrêtés
docker compose logs <service>     # Journal d'un service (ex. docker compose logs app)
docker compose logs --tail 5 web  # Les 5 dernières lignes seulement
docker compose start <service>    # Rallume un service arrêté (le même conteneur, ses logs s'accumulent)
docker compose stop <service>     # Arrête un service sans le supprimer
docker compose restart <service>  # Redémarre un service
docker compose exec <service> <cmd>  # Commande DANS un service qui tourne (ex. exec db redis-cli ping)
docker compose config             # Affiche le fichier après remplacement des ${...} (⚠️ mots de passe en clair)
docker compose config -q          # Vérifie seulement que le fichier est valide (rien affiché = OK)
docker compose down               # Arrête et SUPPRIME conteneurs + réseau (les volumes sont GARDÉS)
docker compose down -v            # Pareil + SUPPRIME LES VOLUMES ⚠️ (données perdues)
```

### Modèle de `compose.yaml` (tout ce qu'on a vu)
```yaml
services:                                          # la liste des services (un service = un conteneur à lancer)
  db:                                              # nom du service = son nom sur le réseau (DNS interne : « db »)
    image: redis                                   # image toute faite (téléchargée depuis Docker Hub)
    command: ["redis-server", "--requirepass", "${REDIS_PASSWORD}"]   # remplace la commande de l'image
    volumes:                                       # les volumes branchés sur ce service
      - donnees:/data                              # volume NOMMÉ (pas de ./) → casier géré par Docker
    healthcheck:                                   # test de santé, lancé régulièrement DANS le conteneur
      test: ["CMD-SHELL", "redis-cli -a ${REDIS_PASSWORD} ping | grep PONG"]   # CMD-SHELL pour le tuyau |
      interval: 2s                                 # un test toutes les 2 s
      timeout: 2s                                  # test trop long = échec
      retries: 5                                   # 5 échecs de suite = unhealthy

  web:                                             # 2e service : mon appli
    build: .                                       # construit avec le Dockerfile du dossier
    image: hhabchane/compteur-web:v1               # + image: → nom donné à l'image construite
    ports:                                         # ports publiés vers mon PC (seulement pour ce qu'on visite depuis le PC)
      - "8080:5000"                                # DEHORS (PC) : DEDANS (port où l'appli écoute)
    volumes:                                       # (exemple) un dossier de mon PC partagé avec le conteneur
      - ./entree:/entree:ro                        # BIND MOUNT (avec ./) → dossier de mon PC, lecture seule
    environment:                                   # variables d'environnement (réglages donnés au démarrage)
      REDIS_HOST: db                               # un service s'appelle par son NOM (DNS interne)
      REDIS_PASSWORD: ${REDIS_PASSWORD}            # valeur lue dans le fichier .env
      NOM_APP: Compteur TP3                        # valeur écrite directement (pas secrète)
    command: ["sh", "-c", "sleep 2 && wget -qO- http://web"]   # (exemple) remplace le CMD de l'image
    depends_on:                                    # ordre de démarrage : ce service attend…
      db:                                          # … le service db…
        condition: service_healthy                 # … et qu'il soit healthy (pas seulement démarré)
        # condition: service_completed_successfully → attend que le service ait fini avec Exited (0)
        # (depends_on simple, sans condition → attend seulement le DÉMARRAGE)

volumes:                                           # déclaration des volumes NOMMÉS du projet (obligatoire)
  donnees:                                         # nom réel créé par Docker : <projet>_donnees
```
- **`.env`** (à côté de `compose.yaml`, lu automatiquement) : `REDIS_PASSWORD=motdepasse123` (pas d'espaces autour du `=`). **Jamais sur GitHub** (`.gitignore`) → versionner un `.env.example` avec une valeur bidon.
- Un healthcheck ne regarde que le **code de sortie** : `redis-cli ping` répond `NOAUTH` avec le code 0 → ajouter `| grep PONG`.
- Changer un **réglage** (`environment:`) → `up -d` suffit (conteneur recréé). Changer le **code** → `up -d --build`.
- `Up` ≠ « ça marche » : un conteneur peut tourner pendant que l'appli renvoie une erreur 500.

---

## 6. À l'intérieur d'un conteneur (après `docker run -it ...`)

```bash
exit                              # Sortir → le programme principal (bash) s'arrête → le conteneur s'arrête
```
Le prompt `root@ebb9bdcda9a1:/#` signifie : `root` = admin dans le conteneur, `ebb9bdcda9a1` = ID du conteneur, `/` = racine, `#` = prompt de root.

---

## 7. Commandes Linux utiles autour de Docker

```bash
pwd                               # Affiche le dossier où je suis
ls                                # Liste les fichiers du dossier
cd <dossier>                      # Va dans un dossier (cd ~/docker-learning)
ls -a                             # Liste AUSSI les fichiers cachés (ceux qui commencent par un point : .env, .gitignore)
cd <dossier>                      #   cd exercices = chemin RELATIF (part d'où je suis)
cd /chemin                        #   cd /exercices = chemin ABSOLU (part de la racine du système) ; .. = dossier parent
mkdir -p <dossier>                # Crée un dossier (et ses parents), sans erreur s'il existe déjà
cat <fichier>                     # Affiche le contenu d'un fichier (cat seul, sans fichier → attend le clavier)
cp <source> <destination>         # COPIE un fichier (ex. cp ../12-variables-env/Dockerfile .) ; . = ici
mv <source> <destination>         # DÉPLACE ou RENOMME un fichier (ex. mv nano Dockerfile)
rm <fichier>                      # SUPPRIME un fichier ⚠️ définitivement (pas de corbeille)
echo 'texte' > <fichier>          # ÉCRASE (ou crée) le fichier avec ce texte
echo 'texte' >> <fichier>         # AJOUTE une ligne à la fin du fichier
printf '%s\n' 'l1' 'l2' > <fichier>  # Écrit plusieurs lignes d'un coup
cat > <fichier> << 'EOF'          # « heredoc » : écrit tout ce qui suit jusqu'à la ligne EOF
sed -i 's/ANCIEN/NOUVEAU/' <fichier>  # RECHERCHER / REMPLACER dans un fichier (sans éditeur)
sed -i '/MOT/d' <fichier>         # SUPPRIME les lignes qui contiennent MOT
grep <mot> <fichier>              # Affiche les lignes qui contiennent <mot> ; grep -i = sans tenir compte des majuscules
<commande> | grep <mot>           # Tuyau | : envoie la sortie d'une commande à une autre (ex. docker info | grep Username)
nano <fichier>                    # Éditeur : Ctrl+O, Entrée (sauver) → Ctrl+X (quitter) ; Ctrl+K = couper une ligne
curl http://localhost:8080        # Affiche une page web dans le terminal
curl -s http://localhost:8080     # Pareil, sans la barre de progression (silencieux)
$PWD   ou   $(pwd)                # Remplacé par le chemin complet du dossier courant (utile pour -v)
echo $?                           # Code de sortie de la DERNIÈRE commande (0 = réussite)
cmd1 ; cmd2                       # Lance cmd1 puis cmd2, quoi qu'il arrive
cmd1 && cmd2                      # Lance cmd2 SEULEMENT si cmd1 a réussi
```
- Linux distingue **majuscules et minuscules** : `Dockerfile` ≠ `dockerfile`.
- Coller dans le terminal Ubuntu : **Ctrl+Shift+V** (Ctrl+V ne marche pas).
- Ne jamais copier le prompt ni ses symboles (`$`, `❯`, `habchane@...`) avec la commande.
- Dans un vrai terminal bash, `!` en début de ligne **inverse le résultat** d'une commande : ne pas le mettre devant une commande.

### Git (vérifier ce qui ira sur GitHub)
```bash
git status --short                          # Fichiers modifiés (M) et nouveaux (??)
git status --short --untracked-files=all    # Pareil, en détaillant chaque nouveau fichier
git status --short --ignored -- .env        # !! = fichier ignoré par Git (ne partira pas sur GitHub)
git check-ignore -v .env                    # Quelle règle de .gitignore ignore ce fichier (ex. .gitignore:9:*.env)
```

### Permissions Docker
```bash
groups                            # Mes groupes dans CE terminal (docker doit y être)
groups $USER                      # Les groupes enregistrés pour mon compte
sudo usermod -aG docker $USER     # M'ajoute au groupe docker (une seule fois)
                                  #   → puis se DÉCONNECTER/RECONNECTER d'Ubuntu
newgrp docker                     # Dépannage temporaire (valable dans ce terminal seulement)
```

---

## 8. Erreurs fréquentes → solution rapide

| Message | Cause | Solution |
|---|---|---|
| `permission denied ... docker.sock` | Pas dans le groupe `docker` | `sudo usermod -aG docker $USER` + reconnexion |
| `conflict: unable to delete ... (must be forced)` | Un conteneur utilise l'image | `docker rm` le conteneur, puis `docker rmi` |
| `Conflict. The container name "/x" is already in use` | Un conteneur (même arrêté) a déjà ce nom | `docker ps -a` → `docker rm x`, ou autre nom |
| `No such image` | L'image n'existe pas (déjà supprimée, faute de frappe) | Vérifier avec `docker images` |
| `requires 1 argument ... PATH` | Oubli du `.` dans `docker build` | `docker build -t nom .` |
| `Unable to connect` (navigateur) | Aucun conteneur ne tourne sur ce port | `docker ps` → relancer le conteneur |
| `No such file or directory` (sur une URL ou un prompt) | Collé une URL / un prompt dans le terminal | Taper seulement la commande ; URL → navigateur ou `curl` |
| `No such file or directory` (sur un fichier) | Fichier pas encore créé, ou mauvais dossier, ou mauvaise casse | `pwd`, `ls -a` ; créer le fichier **avant** de le lire |
| `Standard input is not a terminal` / `non-TTY device` | Commande interactive (`nano`, `-it`, `docker login`) lancée hors d'un vrai terminal | La lancer dans un vrai terminal interactif |
| `no configuration file provided: not found` | `docker compose` lancé dans un dossier sans `compose.yaml` | `cd` dans le dossier du projet |
| `no such service: app.` | Nom de service mal écrit (ici avec un point) | Vérifier le nom dans `compose.yaml` |
| `Could not resolve host: web` (depuis le PC) | Les noms de services n'existent que **dans** le réseau Compose | Depuis le PC : `localhost:<port publié>` |
| `service "x" didn't complete successfully: exit 1` | Le service dont on attend la fin a planté | `docker compose logs x` → lire le traceback de bas en haut |
| `dependency failed to start: container ... is unhealthy` | Le healthcheck échoue (5 fois de suite) | Corriger le `test:` ; `docker compose ps -a` |
| `redis.exceptions.AuthenticationError` | L'appli n'a pas le mot de passe de Redis | Ajouter `REDIS_PASSWORD: ${REDIS_PASSWORD}` dans `environment:` |
| `ConnectionError ... Temporary failure in name resolution` | Le service appelé (`db`) est arrêté → absent du DNS interne | `docker compose start db` |
| `500 Internal Server Error` | L'appli web tourne mais plante en traitant la demande | `docker compose logs --tail 5 web` |
| `unauthorized: incorrect username or password` | Mauvais mot de passe Docker Hub (ou compte Google, ou collage raté) | `docker login` (par le navigateur) ou jeton d'accès |
| `push access denied ... insufficient_scope` | Push sans nom d'utilisateur → rayon `library` (images officielles) | `docker tag x hhabchane/x:v1` puis push de celle-là |
| `ErrImagePull` / `ImagePullBackOff` (Kubernetes) | Image introuvable dans le registre (nom incomplet, tag inexistant) | Nom complet : `hhabchane/compteur-web:v2` |
