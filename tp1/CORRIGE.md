# TP 1 : Corrigé complet

> ⚠️ **Avant de lire** : les parties marquées **🔒 PAS ENCORE FAITE** (partie 1, étapes 3 à 6 ; partie 5 ; questions), essaie-les d'abord **seul**, puis compare. Lire une solution ≠ savoir la refaire.
>
> Tout se fait depuis `~/docker-learning/tp1`, sauf indication contraire.
> Les lignes `# ...` sont des commentaires : on ne les tape pas.

---

## Partie 0 : Préparer le terrain ✅ (fait)

```bash
docker ps -a                      # voir TOUS les conteneurs (même arrêtés)
docker stop site-v1               # l'arrêter s'il tourne (sinon, rien de grave)
docker rm site-v1                 # le supprimer
mkdir ~/docker-learning/tp1       # créer le dossier du TP
cd ~/docker-learning/tp1          # aller dedans
pwd                               # → /home/habchane/docker-learning/tp1
```
**Contrôle 0** : `docker ps -a` n'affiche que les titres des colonnes.

---

## Partie 1 : Images et conteneurs

### Étapes 1-2 ✅ (fait)
```bash
docker pull alpine                # télécharger sans lancer
docker images                     # alpine ≈ 13 MB, ubuntu ≈ 162 MB → alpine est ~12× plus petit
```

### Étapes 3 à 6 🔒 PAS ENCORE FAITE
```bash
docker run alpine echo Bonjour    # ×3 : affiche "Bonjour" puis le conteneur s'arrête
docker run alpine echo Bonjour    #   (après le nom de l'image = la commande à lancer dedans,
docker run alpine echo Bonjour    #    elle remplace la commande par défaut)

docker images                     # → 1 seule ligne alpine
docker ps -a                      # → 3 conteneurs alpine, COMMAND "echo Bonjour", STATUS Exited (0)

docker rmi alpine                 # → ERREUR attendue :
# conflict: unable to delete alpine:latest (must be forced) - container xxxx is using its referenced image

docker rm <id1> <id2> <id3>       # supprimer les 3 conteneurs (IDs lus dans docker ps -a)
docker rmi alpine                 # → Untagged / Deleted : maintenant ça marche
```
❓ **Réponse** : **1 image, 3 conteneurs**. Chaque `docker run` prépare un **nouveau plat** à partir de la **même recette**. L'image n'est téléchargée qu'une fois.

> 💡 Toi, tu as fait `docker run -it alpine sh` : très bien pour explorer. Mais `bash` n'existe pas dans alpine, c'est `sh`. Bien vu !

---

## Partie 2 : Conteneur nommé et persistant ✅ (fait, avec alpine au lieu d'ubuntu)

```bash
docker run --name carnet -it ubuntu bash   # 1. conteneur interactif nommé
```
Dans le conteneur (prompt `root@xxxx:/#`) :
```bash
mkdir /notes                               # 2. créer le dossier
echo 'TP1 commencé' > /notes/jour1.txt     #    créer le fichier
cat /notes/jour1.txt                       #    vérifier
exit                                       # 3. sortir → le conteneur s'arrête
```
Sur le PC :
```bash
docker ps -a                               # 4. carnet → STATUS Exited (0)
docker start -ai carnet                    # 5. rallumer ET entrer dedans
cat /notes/jour1.txt                       #    → TP1 commencé ✅
exit
docker run --name carnet -it ubuntu bash   # 6. → ERREUR : Conflict. The container name "/carnet" is already in use
docker run --rm -it ubuntu bash            # 7. nouveau conteneur, supprimé auto à l'arrêt
cat /notes/jour1.txt                       #    → No such file or directory
exit
```
❓ **Réponse** : à l'étape 5, c'est **le même** conteneur rallumé (`start`), donc il a gardé son fichier. À l'étape 7, c'est un **nouveau** conteneur (`run`), qui part de l'image **propre**. Le fichier n'a jamais été dans l'image, seulement dans `carnet`.

> 💡 Toi : tu as fait `docker rm carnet` puis `docker run --name carnet ...` : même résultat. Le `--rm` évite juste le ménage manuel.

---

## Partie 3 : Le portfolio en direct avec un volume ✅ (fait, port 8080 au lieu de 9000, logs non affichés)

```bash
mkdir portfolio
echo '<h1>Ton Nom</h1><p>Version volume</p>' > portfolio/index.html

docker run --name portfolio-live -d -p 9000:80 \
  -v "$PWD/portfolio:/usr/share/nginx/html:ro" nginx   # 2. arrière-plan + port + volume lecture seule

docker ps                                  # 3. STATUS Up … / PORTS 0.0.0.0:9000->80/tcp
curl http://localhost:9000                 # 4. affiche la page (et Firefox : http://localhost:9000)

echo '<h1>Ton Nom</h1><p>Version volume modifiée</p>' > portfolio/index.html
curl http://localhost:9000                 # 5. → nouvelle phrase, SANS redémarrer le conteneur

docker logs portfolio-live                 # 6. lignes "GET / HTTP/1.1" 200 = tes visites
```
❓ **Réponse** : `-p 9000:80` → **9000 = port de mon PC** (dehors), **80 = port dans le conteneur** (dedans, là où nginx écoute).

> ⚠️ Ne supprime pas `portfolio-live` ici : il sert dans la partie 4 (comparaison 9000 / 9001).

---

## Partie 4 : Le portfolio en image autonome ✅ (fait, ports 8080/8081 au lieu de 9001/9002)

`tp1/Dockerfile` :
```dockerfile
# Base : nginx
FROM nginx
# Photocopie du dossier portfolio dans le dossier web de nginx
COPY portfolio/ /usr/share/nginx/html/
```
```bash
docker build -t portfolio:v1 .             # 2. image avec le tag v1
docker run --name portfolio-v1 -d -p 9001:80 portfolio:v1   # 3.
curl http://localhost:9000                 # 4. volume
curl http://localhost:9001                 #    image v1 → même page pour l'instant

echo '<h1>Ton Nom</h1><p>Version 2</p>' > portfolio/index.html   # 5.
curl http://localhost:9000                 # 6. → Version 2 (VOLUME = tunnel en direct)
curl http://localhost:9001                 #    → ancienne version (COPY = photocopie figée)

docker build -t portfolio:v2 .             # 7. → CACHED [1/2] FROM nginx  /  [2/2] COPY refait
docker run --name portfolio-v2 -d -p 9002:80 portfolio:v2   # 8.
docker images                              # 9. → 2 lignes : portfolio:v1 et portfolio:v2
```
❓ **Réponses** :
- 9001 n'a pas changé : `portfolio:v1` contient une **photocopie** faite au moment du `build`. Modifier le fichier sur le PC ne touche pas l'image. Il faut **rebuild** (→ v2).
- 3 nginx sur le port 80 : chaque conteneur a son **propre réseau isolé**, donc son propre port 80. Seuls les ports **du PC** (9000, 9001, 9002) doivent être **différents**.

> ⚠️ Le piège que tu as rencontré : `curl -s` juste après `docker build` → réponse **vide**. `build` crée une image mais **ne lance rien**, et `-s` cache l'erreur « Connection refused ».

---

## Partie 5 : Une appli Python 🔒 PAS ENCORE FAITE (tu as refait l'appli de la notion 8)

```bash
mkdir appli
cd appli
nano app.py                       # coller le code Python du sujet, Ctrl+O, Entrée, Ctrl+X
echo '1.0' > version.txt
nano Dockerfile
```
`tp1/appli/Dockerfile` :
```dockerfile
FROM python:3.13-slim
WORKDIR /projet
COPY app.py version.txt ./
RUN date > build-info.txt
CMD ["python", "app.py"]
```
> 💡 `COPY` avec **plusieurs fichiers** : la destination doit être un **dossier** qui **finit par `/`** → `./` (= le WORKDIR `/projet`).

```bash
docker build -t appli:1.0 .       # 4.
docker run --rm appli:1.0         # 5. 1er lancement
docker run --rm appli:1.0         #    1 minute plus tard

echo '2.0' > version.txt          # 6.
docker build -t appli:2.0 .       #    → COPY refait (version.txt a changé) → RUN refait aussi
docker run --rm appli:1.0         #    → Version : 1.0
docker run --rm appli:2.0         #    → Version : 2.0
cd ..                             # retour dans tp1
```
❓ **Réponses** :
- Entre les 2 lancements de l'étape 5 : **« Lancée le » change** (calculée par `CMD` à chaque `run`), **« Construite le » reste fixe** (écrite par `RUN`, une fois, au `build`).
- « Dossier » vaut **`/projet`** grâce à **`WORKDIR /projet`** : c'est le dossier de travail dans lequel `CMD` lance le programme.
- Bonus : `appli:1.0` et `appli:2.0` coexistent. Les **tags** permettent de garder plusieurs versions et de revenir en arrière.

---

## Partie 6 : Grand ménage final 🟡 (fait, mais il reste alpine)

```bash
docker stop portfolio-live portfolio-v1 portfolio-v2               # arrêter ceux qui tournent
docker rm portfolio-live portfolio-v1 portfolio-v2 carnet          # tout supprimer en 1 commande
docker rmi portfolio:v1 portfolio:v2 appli:1.0 appli:2.0           # supprimer les images du TP
docker rmi alpine                                                  # (si pas déjà fait en partie 1)

docker ps -a                      # → vide
docker images                     # → plus d'images du TP ; spark, cuda… intactes ⚠️
ls portfolio                      # → index.html toujours là (il est sur le PC, pas dans un conteneur)
```

---

## Questions finales 🔒 (essaie d'abord sans regarder !)

1. **Image vs conteneur** : l'image est la **recette**, figée et en lecture seule. Le conteneur est le **plat** préparé à partir d'elle : il tourne, s'arrête, a ses propres fichiers. 1 image → plusieurs conteneurs.
2. **`run` vs `start`** : `run` crée un **nouveau** conteneur (nouvel ID, part de l'image propre). `start` **rallume** un conteneur **existant**, avec ses fichiers.
3. **`ps` vs `ps -a`** : `ps` montre les conteneurs **qui tournent**, `ps -a` montre **tous** les conteneurs, même arrêtés.
4. **COPY vs volume** : COPY = **photocopie figée** dans l'image au build, donc image **autonome**, idéale pour **livrer/déployer**. Volume = **tunnel en direct** vers le PC, idéal pour **développer** (on voit les changements tout de suite) ou **garder des données** après le `rm`.
5. **RUN vs CMD** : `RUN` s'exécute **au build, une fois**, et son résultat est figé dans l'image. `CMD` s'exécute **à chaque démarrage** d'un conteneur.
6. **Le `.` de `docker build`** : le **contexte de build**, c'est-à-dire le dossier où Docker trouve le `Dockerfile` et les fichiers à `COPY`. Sans lui : `requires 1 argument`.
7. **ubuntu s'arrête, nginx non** : un conteneur vit **tant que son programme principal tourne**. `bash` se termine avec `exit`, alors que nginx est un serveur qui attend des visiteurs **indéfiniment**.
8. **« name already in use » mais `docker ps` vide** : le conteneur existe mais est **arrêté**, et `ps` ne le montre pas. → `docker ps -a` pour le voir, puis `docker rm <nom>` (ou `docker start` si on veut le réutiliser, ou choisir un autre nom).
