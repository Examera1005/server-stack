# 🚀 Server Stack — Infrastructure Homelab, Média & Musique Prête pour la Production

[![Licence: MIT](https://img.shields.io/badge/Licence-MIT-yellow.svg)](LICENSE)
[![Docker Compose](https://img.shields.io/badge/Docker--Compose-v2%2B-blue.svg)](https://docs.docker.com/compose/)
[![Architecture](https://img.shields.io/badge/Stack-Immich%20%7C%20M%C3%A9dia%20%7C%20Musique-emerald.svg)](#-vue-densemble-de-larchitecture)

> 🌐 **Langue / Language :** **[English](README.md)** | **Français (French)**

Une infrastructure **Homelab complète, modulaire et conteneurisée** conçue pour la gestion automatisée des médias (Films, Séries, Sous-titres), la sauvegarde de photos/vidéos propulsée par IA (Immich), le streaming musical multi-utilisateurs haute fidélité (Navidrome) et une application web de découverte musicale sur mesure (**StreamVault**).

---

## 🏛️ Vue d'ensemble de l'Architecture

Le dépôt est structuré en sous-stacks indépendantes qui peuvent être déployées ensemble ou séparément :

```
server-stack/
├── docker-compose.yml          # Conteneur Watchtower (Mises à jour automatiques)
├── LICENSE                     # Licence open-source MIT
├── CONTRIBUTING.md             # Guide de contribution
├── immich/                     # Stack Photos & Vidéos avec IA
│   ├── docker-compose.yml
│   └── .env.example
├── media/                      # Stack Films, Séries & Sous-titres
│   └── docker-compose.yml
└── music/                      # Stack Musique Multi-utilisateurs & StreamVault
    ├── docker-compose.yml
    ├── Dockerfile.deemix
    ├── patch_deezer.py
    ├── deezer-download.sh
    ├── sync-playlists.sh
    ├── star_favourites.py
    ├── delsong.sh
    └── web_app/                # Application Web StreamVault (Flask + Design Sombre)
        ├── Dockerfile
        ├── app.py
        └── templates/index.html
```

---

## 📦 Détail des Stacks & Fonctionnalités

### 🖼️ 1. Stack Immich (Photos & Vidéos)
- **Immich Server** : Serveur de sauvegarde photos et vidéos haute performance avec synchronisation web et mobile.
- **Moteur Machine Learning** : Reconnaissance faciale, détection d'objets et recherche sémantique CLIP.
- **PostgreSQL 14 + pgvector** : Base de données vectorielle pour les embeddings IA.
- **Redis (Valkey)** : Cache rapide et traitement des files d'attente.

### 🍿 2. Stack Média (Films, Séries & Sous-titres)
- **Jellyfin** : Serveur de streaming multimédia sans suivi, avec support du transcodage matériel GPU (`/dev/dri`).
- **qBittorrent** : Client de téléchargement torrent haute vitesse avec Web UI.
- **Prowlarr** : Gestionnaire d'indexeurs synchronisé avec Sonarr/Radarr.
- **Sonarr** : Automatisation et organisation du téléchargement de séries TV.
- **Radarr** : Automatisation et organisation du téléchargement de films.
- **Bazarr** : Téléchargement automatique de sous-titres (.srt).
- **FlareSolverr** : Proxy de contournement des protections anti-bot Cloudflare.

### 🎵 3. Stack Musique & Application StreamVault
- **Navidrome (Multi-instances)** : Serveurs de streaming compatibles Subsonic avec instances isolées pour bibliothèques familiales multi-utilisateurs.
- **StreamVault Web Application** (Port `4535`) : Interface web personnalisée construite avec Flask et un design dark mode glassmorphism. Inclut la recherche Deezer, les tops charts, un lecteur d'extrait audio et le téléchargement conteneurisé en 1 clic vers une bibliothèque ciblée.
- **SpotDL Web** : Interface web de téléchargement de playlists Spotify.
- **Slskd** : Client P2P Soulseek autonome avec interface web.
- **Lidarr** : Automatisation de la collection musicale.
- **Deemix CLI (Patché)** : Conteneur Docker personnalisé intégrant `patch_deezer.py` pour corriger les erreurs de métadonnées et tags Deezer.

---

## 🌐 Tableau des Ports & Services

| Nom du Service | Port (Hôte:Conteneur) | Rôle du Service |
| :--- | :---: | :--- |
| **Immich Web UI** | `2283:2283` | Gestionnaire de photos & vidéos |
| **Jellyfin** | `8096:8096` | Plateforme de streaming média |
| **qBittorrent WebUI** | `8085:8080` | Gestionnaire de téléchargements torrent |
| **Prowlarr** | `9696:9696` | Gestionnaire d'indexeurs Torrent / Usenet |
| **Sonarr** | `8989:8989` | Automatisation Séries TV |
| **Radarr** | `7878:7878` | Automatisation Films |
| **Bazarr** | `6767:6767` | Automatisation Sous-titres |
| **FlareSolverr** | `8191:8191` | Proxy de contournement Cloudflare |
| **Navidrome (Principal)** | `4533:4533` | Serveur de streaming audio Subsonic |
| **Navidrome (Secondaire 1)**| `4536:4533` | Instance isolée de bibliothèque musicale |
| **Navidrome (Secondaire 2)**| `4537:4533` | Instance isolée de bibliothèque musicale |
| **StreamVault Web UI** | `4535:4535` | App web de recherche & téléchargement musical |
| **SpotDL Web UI** | `4534:4534` | Téléchargeur de playlists Spotify |
| **Slskd (Soulseek)** | `5030:5030` | Interface P2P Soulseek |
| **Lidarr** | `8686:8686` | Gestionnaire d'automation musicale |

---

## 🛠️ Scripts & Utilitaires de Personnalisation

Le dossier `music/` inclut plusieurs scripts shell et Python :

- **`deezer-download.sh`** : Télécharge des pistes, albums ou playlists Deezer en résolvant automatiquement les liens de profil utilisateur vers leur playlist de Coups de cœur.
- **`sync-playlists.sh`** : Synchronise automatiquement les playlists Spotify listées dans `config/spotdl/playlists.txt`.
- **`star_favourites.py`** : Script Python qui marque automatiquement tous les morceaux téléchargés de la playlist *Favourite tracks* comme Favoris (❤️) dans la base SQLite Navidrome.
- **`delsong.sh`** : Script shell interactif pour rechercher et supprimer un morceau du stockage hôte.
- **`patch_deezer.py`** : Applique des correctifs lors du build Docker dans la bibliothèque Deemix (gestion des paroles manquantes, énumérations, etc.).

---

## ⚙️ Instructions de Personnalisation (Ajout/Retrait/Commentaires)

### 1. Modifier les Chemins de Stockage
Par défaut, les fichiers compose montent les volumes sur `/mnt/hdd/media`. Si votre disque de stockage est ailleurs (ex: `/mnt/stockage` ou `/data/media`) :
- Ouvrez `media/docker-compose.yml` ou `music/docker-compose.yml`.
- Recherchez `/mnt/hdd/media` et remplacez-le par votre chemin hôte réel.

### 2. Activer / Désactiver l'Accélération Matérielle (GPU Transcoding)
- **Intel / AMD iGPU** : Dans `media/docker-compose.yml` (Jellyfin) et `immich/docker-compose.yml` (Immich), le périphérique `/dev/dri:/dev/dri` est transmis.
- **Nvidia GPU** : Installez `nvidia-container-toolkit` et ajoutez `runtime: nvidia` dans le service concerné.
- **CPU uniquement** : Si votre serveur n'a pas de GPU compatible, commentez ou supprimez simplement les lignes avec `/dev/dri`.

### 3. Activer / Désactiver les Instances Navidrome Secondaires
Si vous n'avez besoin que d'une seule bibliothèque musicale, ouvrez `music/docker-compose.yml` et commentez ou supprimez les blocs de services `navidrome-maman` et `navidrome-roland`.

---

## 🚀 Guide d'Installation Rapide

### Pré-requis
- Docker Engine >= 24.0
- Docker Compose v2
- Git

### Étape 1 : Cloner le Dépôt
```bash
git clone https://github.com/VOTRE_PSEUDO/server-stack.git
cd server-stack
```

### Étape 2 : Configurer les Fichiers d'Environnement

1. **Configuration d'Immich :**
   ```bash
   cd immich
   cp .env.example .env
   ```
   Éditez `.env` et définissez un mot de passe sécurisé pour `DB_PASSWORD`.

2. **Configuration du Cookie Deezer (Deemix) :**
   ```bash
   mkdir -p music/config/deemix
   echo "VOTRE_ARL_COOKIE_DEEZER" > music/config/deemix/.arl
   ```
   *(Pour trouver votre ARL : Connectez-vous sur deezer.com -> F12 -> Application -> Cookies -> `arl`)*

### Étape 3 : Lancer les Services

```bash
# 1. Démarrer Watchtower (Racine)
docker compose up -d

# 2. Démarrer la stack Immich
cd immich && docker compose up -d && cd ..

# 3. Démarrer la stack Média
cd media && docker compose up -d && cd ..

# 4. Démarrer la stack Musique
cd music && docker compose up -d && cd ..
```

---

## 🔐 Sécurité & Bonnes Pratiques

- **Aucun secret dans le dépôt** : Tous les mots de passe et clés sont ignorés grâce à `.gitignore`.
- **Permissions Utilisateur (`PUID`/`PGID`)** : Assurez-vous que les variables `PUID` et `PGID` correspondent à votre utilisateur système (`id -u` / `id -g`).
- **Reverse Proxy** : Il est recommandé de placer ces services derrière un reverse proxy comme **Nginx Proxy Manager**, **Traefik**, ou **Cloudflare Tunnels** avec des certificats SSL (HTTPS).

---

## 📄 Licence & Contribution

Projet distribué sous licence **MIT**. Voir le fichier [`LICENSE`](LICENSE) pour plus de détails.

Les contributions sont les bienvenues ! Veuillez consulter le guide [`CONTRIBUTING.md`](CONTRIBUTING.md) avant d'ouvrir une PR.
