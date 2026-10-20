# 🎵 StreamVault + Navidrome — Kit Autonome Clé en Main (Linux & macOS)

Ce dépôt contient **tout le nécessaire** pour installer ton propre serveur de streaming musical (**Navidrome**) couplé à **StreamVault** (recherche, écoute d'extraits 30s, téléchargement de titres et d'albums en 1 clic, historique & gestion de bibliothèque) :
- **Compatible Linux & macOS (Intel et Apple Silicon M1/M2/M3/M4)**.
- **Zéro compte externe / Zéro cookie `.arl` requis** : fonctionne immédiatement dès l'installation.
- **Authentification unique (SSO)** : StreamVault est protégé par ton compte Navidrome.
- **Accès HTTPS partout (4G/5G) sans VPN sur l'iPhone** : grâce à Tailscale Funnel côté serveur uniquement (0 % de batterie consommée sur le téléphone).

---

## ⚡ 1. Installation en Copier-Coller (macOS / Linux / Raspberry Pi)

### Pré-requis : Installer Docker (si ce n'est pas déjà fait)
- **Sur macOS** :
  ```bash
  brew install --cask orbstack && open -a OrbStack
  ```
  *(ou installe [OrbStack](https://orbstack.dev) / [Docker Desktop](https://www.docker.com/products/docker-desktop/)).*
- **Sur Linux** :
  ```bash
  curl -fsSL https://get.docker.com | sh
  sudo usermod -aG docker $USER
  newgrp docker
  ```

### Cloner et lancer StreamVault + Navidrome
```bash
git clone -b streamvault https://github.com/Examera1005/server-stack.git streamvault
cd streamvault
cp .env.example .env
docker compose up -d --build
```

---

## 🌍 2. Activer le HTTPS Public (Tailscale Funnel — Zéro VPN sur l'iPhone)

Tailscale tourne **uniquement sur le Mac / serveur Linux** pour fournir un domaine `https://...ts.net` gratuit avec certificat SSL automatique (sans ouvrir de port sur la box internet, et **sans installer Tailscale sur l'iPhone**) :

1. Dans ta console Tailscale ([login.tailscale.com/admin/dns](https://login.tailscale.com/admin/dns)), active **MagicDNS** et **HTTPS Certificates**, puis autorise **Funnel** lorsque le terminal te le propose.
2. Lance le script automatique (qui installe aussi Tailscale automatiquement sur Linux et macOS) :

```bash
./setup-funnel.sh
```

Le script affiche tes 2 adresses HTTPS prêtes à l'emploi :
- 🎧 **Navidrome** : `https://nom-du-serveur.tailxxxx.ts.net` *(Port 443)*
- ⚡ **StreamVault** : `https://nom-du-serveur.tailxxxx.ts.net:8443` *(Port 8443)*

---

## 📱 3. Configuration sur l'iPhone (en 2 minutes)

### Étape A : Créer son compte sur Navidrome (1 seule fois)
1. Ouvre **`https://nom-du-serveur.tailxxxx.ts.net`** (ou `http://localhost:4533`).
2. Crée ton **identifiant** et ton **mot de passe** administrateur.
*(Ce même identifiant et mot de passe déverrouille automatiquement **StreamVault** !)*

### Étape B : Ajouter l'application **StreamVault** sur l'écran d'accueil iPhone
1. Sur l'iPhone, ouvre **Safari** et va sur **`https://nom-du-serveur.tailxxxx.ts.net:8443`**.
2. Appuie sur le bouton **Partager** (carré avec flèche vers le haut) → **« Sur l'écran d'accueil »** → **Ajouter**.
3. Ouvre **StreamVault** depuis ton écran d'accueil et connecte-toi avec ton identifiant/mot de passe Navidrome (la session reste active 90 jours).

### Étape C : Installer le lecteur musical sur l'iPhone (Style Spotify / Apple Music)
Télécharge l'une de ces applications gratuites sur l'**App Store** pour écouter ta musique hors-ligne, en arrière-plan et sur CarPlay :
- 🏆 **Amperfy** *(100 % Gratuit, Open-Source, cache hors-ligne, CarPlay)*
- 🎵 **Substreamer** *(Gratuit, interface moderne)*
- 🎶 **Arpeggi** ou **play:Sub**

Dans l'application sur l'iPhone, entre :
- **Adresse du serveur** : `https://nom-du-serveur.tailxxxx.ts.net`
- **Utilisateur / Mot de passe** : Ceux créés à l'Étape A.

---

## 🛠️ Commandes Utiles

```bash
# Voir les logs en direct
docker compose logs -f

# Redémarrer les services
docker compose restart

# Mettre à jour
docker compose pull && docker compose up -d --build
```
