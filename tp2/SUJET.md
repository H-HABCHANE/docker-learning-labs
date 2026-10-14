# TP 2 : Docker Compose (notions 9 et 10)

**Thème : « Le livre d'or »**
Un petit site qui affiche des messages. Il est fait de **3 services** qui travaillent ensemble :

```
 entree/messages.txt  (sur ton PC)
          │  bind mount, lecture seule
          ▼
 ┌──────────────┐  écrit index.html   ┌──────────────────┐   lit (ro)   ┌───────┐   ◀── PC : http://localhost:8090
 │  generateur  │ ──────────────────▶ │  volume nommé    │ ◀─────────── │  web  │
 │ (ton image   │  + generations.txt  │    "pages"       │              │ nginx │ ◀── testeur : http://web
 │   Python)    │                     └──────────────────┘              └───────┘
 └──────────────┘                                                            ▲
                                                                  ┌─────────┴──┐
                                                                  │  testeur   │
                                                                  │  (alpine)  │
                                                                  └────────────┘
```

## Règles du TP
- **Aucune commande n'est donnée**, seulement des objectifs. Tes `notes.md` et `commandes-docker.md` sont autorisés.
- Tout se passe dans **`~/docker-learning/tp2/`**. Vérifie avec **`pwd`** avant de créer un fichier !
- À chaque **🔍 Contrôle**, colle ta sortie de terminal **et** réponds aux questions **avec tes mots**.
- **Prédiction avant chaque test** marqué 🤔.
- Si tu bloques, demande un **indice**.

---

## Partie 0 : Préparer le terrain
1. Vérifie qu'aucun conteneur ne tourne et qu'aucun volume ne traîne d'un exercice précédent.
2. Crée le dossier `tp2/` avec un sous-dossier `entree/`, puis place-toi dans `tp2/`.
3. Crée `entree/messages.txt` avec **3 messages**, un par ligne (par exemple : `Bonjour !`, `Docker c'est top`, `Vive Compose`).

🔍 **Contrôle 0** : `pwd`, `ls -R` et `cat entree/messages.txt`.

---

## Partie 1 : L'image du générateur (notion 8)
1. Crée `generateur.py` avec ce code (fourni) :
   ```python
   from pathlib import Path
   from datetime import datetime

   messages = Path("/entree/messages.txt").read_text(encoding="utf-8").splitlines()
   messages = [m for m in messages if m.strip()]

   fichier_compteur = Path("/sortie/generations.txt")
   n = int(fichier_compteur.read_text()) + 1 if fichier_compteur.exists() else 1
   fichier_compteur.write_text(str(n))

   items = "\n".join(f"<li>{m}</li>" for m in messages)
   Path("/sortie/index.html").write_text(
       f"<h1>Livre d'or</h1>\n<ul>\n{items}\n</ul>\n"
       f"<p>Page generee {n} fois, derniere fois le {datetime.now():%d/%m/%Y %H:%M:%S}</p>\n",
       encoding="utf-8",
   )
   print(f"Generation {n} : {len(messages)} message(s)")
   ```
2. Écris le **Dockerfile** : base `python:3.13-slim`, dossier de travail `/app`, copie de `generateur.py`, et lancement de `python generateur.py` au démarrage.

❓ Le programme lit `/entree/messages.txt` et écrit dans `/sortie/`. Pourquoi ne faut-il **pas** copier `messages.txt` dans l'image avec `COPY` ?

---

## Partie 2 : Le fichier `compose.yaml` (notions 9 et 10)
Écris `compose.yaml` avec **3 services** et **1 volume nommé** :

| Service | Contenu |
|---|---|
| `generateur` | construit depuis le Dockerfile du dossier ; le dossier `./entree` monté sur `/entree` **en lecture seule** (bind mount) ; le volume nommé **`pages`** monté sur `/sortie` |
| `web` | image `nginx` ; port **8090** du PC → port 80 ; le volume `pages` monté sur `/usr/share/nginx/html` **en lecture seule** ; démarre **seulement quand `generateur` a terminé avec succès** |
| `testeur` | image `alpine` ; démarre **après** `web` ; commande : attendre 2 secondes puis afficher la page de `web` **en l'appelant par son nom** |

N'oublie pas la **déclaration** du volume nommé en bas du fichier.

🔍 **Contrôle 2** : `cat Dockerfile` et `cat compose.yaml`. **Montre-les avant de lancer quoi que ce soit.**
❓ Quel service a besoin de `ports:`, et pourquoi **un seul** ?

---

## Partie 3 : Premier lancement
1. 🤔 Prédiction : après le lancement, quel sera l'**état** de chacun des 3 services (`Up` ou `Exited`) ? Pourquoi ?
2. Lance le projet **en reconstruisant l'image**.
3. Affiche l'état de **tous** les services du projet, y compris ceux qui sont arrêtés.
4. Affiche les logs de `generateur`, puis ceux de `testeur`.
5. Affiche la page **depuis ton PC**.
6. Retrouve le **volume** et l'**image** créés par Compose, et note leurs noms.

🔍 **Contrôle 3** : les sorties des étapes 2 à 6.
❓ Pourquoi `testeur` utilise `http://web`, alors que toi tu utilises `http://localhost:8090` ?

---

## Partie 4 : Bind mount et génération
1. Ajoute un **4ᵉ message** à `entree/messages.txt`, **sans toucher aux conteneurs**.
2. 🤔 Prédiction : la page affichera-t-elle le 4ᵉ message tout de suite ? Pourquoi ?
3. Vérifie avec `curl`.
4. Fais en sorte que la page soit **régénérée**, sans tout relancer. 💡 Un seul service à rallumer.
5. Vérifie : le 4ᵉ message est-il là ? Et le compteur « Page generee N fois » ?

🔍 **Contrôle 4** : les sorties des étapes 3 à 5.
❓ `messages.txt` est dans un bind mount, donc il est « en direct ». Pourquoi la page n'a-t-elle pas changé toute seule ?

---

## Partie 5 : Persistance des données
1. 🤔 Prédiction : après **arrêt et suppression** des conteneurs (en gardant les volumes), puis relance, quel nombre affichera « Page generee N fois » ?
2. Vérifie.
3. 🤔 Prédiction : même question, mais en supprimant **aussi les volumes**. Et les messages seront-ils perdus ?
4. Vérifie.

🔍 **Contrôle 5** : les sorties, avec les lignes `Removed` / `Created` bien visibles.
❓ Pourquoi le compteur repart-il de 1, alors que les **messages**, eux, ne sont **pas** perdus ?

---

## Partie 6 : Provoquer une panne 💥
1. Dans `compose.yaml`, ajoute **temporairement** au service `generateur` une `command:` qui lance un fichier qui n'existe pas : `python inexistant.py`.
2. 🤔 Prédiction : que va-t-il arriver à `generateur` ? Et à `web` ? Et à `testeur` ?
3. Lance le projet et lis **attentivement** le message d'erreur.
4. Regarde l'état des services et le code de sortie de `generateur`.
5. **Répare** : retire la ligne `command:`, relance, et vérifie que le site fonctionne.

🔍 **Contrôle 6** : le message d'erreur, l'état des services, puis la preuve que c'est réparé.
❓ Quelle ligne du `compose.yaml` empêche `web` de démarrer ? Pourquoi est-ce une **bonne** chose ?

---

## Partie 7 : Ménage final 🧹
1. Arrête et supprime **tout** le projet, volumes compris.
2. Supprime l'image construite par Compose pour ce TP.
3. Vérifie qu'il ne reste aucun conteneur ni volume du TP, que les images des **autres projets** sont intactes, et que `entree/messages.txt` existe toujours.

🔍 **Contrôle 7** : `docker ps -a`, `docker volume ls`, `docker images` et `cat entree/messages.txt`.

---

## Questions finales (sans notes, avec tes mots)
1. À quoi sert Docker Compose, par rapport à plusieurs `docker run` ?
2. Comment s'appelle le projet Compose, et d'où vient ce nom ? Donne le nom complet d'un conteneur et du volume de ce TP.
3. Différence entre `image:` et `build:` dans un `compose.yaml` ?
4. Différence entre un **bind mount** et un **volume nommé** ? Le TP utilise les deux : pour quoi, et pourquoi ce choix ?
5. Différence entre `depends_on` simple et `condition: service_completed_successfully` ?
6. Différence entre `docker compose down` et `docker compose down -v` ? Laquelle est dangereuse, et pourquoi ?
7. Comment deux services d'un même projet communiquent-ils ? Ont-ils besoin de `ports:` pour ça ?
8. `docker compose start generateur` et `docker compose up -d` : dans la partie 4, pourquoi la première suffisait-elle ?

Bon courage ! 💪🐳
