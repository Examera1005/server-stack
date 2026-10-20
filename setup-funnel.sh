#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "🌐 Configuration de Tailscale Funnel (HTTPS sans VPN iPhone)"
echo "=========================================================="

OS="$(uname -s)"
TS_CMD="tailscale"
SUDO="sudo"

if [ "$OS" = "Darwin" ]; then
    # Support macOS (Homebrew Cask / App Store / CLI)
    SUDO=""
    if command -v tailscale >/dev/null 2>&1; then
        TS_CMD="tailscale"
    elif [ -x "/Applications/Tailscale.app/Contents/MacOS/Tailscale" ]; then
        TS_CMD="/Applications/Tailscale.app/Contents/MacOS/Tailscale"
    else
        echo "📦 Installation de Tailscale sur macOS..."
        if command -v brew >/dev/null 2>&1; then
            brew install --cask tailscale
            open -a Tailscale
            sleep 3
            TS_CMD="/Applications/Tailscale.app/Contents/MacOS/Tailscale"
        else
            echo "⚠️ Veuillez installer Tailscale depuis https://tailscale.com/download/mac puis relancer ce script."
            exit 1
        fi
    fi
else
    # Support Linux (Debian, Ubuntu, Raspberry Pi, etc.)
    if ! command -v tailscale >/dev/null 2>&1; then
        echo "📦 Installation de Tailscale sur Linux..."
        curl -fsSL https://tailscale.com/install.sh | sh
    fi
fi

if ! "$TS_CMD" status >/dev/null 2>&1; then
    echo "🔑 Connexion du serveur à Tailscale..."
    $SUDO "$TS_CMD" up
fi

echo "🚀 Activation du Funnel HTTPS pour Navidrome (Port 443 -> 4533)..."
$SUDO "$TS_CMD" funnel --bg --https=443 http://127.0.0.1:4533

echo "🚀 Activation du Funnel HTTPS pour StreamVault (Port 8443 -> 4535)..."
$SUDO "$TS_CMD" funnel --bg --https=8443 http://127.0.0.1:4535

DNS_NAME=$("$TS_CMD" status --json | python3 -c "import sys,json; print(json.load(sys.stdin).get('Self',{}).get('DNSName','').rstrip('.'))" 2>/dev/null || true)

echo ""
echo "✅ Tailscale Funnel est actif !"
if [ -n "$DNS_NAME" ]; then
    echo "----------------------------------------------------------"
    echo "🎧 URL Navidrome (App iPhone)  : https://${DNS_NAME}"
    echo "⚡ URL StreamVault (WebApp iOS): https://${DNS_NAME}:8443"
    echo "----------------------------------------------------------"
else
    $SUDO "$TS_CMD" funnel status
fi
echo "📱 Aucune application VPN n'est requise sur l'iPhone (0 batterie consommée) !"
