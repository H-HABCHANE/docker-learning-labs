# TP 3 : Corrigé et leçons

Les fichiers de ce dossier sont **mon travail** (état final : version 2, `NOM_APP` = `Super compteur`).
Le vrai `.env` n'est pas versionné ; copier `.env.example` en `.env` et choisir un mot de passe avant de lancer.

## Fichiers attendus

### `Dockerfile`
```dockerfile
FROM python:3.13-slim
WORKDIR /app
RUN pip install --no-cache-dir redis flask   # avant COPY : réutilisé en cache quand seul app.py change
COPY app.py .
CMD ["python", "app.py"]
```
- `flask` installe aussi ses **dépendances** (`werkzeug`, `jinja2`, `click`…) : 8 bibliothèques au total.
- `--no-cache-dir` : pip ne garde pas de copie des fichiers téléchargés dans l'image (image plus légère). Rien à voir avec le cache de **build** de Docker.
- Le `WARNING: Running pip as the 'root' user` n'est pas grave dans un conteneur jetable.

### `.env` (jamais sur GitHub) et `.env.example` (versionné)
```
REDIS_PASSWORD=change-moi
```
Preuve : `git status --short --ignored -- .env .env.example` → `?? .env.example` et `!! .env`.
(Le `.gitignore` de la racine, règle `*.env`, suffit déjà ; celui de `tp3/` est une sécurité en plus.)

### `compose.yaml`
```yaml
services:
  db:
    image: redis
    command: ["redis-server", "--requirepass", "${REDIS_PASSWORD}"]
    volumes:
      - donnees:/data
    healthcheck:
      test: ["CMD-SHELL", "redis-cli -a ${REDIS_PASSWORD} ping | grep PONG"]
      interval: 2s
      timeout: 2s
      retries: 5

  web:
    build: .
    image: hhabchane/compteur-web:v1      # build: + image: → l'image construite porte ce nom
    ports:
      - "8080:5000"                       # DEHORS (PC) : DEDANS (Flask écoute sur 5000)
    environment:
      REDIS_HOST: db
      REDIS_PASSWORD: ${REDIS_PASSWORD}
      NOM_APP: Compteur TP3
    depends_on:
      db:
        condition: service_healthy

volumes:
  donnees:
```

## Commandes de chaque partie
| Partie | Commandes |
|---|---|
| 0 | `docker ps -a` ; `docker login` (ou `docker info \| grep Username`) |
| 2 | `echo 'REDIS_PASSWORD=change-moi' > .env.example` ; `git status --short --ignored -- .env .env.example` |
| 4 | `docker compose up -d --build` ; `docker compose ps -a` ; `curl -s http://localhost:8080` ; `docker images hhabchane/compteur-web` |
| 5 | `sed -i 's/Compteur TP3/Super compteur/' compose.yaml` ; `docker compose up -d` |
| 6 | `sed -i 's/"1"/"2"/' app.py` ; `sed -i 's/compteur-web:v1/compteur-web:v2/' compose.yaml` ; `docker compose up -d --build` |
| 7 | `docker push hhabchane/compteur-web:v2` ; `docker push hhabchane/compteur-web:v1` |
| 8 | `docker compose stop db` ; `curl …` ; `docker compose ps -a` ; `docker compose logs --tail 5 web` ; `docker compose start db` |
| 9 | `docker compose down -v` ; `docker rmi hhabchane/compteur-web:v1 hhabchane/compteur-web:v2` |

## Résultats observés
- **Partie 4** : `web` **Up** (un serveur web ne s'arrête pas, contrairement aux scripts des exercices 11-12). `db` healthy. Visites 1, 2, 3… Image `EXTRA = U` = utilisée par un conteneur.
- **Partie 5** : `db` `Running` (pas touché), `web` `Recreate`, **aucun `Building`**. Le nom change, la version reste 1 (elle est dans le code, donc dans l'image).
- **Partie 6** : `RUN pip install` **`CACHED`**, seul `COPY app.py` refait. v1 et v2 coexistent (deux ID différents). Le compteur continue : il est dans le volume de `db`, `web` est **sans état**.
  - Leçon : visite 13 et non 14 → à la partie 5 la page n'avait pas vraiment été affichée. **Le terminal a toujours raison** : toujours coller la sortie brute.
- **Partie 7** : `Mounted from hhabchane/bonjour` (couches déjà dans un autre dépôt à moi), `Layer already exists` (déjà dans ce dépôt), `Pushed` (vraiment envoyée). Pour la v1, seulement 2 couches envoyées (`app.py` + métadonnées). Le digest = l'ID local.
- **Partie 8** : `db` arrêté → page **`500 Internal Server Error`**, `web` toujours **Up**. Logs : `redis.exceptions.ConnectionError: Error -3 connecting to db:6379. Temporary failure in name resolution.` (un conteneur arrêté disparaît du DNS interne). `docker compose start db` → healthy → visite 14 : `web` s'est reconnecté tout seul, rien n'a été perdu.
- **Partie 9** : supprimer les images en local ne les supprime **pas** de Docker Hub.

## Questions finales
1. `service_healthy` : l'application attend que la base soit **prête**, pas seulement démarrée → pas de connexion trop tôt.
2. Healthcheck honnête : `redis-cli -a ${REDIS_PASSWORD} ping | grep PONG`. Un simple `redis-cli ping` répond `NOAUTH` **avec le code 0** → Docker croit que tout va bien.
3. `.env` évite d'écrire le secret dans `compose.yaml` et de le publier sur GitHub ; il ne protège pas contre quelqu'un qui a accès à la machine ou à Docker (`docker compose config`, `docker inspect`).
4. **Reconstruire l'image** = refaire la recette (changement de code : `VERSION = "2"`). **Recréer le conteneur** = nouveau conteneur à partir d'une image existante (changement de réglage : `NOM_APP`).
5. Sans `hhabchane/`, `compteur-web:v2` = `docker.io/library/compteur-web:v2`, qui n'existe pas → `ErrImagePull` puis `ImagePullBackOff`.
6. Versions précises : on sait exactement ce qui tourne et on peut revenir en arrière ; `latest` ne bouge pas tout seul et ne dit pas quelle version tourne.
7. Un **healthcheck sur `web`** qui teste vraiment une page. ⚠️ `python:3.13-slim` n'a ni `curl` ni `wget` → tester avec Python :
   `python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000')"`. Dans Kubernetes : les **probes** (liveness / readiness).

## Leçon principale
**`Up` ≠ « ça marche »** : le conteneur peut tourner pendant que l'application est en panne. Seul un test qui vérifie le **vrai travail** de l'application le détecte.
