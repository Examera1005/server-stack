# 🎵 StreamVault + Navidrome — Kit Autonome Clé en Main

Ce dépôt contient **tout le nécessaire** pour installer ton propre serveur de streaming musical (**Navidrome**) couplé à **StreamVault** (recherche, écoute d'extraits 30s, téléchargement en 1 clic, historique & gestion de bibliothèque), **100 % indépendant** et prêt à être utilisé sur **iPhone** / Android / PC.

---

## ⚡ 1. Installation en Copier-Coller (Serveur / PC / Raspberry Pi / NAS)

### Pré-requis : Installer Docker (si ce n'est pas déjà fait)
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

### Lancer StreamVault + Navidrome
Copie-colle simplement ces commandes dans le terminal :

```bash
git clone <URL_DE_CE_REPO> streamvault
cd streamvault
cp .env.example .env
docker compose up -d --build
```
*(Si tu copies le dossier directement via clé USB / AirDrop / SCP sans Git, fais juste `cd streamvault && docker compose up -d --build`)*

C'est tout ! Les 2 services tournent maintenant :
- **StreamVault (Ajouter & Gérer la musique)** : `http://IP_DU_SERVEUR:4535`
- **Navidrome (Serveur de streaming audio)** : `http://IP_DU_SERVEUR:4533`

*(Pour connaître l'IP locale du serveur, tape `hostname -I | awk '{print $1}'` dans le terminal).*

---

## 🔑 2. Activer le téléchargement Haute Qualité Deezer (Optionnel)

Par défaut, **StreamVault fonctionne immédiatement sans configuration** grâce au fallback automatique **SpotDL**.
Pour télécharger directement via **Deemix** (plus rapide, tags complets et FLAC/MP3 320kbps) :

1. Connecte-toi à [deezer.com](https://www.deezer.com) sur un navigateur (même un compte gratuit suffit).
2. Ouvre les outils de développement (`F12` → onglet **Application** ou **Stockage** → **Cookies** → `https://www.deezer.com`).
3. Copie la valeur du cookie nommé **`arl`**.
4. Colle-la dans le fichier `config/deemix/.arl` avec cette commande :

```bash
echo "COLLE_TON_COOKIE_ARL_ICI" > config/deemix/.arl
```
*(Aucun redémarrage nécessaire, StreamVault l'utilise instantanément).*

---

## 📱 3. Configuration sur iPhone (WebApp + Lecteur Musical)

### Étape A : Créer son compte sur Navidrome
1. Ouvre **`http://IP_DU_SERVEUR:4533`** dans ton navigateur.
2. Choisis un **identifiant** et un **mot de passe** administrateur (c'est la seule fois où tu auras besoin de le faire).

### Étape B : Mettre l'application **StreamVault** sur l'écran d'accueil de l'iPhone
StreamVault intègre une WebApp native iOS (icône dédiée, plein écran sans barre Safari) :
1. Sur l'iPhone, ouvre **Safari** et va sur **`http://IP_DU_SERVEUR:4535`**.
2. Appuie sur le bouton **Partager** (le carré avec la flèche vers le haut en bas de l'écran).
3. Fais défiler et appuie sur **« Sur l'écran d'accueil »** → **Ajouter**.
4. L'application **StreamVault** apparaît sur ton iPhone comme une vraie appli pour chercher et ajouter n'importe quel son ou album en 1 clic !

### Étape C : Installer l'application de lecture sur l'iPhone (Style Spotify / Apple Music)
Pour écouter ta musique hors-ligne, en voiture (CarPlay) et en arrière-plan sur iPhone, télécharge l'une de ces applications gratuites sur l'**App Store** :
- 🏆 **Amperfy** *(100 % Gratuit, Open-Source, mode hors-ligne, CarPlay)*
- 🎵 **Substreamer** *(Gratuit, interface moderne)*
- 🎶 **Arpeggi** ou **play:Sub** *(Alternatives populaires)*

Dans l'application choisie sur l'iPhone, entre simplement :
- **Adresse du serveur (Server URL)** : `http://IP_DU_SERVEUR:4533`
- **Utilisateur / Mot de passe** : Ceux créés à l'Étape A
- *(Si demandé, activer "Subsonic API" / "Plaintext password" ou connexion standard).*

---

## 🌍 4. Écouter et ajouter de la musique hors de chez soi (4G / 5G) en 2 minutes

Pour que tout marche partout (en 4G/5G hors du Wi-Fi de la maison) **sans ouvrir de ports sur la box internet** :

1. Sur le serveur, installe **Tailscale** :
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   ```
2. Récupère l'adresse IP Tailscale du serveur (qui commence par `100.x.y.z`) :
   ```bash
   tailscale ip -4
   ```
3. Sur l'iPhone, télécharge l'app **Tailscale** sur l'App Store et connecte-toi au même compte.
4. Utilise l'adresse `http://100.x.y.z:4535` (StreamVault) et `http://100.x.y.z:4533` (Amperfy / Navidrome) : ça fonctionnera partout dans le monde comme à la maison !

---

## 🛠️ Commandes Utiles

```bash
# Voir les logs en direct
docker compose logs -f

# Redémarrer les services
docker compose restart

# Mettre à jour les conteneurs
docker compose pull && docker compose up -d --build
```
