#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "🎵 Installation Automatique : StreamVault + Navidrome"
echo "=========================================================="

# 1. Vérifier que Docker tourne
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Docker n'est pas installé. Installe OrbStack (https://orbstack.dev) puis relance cette commande."
    exit 1
fi

if ! docker info >/dev/null 2>&1; then
    echo "🚀 Démarrage d'OrbStack / Docker..."
    if [ "$(uname -s)" = "Darwin" ]; then
        open -a OrbStack 2>/dev/null || open -a Docker 2>/dev/null || true
        sleep 5
    fi
fi

# 2. Nettoyer les éventuels conteneurs nginx créés par erreur
NGINX_CONTAINERS=$(docker ps -aq --filter "ancestor=nginx" 2>/dev/null || true)
if [ -n "$NGINX_CONTAINERS" ]; then
    echo "🧹 Suppression des conteneurs nginx parasites..."
    docker rm -f $NGINX_CONTAINERS >/dev/null 2>&1 || true
fi

# 3. Cloner ou mettre à jour le vrai dossier ~/streamvault
INSTALL_DIR="$HOME/streamvault"
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "🔄 Mise à jour de $INSTALL_DIR..."
    cd "$INSTALL_DIR"
    git fetch origin streamvault
    git reset --hard origin/streamvault
else
    echo "📥 Téléchargement de StreamVault dans $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
    git clone -b streamvault https://github.com/Examera1005/server-stack.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

cp -n .env.example .env 2>/dev/null || cp .env.example .env

# 4. Lancer les conteneurs Navidrome (4533) et StreamVault (4535)
echo "🐳 Construction et démarrage de Navidrome + StreamVault..."
docker compose up -d --build

echo "⏳ Vérification du démarrage des services..."
sleep 3
docker compose ps

echo ""
echo "✅ Navidrome et StreamVault sont lancés en local :"
echo "   🎧 Navidrome   : http://localhost:4533"
echo "   ⚡ StreamVault : http://localhost:4535"

if [ "$(uname -s)" = "Darwin" ]; then
    open "http://localhost:4533" "http://localhost:4535" 2>/dev/null || true
fi

echo ""
echo "🌐 Lancement de la configuration HTTPS (Tailscale Funnel)..."
chmod +x ./setup-funnel.sh
./setup-funnel.sh
