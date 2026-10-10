# TP 1 : Révision générale (notions 1 à 8)

**Thème : « Mon portfolio Docker »**
Tu vas construire, étape par étape, un petit portfolio web et une appli Python, en utilisant **toutes** les notions vues.

## Règles du TP
- **Aucune commande n'est donnée** : seulement des objectifs. À toi de trouver la commande (tes `notes.md` sont autorisées 😉).
- Travaille dans un nouveau dossier : `~/docker-learning/tp1/`.
- À chaque **🔍 Contrôle**, colle-moi le résultat. Je corrige avant que tu passes à la suite.
- Si tu bloques, demande-moi un **indice**.
- Les commandes interactives (`-it`, `nano`) vont dans le **vrai terminal**.
- ⚠️ Ne touche **jamais** aux images des autres projets (spark, cuda…).

---

## Partie 0 : Préparer le terrain 🧹
1. Vérifie quels conteneurs existent (même arrêtés).
2. Arrête puis supprime `site-v1` s'il existe encore.
3. Crée le dossier `tp1`, puis va dedans.

🔍 **Contrôle 0** : la liste de **tous** les conteneurs doit être vide, et `pwd` doit afficher `.../docker-learning/tp1`.

---

## Partie 1 : Images et conteneurs (notions 1, 2, 3)
1. Télécharge l'image **`alpine`** **sans** lancer de conteneur. C'est un Linux minuscule, tu vas comparer sa taille avec `ubuntu`.
2. Affiche tes images et compare la taille d'`alpine` et d'`ubuntu`.
3. Lance **3 fois** un conteneur `alpine` qui exécute la commande `echo Bonjour`. 💡 Après le nom de l'image, tu peux écrire la commande à lancer.
4. Compte les images `alpine` et les conteneurs `alpine` que tu as.
5. Essaie de supprimer l'image `alpine`. Lis bien le message.
6. Fais le ménage **dans le bon ordre**, puis supprime l'image `alpine`.

🔍 **Contrôle 1** : colle-moi les sorties des étapes 2, 4 et 5.
❓ Combien d'images et combien de conteneurs avais-tu à l'étape 4 ? Pourquoi ?

---

## Partie 2 : Conteneur nommé et persistant (notions 3, 4)
1. Lance un conteneur `ubuntu` **interactif**, nommé **`carnet`**.
2. À l'intérieur, crée le fichier `/notes/jour1.txt` contenant `TP1 commencé`. 💡 Il faut d'abord créer le dossier `/notes` (`mkdir`).
3. Sors du conteneur.
4. Vérifie son **état** (STATUS).
5. **Rallume** `carnet`, entre dedans et vérifie que ton fichier est toujours là. Puis sors.
6. Essaie de lancer un **nouveau** conteneur nommé `carnet`. Que se passe-t-il ?
7. Lance un conteneur `ubuntu` **qui se supprime tout seul** à l'arrêt, et vérifie si `/notes/jour1.txt` existe dedans.

🔍 **Contrôle 2** : colle-moi les sorties des étapes 4, 5, 6 et 7.
❓ Pourquoi le fichier existe à l'étape 5 mais pas à l'étape 7 ?

---

## Partie 3 : Le portfolio en direct avec un volume (notions 5, 6)
1. Crée un dossier `portfolio/` contenant un `index.html` avec ton nom dans un `<h1>`, et une phrase « Version volume » dans un `<p>`.
2. Lance un nginx :
   - nommé **`portfolio-live`**,
   - en **arrière-plan**,
   - sur le port **9000** de ton PC,
   - qui sert ton dossier `portfolio/` **en lecture seule**.
3. Vérifie qu'il **tourne**, et lis la colonne PORTS.
4. Affiche la page **dans le terminal**, puis dans Firefox.
5. Modifie la phrase en « Version volume modifiée », **sans toucher au conteneur**, et revérifie.
6. Affiche les **logs** de `portfolio-live` et retrouve tes visites (code `200`).

🔍 **Contrôle 3** : colle-moi les sorties des étapes 3, 4, 5 et un extrait des logs.
❓ Dans `-p 9000:80`, que représente chaque nombre ?

---

## Partie 4 : Le portfolio en image autonome (notion 7)
1. Dans `tp1/`, écris un **Dockerfile** qui part de `nginx` et y **copie** le dossier `portfolio/`.
2. Construis l'image **`portfolio:v1`**. 💡 Après les deux-points, c'est le **tag** (la version). Jusqu'ici tu utilisais `latest` sans le savoir !
3. Lance un conteneur **`portfolio-v1`** à partir de cette image, en arrière-plan, sur le port **9001**.
4. Tu as maintenant **deux** sites en même temps : vérifie les ports 9000 **et** 9001.
5. Modifie `portfolio/index.html` : « Version 2 ».
6. Vérifie 9000 et 9001. Lequel a changé ? **Fais ta prédiction avant !**
7. Construis **`portfolio:v2`**, sans supprimer `v1`. Observe le **cache** dans la sortie.
8. Lance **`portfolio-v2`** sur le port **9002**.
9. Affiche tes images : combien de lignes `portfolio` vois-tu ?

🔍 **Contrôle 4** : colle-moi le Dockerfile, les sorties des étapes 6, 7 (juste les lignes `[1/2]` et `[2/2]`) et 9.
❓ Pourquoi 9001 n'a pas changé à l'étape 6 ? Et pourquoi peut-on avoir 3 nginx en même temps, tous sur le port 80 à l'intérieur ?

---

## Partie 5 : Une appli Python (notion 8)
1. Crée un sous-dossier `appli/` avec ce fichier `app.py` (je te le donne) :
   ```python
   import datetime, os
   print("=== Fiche de l'appli ===")
   print("Version      :", open("version.txt").read().strip())
   print("Construite le:", open("build-info.txt").read().strip())
   print("Lancée le    :", datetime.datetime.now())
   print("Dossier      :", os.getcwd())
   ```
2. Crée aussi `appli/version.txt` contenant `1.0`.
3. Écris le **Dockerfile** de `appli/` :
   - base `python:3.13-slim`,
   - dossier de travail **`/projet`**,
   - copie de `app.py` **et** `version.txt`,
   - pendant le build, enregistre la date dans `build-info.txt`,
   - au démarrage, lance `python app.py`.
4. Construis l'image **`appli:1.0`**.
5. Lance-la **2 fois** avec suppression automatique, à une minute d'écart.
6. Passe `version.txt` à `2.0`, construis **`appli:2.0`**, et lance les **deux versions** l'une après l'autre.

🔍 **Contrôle 5** : colle-moi le Dockerfile et les sorties des étapes 5 et 6.
❓ Quelle ligne change entre les deux lancements de l'étape 5, et laquelle reste fixe ? Pourquoi ?
❓ Que vaut « Dossier », et quelle instruction l'explique ?

---

## Partie 6 : Grand ménage final 🧹
1. Arrête et supprime **tous** les conteneurs du TP (`portfolio-live`, `portfolio-v1`, `portfolio-v2`, `carnet`), en **une seule** commande `rm` si tu peux.
2. Supprime les images du TP : `portfolio:v1`, `portfolio:v2`, `appli:1.0`, `appli:2.0`.
3. Vérifie que les fichiers de `portfolio/` sont **toujours sur ton PC**.
4. Vérifie que les images des **autres projets** sont intactes.

🔍 **Contrôle 6** : colle-moi `docker ps -a`, `docker images` et `ls portfolio`.

---

## Questions finales (sans regarder tes notes !)
1. Différence entre une **image** et un **conteneur** ?
2. Différence entre `docker run` et `docker start` ?
3. Différence entre `docker ps` et `docker ps -a` ?
4. Différence entre **COPY** (Dockerfile) et un **volume** (`-v`) ? Donne un cas où chacun est préférable.
5. Différence entre **RUN** et **CMD** ?
6. Que signifie le `.` à la fin de `docker build` ?
7. Pourquoi un conteneur `ubuntu` s'arrête après `exit`, alors qu'un nginx reste allumé ?
8. Tu obtiens « Conflict. The container name is already in use », mais `docker ps` est vide. Que se passe-t-il et que fais-tu ?

Bon courage ! 💪🐳
