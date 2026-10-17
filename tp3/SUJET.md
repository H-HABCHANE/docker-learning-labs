# TP 3 : Révision des notions 11 à 13

**Thème : « Le compteur web »**
Un vrai petit **site web** en Python (Flask) qui compte ses visiteurs dans une base **Redis protégée par un mot de passe**. L'image sera **versionnée** et **publiée sur Docker Hub** : c'est elle que tu déploieras ensuite dans **Kubernetes**.

```
  PC : http://localhost:8080
            │  ports 8080 → 5000
            ▼
   ┌──────────────────┐   REDIS_HOST=db + mot de passe   ┌──────────────────┐
   │       web        │ ───────────────────────────────▶ │        db        │
   │ (ton image Flask │                                  │  redis + volume  │
   │  hhabchane/...)  │   démarre seulement quand db     │  + healthcheck   │
   └──────────────────┘   est healthy                    └──────────────────┘
            ▲                                                     ▲
            └──────────── .env (REDIS_PASSWORD, jamais sur GitHub) ┘
```

## Règles du TP
- **Aucune commande n'est donnée**, seulement des objectifs. Tes `notes.md` et `commandes-docker.md` sont autorisés.
- Tout se passe dans **`~/docker-learning/tp3/`**. Vérifie avec **`pwd`** avant de créer un fichier, et travaille dans **un seul terminal**.
- À chaque **🔍 Contrôle**, colle ta sortie de terminal **et** réponds aux questions **avec tes mots** (une phrase à toi vaut mieux qu'un beau texte copié).
- **Prédiction avant chaque test** marqué 🤔.
- Si tu bloques, demande un **indice**.

---

## Partie 0 : Préparer le terrain
1. Vérifie qu'aucun conteneur ne tourne (à part `minikube`, qu'on ne touche pas) et que tu es toujours connecté à Docker Hub.
2. Crée le dossier `tp3/` (s'il n'existe pas) et place-toi dedans.

🔍 **Contrôle 0** : `pwd`, `docker ps -a` et la preuve que tu es connecté à Docker Hub.

---

## Partie 1 : L'application et son image (notions 8 et 11)
1. Crée `app.py` avec ce code (fourni) :
   ```python
   import os
   import redis
   from flask import Flask

   VERSION = "1"
   NOM = os.environ.get("NOM_APP", "Sans nom")

   r = redis.Redis(
       host=os.environ.get("REDIS_HOST", "localhost"),
       port=6379,
       password=os.environ.get("REDIS_PASSWORD"),
   )

   app = Flask(__name__)

   @app.route("/")
   def accueil():
       n = r.incr("visites")
       return f"[{NOM}] version {VERSION} - visite numero {n}\n"

   # 0.0.0.0 = accepter les connexions venant de l'exterieur du conteneur
   app.run(host="0.0.0.0", port=5000)
   ```
   **Nouveauté** : contrairement au compteur des exercices 11 et 12, ce programme **ne s'arrête pas** : c'est un **serveur web** (comme nginx) qui écoute sur le port **5000** et compte une visite **à chaque page affichée**.
2. Écris le **Dockerfile** : base `python:3.13-slim`, dossier de travail `/app`, installation des bibliothèques **`flask`** et **`redis`**, copie de `app.py`, lancement de `python app.py`.

❓ Dans quel ordre places-tu l'installation des bibliothèques et la copie de `app.py` ? Pourquoi ?

---

## Partie 2 : Le secret (notion 12)
1. Crée le fichier qui contient le mot de passe de Redis (variable `REDIS_PASSWORD`, choisis la valeur).
2. Crée son « mode d'emploi » versionnable, avec une valeur bidon.
3. Prouve que Git **ignore** le vrai fichier secret, mais **pas** le mode d'emploi.

🔍 **Contrôle 2** : `ls -a` et les sorties Git qui le prouvent (**ne colle pas** le contenu du vrai fichier secret).

---

## Partie 3 : Le fichier `compose.yaml` (notions 9 à 13)
Écris `compose.yaml` avec **2 services** et **1 volume nommé** :

| Service | Contenu |
|---|---|
| `db` | image `redis` ; démarre Redis **avec le mot de passe** ; volume nommé **`donnees`** sur `/data` ; un healthcheck **honnête** (qui échoue vraiment si le mot de passe est faux), toutes les 2 s, 5 essais |
| `web` | construit depuis le Dockerfile du dossier ; l'image construite doit s'appeler **`hhabchane/compteur-web:v1`** (voir l'astuce ci-dessous) ; port **8080** du PC → port **5000** du conteneur ; reçoit `REDIS_HOST`, `REDIS_PASSWORD` (lu dans le fichier secret) et `NOM_APP` (`Compteur TP3`) ; démarre **seulement quand `db` est en bonne santé** |

💡 **Astuce Compose (petite nouveauté)** : si un service a **à la fois** `build: .` **et** `image: nom:tag`, Compose construit l'image avec le Dockerfile **et lui donne ce nom-là** (au lieu de `<projet>-<service>`).

Le mot de passe ne doit apparaître **nulle part** en clair dans `compose.yaml`.

🔍 **Contrôle 3** : `cat Dockerfile` et `cat compose.yaml`. **Montre-les avant de lancer quoi que ce soit.**
❓ Pourquoi le port à droite (`5000`) n'est-il pas le même que dans le TP 2 (`80`) ?

---

## Partie 4 : Premier lancement
1. 🤔 Prédiction : après le lancement, quel sera l'**état** de `web` (`Up` ou `Exited`) ? Pourquoi est-ce différent des exercices 11 et 12 ?
2. Lance le projet **en reconstruisant l'image**.
3. Affiche l'état de tous les services : `db` doit être **healthy**.
4. Affiche la page **3 fois** depuis ton PC (dans le terminal).
5. Affiche les images `hhabchane/compteur-web` présentes sur ton PC.

🔍 **Contrôle 4** : les sorties des étapes 2 à 5.

---

## Partie 5 : Changer un réglage sans reconstruire (notion 12)
1. Change `NOM_APP` en `Super compteur`.
2. 🤔 Prédiction : quel service sera **recréé** ? L'image sera-t-elle **reconstruite** ? Quel numéro de visite verras-tu ?
3. Applique le changement et affiche la page.

🔍 **Contrôle 5** : les sorties.

---

## Partie 6 : Sortir une version 2 (notion 13)
1. Passe l'application en **version 2** (dans `app.py`), et fais en sorte que la nouvelle image s'appelle **`hhabchane/compteur-web:v2`**.
2. 🤔 Prédiction : le compteur de visites va-t-il repartir à 1 ? Et l'image **v1** existera-t-elle encore sur ton PC ?
3. Relance **en reconstruisant**, puis affiche la page et les images `hhabchane/compteur-web`.

🔍 **Contrôle 6** : les sorties.
❓ Pourquoi n'a-t-on **jamais** utilisé le tag `latest` dans ce TP ?

---

## Partie 7 : Publier (notion 13)
1. 🤔 Prédiction : combien de tags verras-tu sur Docker Hub après **un seul** envoi de la v2 ?
2. Envoie **les deux versions** (v1 et v2) sur Docker Hub.
3. Vérifie sur `https://hub.docker.com/r/hhabchane/compteur-web` (onglet **Tags**).

🔍 **Contrôle 7** : les sorties des envois (au moins la dernière ligne `digest:` de chacun) et les tags vus sur le site.

---

## Partie 8 : Provoquer une panne 💥
1. 🤔 Prédiction : si tu **arrêtes uniquement** le service `db` (sans le supprimer), que deviendra l'état de `web` ? Et que verras-tu en affichant la page ?
2. Arrête uniquement `db`.
3. Affiche la page, l'état des services, puis les **dernières lignes** des logs de `web`.
4. **Répare** : rallume `db`, attends qu'il soit healthy, et affiche la page. Le compteur a-t-il été perdu ?

🔍 **Contrôle 8** : le message d'erreur (dernière ligne du traceback), l'état des services, puis la preuve que c'est réparé.
❓ `web` est resté `Up` alors que le site ne marchait plus. Qu'est-ce que ça t'apprend sur la différence entre « le conteneur tourne » et « l'application fonctionne » ?

---

## Partie 9 : Ménage final 🧹
1. Arrête et supprime le projet, **volumes compris**.
2. Supprime les images `hhabchane/compteur-web` **de ton PC**.
3. 🤔 Prédiction : ces images sont-elles encore sur Docker Hub ?
4. Vérifie : aucun conteneur ni volume du TP, les images des **autres projets** intactes, et les tags toujours présents sur Docker Hub.

🔍 **Contrôle 9** : `docker ps -a`, `docker volume ls`, `docker images`, et ce que tu vois sur Docker Hub.

---

## Questions finales (sans notes, avec tes mots)
1. Pourquoi `depends_on` avec `condition: service_healthy` est-il utile pour une base de données ?
2. Comment as-tu rendu le healthcheck **honnête** ? Que se passait-il avec un simple `redis-cli ping` quand Redis avait un mot de passe ?
3. Pourquoi le mot de passe est-il dans `.env` et pas dans `compose.yaml` ? Contre quoi `.env` ne protège-t-il **pas** ?
4. Différence entre **reconstruire l'image** et **recréer le conteneur** ? Donne un exemple du TP pour chacun.
5. Que se passerait-il si une machine Kubernetes recevait l'ordre de lancer `compteur-web:v2` (sans `hhabchane/`) ?
6. Pourquoi publie-t-on des versions précises (`v1`, `v2`) plutôt que `latest` ?
7. Dans la partie 8, quel outil aurait pu détecter que `web` ne fonctionnait plus ? (Pense à ce que tu as appris en notion 11.)

Bon courage ! 💪🐳
