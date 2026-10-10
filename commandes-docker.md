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
| `-it` | Les deux ensemble → **entrer dans le conteneur** (⚠️ vrai terminal, pas le `!` de Claude Code) | `docker run -it ubuntu bash` |
| `-d` | **Détaché** : tourne en arrière-plan, me rend la main (affiche juste l'ID) | `-d` |
| `-p <PC>:<conteneur>` | Relie un **port** de mon PC à un port du conteneur. **DEHORS : DEDANS** | `-p 8080:80` |
| `-v <dossier PC>:<dossier conteneur>` | **Volume** : partage un dossier PC ↔ conteneur, en direct. **DEHORS : DEDANS**. Chemin complet obligatoire. | `-v "$PWD/site:/usr/share/nginx/html"` |
| `:ro` (à la fin de `-v`) | Volume en **lecture seule** pour le conteneur | `-v "$PWD/site:/usr/share/nginx/html:ro"` |
| `--rm` | **Supprime automatiquement** le conteneur quand il s'arrête | `docker run --rm mon-app` |

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
| `STATUS` | `Up ...` = tourne · `Exited (0)` = arrêté normalement (0 = OK, autre chiffre = erreur) |
| `PORTS` | Ex. `0.0.0.0:8080->80/tcp` = port 8080 du PC → port 80 du conteneur |
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

---

## 5. À l'intérieur d'un conteneur (après `docker run -it ...`)

```bash
exit                              # Sortir → le programme principal (bash) s'arrête → le conteneur s'arrête
```
Le prompt `root@ebb9bdcda9a1:/#` signifie : `root` = admin dans le conteneur, `ebb9bdcda9a1` = ID du conteneur, `/` = racine, `#` = prompt de root.

---

## 6. Commandes Linux utiles autour de Docker

```bash
pwd                               # Affiche le dossier où je suis
ls                                # Liste les fichiers du dossier
cd <dossier>                      # Va dans un dossier (cd ~/docker-learning)
mkdir <dossier>                   # Crée un dossier
cat <fichier>                     # Affiche le contenu d'un fichier
echo 'texte' > <fichier>          # ÉCRASE (ou crée) le fichier avec ce texte
echo 'texte' >> <fichier>         # AJOUTE une ligne à la fin du fichier
nano <fichier>                    # Éditeur de texte : Ctrl+O, Entrée (sauver) → Ctrl+X (quitter)
curl http://localhost:8080        # Affiche une page web dans le terminal
curl -s http://localhost:8080     # Pareil, sans la barre de progression (silencieux)
$PWD   ou   $(pwd)                # Remplacé par le chemin complet du dossier courant (utile pour -v)
```

### Permissions Docker
```bash
groups                            # Mes groupes dans CE terminal (docker doit y être)
groups $USER                      # Les groupes enregistrés pour mon compte
sudo usermod -aG docker $USER     # M'ajoute au groupe docker (une seule fois)
                                  #   → puis se DÉCONNECTER/RECONNECTER d'Ubuntu
newgrp docker                     # Dépannage temporaire (valable dans ce terminal seulement)
```

### Dans Claude Code
```
! <commande>                      # Exécute la commande ici (sauf -it et nano → vrai terminal)
claude -c                         # Reprendre la dernière conversation (depuis ~/docker-learning)
```

---

## 7. Erreurs fréquentes → solution rapide

| Message | Cause | Solution |
|---|---|---|
| `permission denied ... docker.sock` | Pas dans le groupe `docker` | `sudo usermod -aG docker $USER` + reconnexion |
| `conflict: unable to delete ... (must be forced)` | Un conteneur utilise l'image | `docker rm` le conteneur, puis `docker rmi` |
| `Conflict. The container name "/x" is already in use` | Un conteneur (même arrêté) a déjà ce nom | `docker ps -a` → `docker rm x`, ou autre nom |
| `No such image` | L'image n'existe pas (déjà supprimée, faute de frappe) | Vérifier avec `docker images` |
| `requires 1 argument ... PATH` | Oubli du `.` dans `docker build` | `docker build -t nom .` |
| `Unable to connect` (navigateur) | Aucun conteneur ne tourne sur ce port | `docker ps` → relancer le conteneur |
| `No such file or directory` (sur une URL ou un prompt) | Collé une URL / un prompt dans le terminal | Taper seulement la commande ; URL → navigateur ou `curl` |
