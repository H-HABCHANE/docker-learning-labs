# Docker Learning Labs 🐳

Ce dépôt regroupe mes **travaux pratiques, exercices, contrôles et petits projets** réalisés pendant mon apprentissage de **Docker**, de zéro, sous Ubuntu.

Il s'agit d'un dépôt d'apprentissage : chaque dossier correspond à une étape de progression, avec mes fichiers de travail, les sujets et les corrigés.

## Structure du dépôt

```
.
├── README.md               ← ce fichier
├── notes.md                ← mon cours : résumé de chaque notion, erreurs rencontrées (cause + correction)
├── commandes-docker.md     ← aide-mémoire de toutes les commandes Docker, commentées
├── exercices/              ← exercices réalisés pendant le cours, un dossier par notion
│   ├── 07-dockerfile-nginx/    ← première image : nginx + ma page HTML (FROM, COPY)
│   ├── 08-dockerfile-python/   ← application Python empaquetée (WORKDIR, RUN, CMD)
│   ├── 09-docker-compose/      ← Compose : nginx + client qui se parlent par nom de service
│   └── 10-compose-volume/      ← Compose : build + volume nommé partagé (compteur de visites)
├── tp1/                    ← TP 1 : révision générale des notions 1 à 8
│   ├── SUJET.md
│   ├── CORRIGE.md
│   ├── Dockerfile, portfolio/  ← portfolio servi par nginx
│   └── app-python/             ← appli Python
└── tp2/                    ← TP 2 : Docker Compose (notions 9 et 10), « Le livre d'or »
    └── SUJET.md
```

À venir (même organisation) : `tp3/`…, `kubernetes/`, `projets/`.

## Notions couvertes

| # | Notion | Commandes / instructions clés |
|---|---|---|
| 1 | Image vs conteneur | `docker run`, `docker images`, `docker ps` |
| 2 | Supprimer conteneurs et images | `docker rm`, `docker rmi` |
| 3 | Entrer dans un conteneur | `docker pull`, `docker run -it` |
| 4 | Nommer et rallumer un conteneur | `--name`, `docker start -ai` |
| 5 | Serveur web en arrière-plan | `-d`, `-p`, `docker logs`, `docker stop` |
| 6 | Volumes | `-v dossier_pc:dossier_conteneur[:ro]` |
| 7 | Créer sa propre image | `Dockerfile`, `FROM`, `COPY`, `docker build` |
| 8 | Empaqueter une application | `WORKDIR`, `RUN`, `CMD`, `--rm`, cache de build |
| 9 | Docker Compose | `compose.yaml`, `services`, `depends_on`, `docker compose up/ps/logs/down` |
| 10 | Compose avancé | `build:`, volumes nommés, `service_completed_successfully`, `down -v` |

## Lancer les exemples

Prérequis : Docker installé, et l'utilisateur dans le groupe `docker`.

```bash
# Exercice 7 : site nginx → http://localhost:8080
cd exercices/07-dockerfile-nginx
docker build -t mon-site-image .
docker run --name site-v1 -d -p 8080:80 mon-site-image

# Exercice 8 : application Python
cd ../08-dockerfile-python
docker build -t mon-app .
docker run --rm mon-app
```

## Auteur

**Hicham Habchane** ([@H-HABCHANE](https://github.com/H-HABCHANE)), étudiant en apprentissage de Docker.
