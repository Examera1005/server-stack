# 🎵 StreamVault + Navidrome — Kit Autonome Clé en Main (HTTPS via Tailscale Funnel)

Ce dépôt contient **tout le nécessaire** pour installer ton propre serveur de streaming musical (**Navidrome**) couplé à **StreamVault** (recherche, extraits 30s, téléchargement en 1 clic, historique & gestion de bibliothèque), **protégé par le compte Navidrome** et accessible partout en **HTTPS** sur iPhone **sans installer de VPN sur le téléphone** (zéro impact sur la batterie).

---

## ⚡ 1. Installation en Copier-Coller (sur le Serveur / PC / Raspberry Pi)

### Pré-requis : Installer Docker (si ce n'est pas déjà fait)
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

### Lancer StreamVault + Navidrome
```bash
git clone <URL_DE_CE_REPO> streamvault
cd streamvault
cp .env.example .env
docker compose up -d --build
```

---

## 🌍 2. Activer le HTTPS Public (Tailscale Funnel — Zéro VPN sur l'iPhone)

Tailscale tourne **uniquement sur le serveur** pour fournir un domaine `https://...ts.net` gratuit avec certificat SSL automatique (sans ouvrir de port sur la box internet, et **sans installer Tailscale sur l'iPhone**) :

1. Dans ta console d'administration Tailscale ([login.tailscale.com/admin/dns](https://login.tailscale.com/admin/dns)), active **MagicDNS** et **HTTPS Certificates**, puis dans **Access Controls** autorise `funnel`.
2. Lance le script automatique sur le serveur :

```bash
chmod +x setup-funnel.sh
./setup-funnel.sh
```

Le script affiche tes 2 adresses HTTPS prêtes à l'emploi :
- 🎧 **Navidrome** : `https://nom-du-serveur.tailxxxx.ts.net` *(Port 443)*
- ⚡ **StreamVault** : `https://nom-du-serveur.tailxxxx.ts.net:8443` *(Port 8443)*

---

## 📱 3. Configuration sur l'iPhone (en 2 minutes)

### Étape A : Créer son compte sur Navidrome (1 seule fois)
1. Ouvre **`https://nom-du-serveur.tailxxxx.ts.net`** (ou `http://IP_LOCALE:4533`).
2. Crée ton **identifiant** et ton **mot de passe** administrateur.
*(Ce même identifiant et mot de passe déverrouille automatiquement **StreamVault** !)*

### Étape B : Ajouter l'application **StreamVault** sur l'écran d'accueil iPhone
1. Sur l'iPhone, ouvre **Safari** et va sur **`https://nom-du-serveur.tailxxxx.ts.net:8443`**.
2. Appuie sur le bouton **Partager** (carré avec flèche vers le haut) → **« Sur l'écran d'accueil »** → **Ajouter**.
3. Ouvre l'application **StreamVault** depuis ton écran d'accueil et connecte-toi avec ton identifiant/mot de passe Navidrome (la session reste active 90 jours).

### Étape C : Installer le lecteur musical sur l'iPhone (Style Spotify / Apple Music)
Télécharge l'une de ces applications gratuites sur l'**App Store** pour écouter ta musique hors-ligne, en arrière-plan et sur CarPlay :
- 🏆 **Amperfy** *(100 % Gratuit, Open-Source, cache hors-ligne, CarPlay)*
- 🎵 **Substreamer** *(Gratuit, interface moderne)*
- 🎶 **Arpeggi** ou **play:Sub**

Dans l'application sur l'iPhone, entre :
- **Adresse du serveur** : `https://nom-du-serveur.tailxxxx.ts.net`
- **Utilisateur / Mot de passe** : Ceux créés à l'Étape A.

---

## 🔑 4. Activer le téléchargement Haute Qualité Deezer (Optionnel)

Par défaut, **StreamVault fonctionne immédiatement** grâce au fallback **SpotDL**.
Pour télécharger directement via **Deemix** (FLAC / MP3 320kbps + tags complets) :
1. Connecte-toi sur [deezer.com](https://www.deezer.com) sur un navigateur (`F12` → **Application/Stockage** → **Cookies** → copie la valeur de **`arl`**).
2. Colle-la sur le serveur :
```bash
echo "COLLE_TON_COOKIE_ARL_ICI" > config/deemix/.arl
```

---

## 🛠️ Commandes Utiles

```bash
# Voir les logs en direct
docker compose logs -f

# Vérifier le statut du Funnel HTTPS
sudo tailscale funnel status

# Mettre à jour
docker compose pull && docker compose up -d --build
```
