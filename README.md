# 🚀 Server Stack — Production-Ready Homelab, Media & Music Infrastructure

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker Compose](https://img.shields.io/badge/Docker--Compose-v2%2B-blue.svg)](https://docs.docker.com/compose/)
[![Architecture](https://img.shields.io/badge/Stack-Immich%20%7C%20Media%20%7C%20Music-emerald.svg)](#-architecture-overview)

> 🌐 **Language / Langue :** **English** | **[Français (French)](README.fr.md)**

A comprehensive, modular, and containerized **Homelab Infrastructure Stack** designed for automated media management (Movies, TV Shows, Subtitles), AI-driven photo & video backup with Immich, multi-user high-fidelity music streaming with Navidrome, and custom music discovery & downloading via **StreamVault**.

---

## 🏛️ Architecture Overview

The repository is structured into isolated, independent sub-stacks that can be deployed individually or together:

```
server-stack/
├── docker-compose.yml          # Root Watchtower container updater
├── LICENSE                     # Open-source MIT License
├── CONTRIBUTING.md             # Contribution guidelines
├── immich/                     # AI-Powered Photo & Video Backup Stack
│   ├── docker-compose.yml
│   └── .env.example
├── media/                      # Movies, TV Shows, Subtitles & Download Pipeline
│   └── docker-compose.yml
└── music/                      # Multi-User Music Streaming & StreamVault UI
    ├── docker-compose.yml
    ├── Dockerfile.deemix
    ├── patch_deezer.py
    ├── deezer-download.sh
    ├── sync-playlists.sh
    ├── star_favourites.py
    ├── delsong.sh
    └── web_app/                # StreamVault Custom Web App (Flask + Modern Dark UI)
        ├── Dockerfile
        ├── app.py
        └── templates/index.html
```

---

## 📦 Stack Breakdown & Features

### 🖼️ 1. Immich Stack (Photos & Videos)
- **Immich Server**: High-performance photo/video backup server with web and mobile app sync.
- **Machine Learning Engine**: Facial recognition, object detection, and CLIP semantic search.
- **PostgreSQL 14 + pgvector**: Vector database for AI search embeddings.
- **Redis (Valkey)**: Fast cache and job queue processor.

### 🍿 2. Media Stack (Movies, TV Shows & Subtitles)
- **Jellyfin**: Privacy-focused media streaming server with hardware GPU transcoding support (`/dev/dri`).
- **qBittorrent**: High-speed torrent downloader with Web UI.
- **Prowlarr**: Indexer manager synchronized with Sonarr/Radarr.
- **Sonarr**: Automated TV series downloader and organizer.
- **Radarr**: Automated movie downloader and organizer.
- **Bazarr**: Automatic subtitleFetcher (.srt).
- **FlareSolverr**: Cloudflare anti-bot bypass proxy for indexers.

### 🎵 3. Music Stack & StreamVault App
- **Navidrome (Multi-Instance Support)**: Subsonic-compatible music streaming servers with isolated instances for multi-user family libraries.
- **StreamVault Web Application** (Port `4535`): Custom web interface built with Flask & modern dark glassmorphism design. Features Deezer search, trending charts, preview audio player, and 1-click containerized downloading to target libraries.
- **SpotDL Web**: Spotify playlist downloader web UI.
- **Slskd**: Soulseek peer-to-peer audio downloading suite with web interface.
- **Lidarr**: Automated music collection manager.
- **Deemix CLI (Patched)**: Custom Docker container built with `patch_deezer.py` to fix edge-case Deezer metadata & tagging issues.

---

## 🌐 Network & Port Reference Table

| Service Name | Port (Host:Container) | Service Purpose |
| :--- | :---: | :--- |
| **Immich Web UI** | `2283:2283` | Photo & Video Management Dashboard |
| **Jellyfin** | `8096:8096` | Media Streaming Platform |
| **qBittorrent WebUI** | `8085:8080` | Torrent Download Manager |
| **Prowlarr** | `9696:9696` | Torrent / Usenet Indexer Manager |
| **Sonarr** | `8989:8989` | TV Shows Automation |
| **Radarr** | `7878:7878` | Movies Automation |
| **Bazarr** | `6767:6767` | Subtitle Automation |
| **FlareSolverr** | `8191:8191` | Cloudflare Bypass Proxy |
| **Navidrome (Primary)** | `4533:4533` | Music Streaming Server |
| **Navidrome (Secondary 1)**| `4536:4533` | Isolated Music Library Instance |
| **Navidrome (Secondary 2)**| `4537:4533` | Isolated Music Library Instance |
| **StreamVault Web UI** | `4535:4535` | Custom Music Discovery & Download Web App |
| **SpotDL Web UI** | `4534:4534` | Spotify Playlist Downloader |
| **Slskd (Soulseek)** | `5030:5030` | P2P Music Downloader UI |
| **Lidarr** | `8686:8686` | Music Automation Manager |

---

## 🛠️ Custom Scripts & Automation Utilities

The `music/` stack includes powerful automation tools:

- **`deezer-download.sh`**: Downloads tracks, albums, or playlists from Deezer links using the patched deemix container. Auto-resolves user profile URLs to their Loved Tracks playlist.
- **`sync-playlists.sh`**: Auto-syncs Spotify playlists listed in `config/spotdl/playlists.txt`.
- **`star_favourites.py`**: Python script that scans downloaded tracks in `Favourite tracks` folders and bulk-stars them in Navidrome's SQLite database.
- **`delsong.sh`**: Interactive CLI script to search and delete specific tracks from host storage.
- **`patch_deezer.py`**: Python script applied during Docker build to patch `deezer-python` and `deemix` library edge cases (missing lyrics, empty barcodes, etc.).

---

## ⚙️ Customization & Configuration Guide

### 1. How to Modify Storage Paths
By default, compose files mount media directories to `/mnt/hdd/media`. If your storage is located elsewhere (e.g., `/mnt/storage` or `/data/media`):
- Open `media/docker-compose.yml` or `music/docker-compose.yml`.
- Search for `/mnt/hdd/media` and replace it with your host storage path.

### 2. How to Enable / Disable Hardware Acceleration (GPU Transcoding)
- **Intel / AMD iGPU**: In `media/docker-compose.yml` under `jellyfin` and `immich/docker-compose.yml` under `immich-server`, the device `/dev/dri:/dev/dri` is passed.
- **Nvidia GPU**: To use Nvidia NVENC, install `nvidia-container-toolkit` and update the compose file to include `runtime: nvidia` under services.
- **CPU Only**: If your host does not have a compatible GPU, simply comment out or remove lines containing `/dev/dri`.

### 3. How to Enable / Disable Extra Navidrome Instances
If you only need a single music library, open `music/docker-compose.yml` and comment out or delete the `navidrome-maman` and `navidrome-roland` service blocks.

---

## 🚀 Quickstart Installation Guide

### Prerequisites
- Docker Engine >= 24.0
- Docker Compose v2
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/server-stack.git
cd server-stack
```

### Step 2: Configure Environment Files & Secrets

1. **Immich Environment Setup:**
   ```bash
   cd immich
   cp .env.example .env
   ```
   Edit `.env` and set your secure Postgres database password (`DB_PASSWORD`).

2. **Deezer ARL Cookie Setup (for Deemix):**
   ```bash
   mkdir -p music/config/deemix
   echo "YOUR_DEEZER_ARL_COOKIE" > music/config/deemix/.arl
   ```
   *(To find your ARL: Log into deezer.com in browser -> F12 -> Application -> Cookies -> `arl`)*

### Step 3: Launch Services

```bash
# 1. Start Watchtower (Root)
docker compose up -d

# 2. Start Immich Stack
cd immich && docker compose up -d && cd ..

# 3. Start Media Stack
cd media && docker compose up -d && cd ..

# 4. Start Music Stack
cd music && docker compose up -d && cd ..
```

---

## 🔐 Security & Best Practices

- **Never commit credentials**: All secrets, database passwords, and API tokens are omitted via `.gitignore`.
- **User Permissions (`PUID`/`PGID`)**: Ensure environment variables match your host user's UID and GID (`id -u` / `id -g`) to avoid permission issues on mounted volumes.
- **Reverse Proxy**: It is recommended to put these services behind a reverse proxy like **Nginx Proxy Manager**, **Traefik**, or **Cloudflare Tunnels** with SSL certificates (Let's Encrypt / HTTPS).

---

## 📄 License & Contributing

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

Contributions are welcome! Please review [`CONTRIBUTING.md`](CONTRIBUTING.md) before submitting pull requests or opening issues.
