# 🚀 Server Stack — Homelab & Media Architecture

Bienvenue sur le dépôt **Server Stack**, une solution complète et conteneurisée d'infrastructure homelab dédiée au stockage de photos/vidéos, à la gestion multimédia (films, séries, sous-titres) et à un écosystème musical multi-utilisateurs avancé.

> 🔒 **Remarque sur la sécurité :** Tous les secrets, mots de passe de bases de données, tokens API et fichiers SQLite ont été nettoyés de ce dépôt. Des modèles de fichiers de configuration (`.env.example`, `.arl.example`) sont fournis.

---

## 🏛️ Vue d'ensemble de l'Architecture

Cette infrastructure s'articule autour de 3 sous-stacks Docker interconnectées et d'un gestionnaire de mises à jour automatique :

```
server-stack/
├── docker-compose.yml          # Watchtower (Mise à jour auto des conteneurs)
├── immich/                     # Stack Photos & Vidéos avec IA
│   ├── docker-compose.yml
│   └── .env.example
├── media/                      # Stack Films, Séries & Streaming
│   └── docker-compose.yml
└── music/                      # Stack Musique Multi-utilisateurs & StreamVault
    ├── docker-compose.yml
    ├── Dockerfile.deemix
    ├── patch_deezer.py
    ├── deezer-download.sh
    ├── sync-playlists.sh
    ├── star_favourites.py
    ├── delsong.sh
    └── web_app/                # Application Web StreamVault (Flask + UI)
```

---

## 📦 Détail des Stacks et Services

### 1. 🖼️ Stack Immich (Photos & Vidéos)
- **`immich-server`** : Serveur principal Immich pour la sauvegarde et le visionnage haute performance.
- **`immich-machine-learning`** : Module IA (reconnaissance faciale, détection d'objets, recherche sémantique CLIP).
- **`database`** (PostgreSQL 14 + pgvector) : Base de données relationnelle avec support des vecteurs IA.
- **`redis`** (Valkey) : Gestion des files d'attente de traitement d'images et d'invalidation de cache.

### 2. 🍿 Stack Media (Films, Séries, Streaming)
- **`jellyfin`** : Serveur de streaming multimédia (transcodage matériel `/dev/dri`).
- **`qbittorrent`** : Client de téléchargement BitTorrent avec WebUI sécurisée.
- **`prowlarr`** : Gestionnaire centralisé d'indexeurs BitTorrent / Usenet.
- **`sonarr`** : Gestionnaire et automatisation du téléchargement des séries TV.
- **`radarr`** : Gestionnaire et automatisation du téléchargement des films.
- **`bazarr`** : Recherche et téléchargement automatique des sous-titres (.srt).
- **`flaresolverr`** : Contournement automatique des protections Cloudflare / CAPTCHA pour les indexeurs.

### 3. 🎵 Stack Music & StreamVault (Musique & Automation)
- **`navidrome`** : Serveur de streaming audio principal Subsonic/Navidrome.
- **`navidrome-maman`** & **`navidrome-roland`** : Instances de streaming secondaires isolées par utilisateur/bibliothèque.
- **`music-search-web` (StreamVault)** : Interface web personnalisée (Flask + Javascript) permettant de chercher des artistes, albums, pistes sur Deezer, d'écouter un extrait et d'initier un téléchargement direct vers une bibliothèque spécifique.
- **`spotdl-web`** : Interface web pour le téléchargement de playlists Spotify via spotdl.
- **`slskd`** : Client P2P Soulseek autonome avec API Web UI.
- **`lidarr`** : Automatisation de la gestion et du téléchargement d'albums de musique.
- **`deemix-local`** : Image Docker construite sur mesure avec des correctifs Python (`patch_deezer.py`) pour le téléchargement FLAC/MP3 depuis Deezer.

---

## 🌐 Tableau des Ports & Services

| Service | Port Hôte | Port Conteneur | Description |
| :--- | :---: | :---: | :--- |
| **Immich Web UI** | `2283` | `2283` | Interface d'administration et de gestion de photos/vidéos |
| **Jellyfin** | `8096` | `8096` | Streaming de films, séries et médias |
| **qBittorrent WebUI** | `8085` | `8080` | Interface de gestion des torrents |
| **Prowlarr** | `9696` | `9696` | Gestionnaire d'indexeurs |
| **Sonarr** | `8989` | `8989` | Gestionnaire de séries TV |
| **Radarr** | `7878` | `7878` | Gestionnaire de films |
| **Bazarr** | `6767` | `6767` | Gestionnaire de sous-titres |
| **FlareSolverr** | `8191` | `8191` | Solveur de challenge Cloudflare |
| **Navidrome (Principal)** | `4533` | `4533` | Streaming musical Subsonic |
| **Navidrome (Maman)** | `4536` | `4533` | Instance Navidrome dédiée |
| **Navidrome (Roland)** | `4537` | `4533` | Instance Navidrome dédiée |
| **StreamVault Web UI** | `4535` | `4535` | App web de recherche & téléchargement musical |
| **SpotDL Web** | `4534` | `4534` | Interface de téléchargement Spotify |
| **Slskd (Soulseek)** | `5030` | `5030` | Interface web Soulseek |
| **Lidarr** | `8686` | `8686` | Gestionnaire de musique |

---

## 🛠️ Scripts & Utilitaires Inclus

Le dossier `music/` inclut plusieurs scripts shell et Python pour automatiser la gestion de la bibliothèque :

- **`deezer-download.sh`** : Télécharge des pistes, albums ou playlists Deezer en résolvant automatiquement les profils utilisateurs vers leurs coups de cœur.
- **`sync-playlists.sh`** : Synchronise automatiquement les playlists Spotify listées dans `playlists.txt` vers le stockage de musique.
- **`star_favourites.py`** : Script Python qui marque automatiquement tous les morceaux téléchargés de la playlist *Favourite tracks* comme Favoris (❤️) dans la base SQLite de Navidrome.
- **`delsong.sh`** : Script interactif pour supprimer un morceau ou artiste de la bibliothèque musicale.
- **`patch_deezer.py`** : Applique des correctifs directement dans le package Python Deezer/Deemix pour éviter les erreurs lors du téléchargement de métadonnées incomplètes.

---

## 🔐 Configuration des Secrets & Lancement

### 1. Pré-requis
- Docker Engine >= 24.0
- Docker Compose v2

### 2. Configuration d'Immich
```bash
cd immich
cp .env.example .env
```
Éditez `.env` et modifiez la variable `DB_PASSWORD` avec un mot de passe sécurisé :
```env
DB_PASSWORD=votre_mot_de_passe_securise
```

### 3. Configuration du Cookie Deezer (Deemix)
Pour utiliser le téléchargement Deezer, obtenez votre cookie `ARL` sur [deezer.com](https://www.deezer.com) (F12 -> Application -> Cookies -> `arl`) et créez le fichier :
```bash
echo "VOTRE_ARL_COOKIE" > music/config/deemix/.arl
```

### 4. Lancement des Stacks

**Démarrage de la stack globale :**
```bash
# Démarrer Watchtower
docker compose up -d

# Démarrer Immich
cd immich && docker compose up -d && cd ..

# Démarrer la stack Media
cd media && docker compose up -d && cd ..

# Démarrer la stack Musique
cd music && docker compose up -d && cd ..
```

---

## 📄 Licence & Contribution

Ce projet est sous licence MIT. N'hésitez pas à adapter ces fichiers Docker Compose et scripts à vos besoins personnels !
