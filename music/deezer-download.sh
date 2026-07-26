#!/usr/bin/env bash
# ==============================================================================
# Script de Téléchargement Deezer (Favoris, Playlists, Albums, Titres)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MUSIC_DIR="${MUSIC_DIR:-/mnt/hdd/media/library/music}"
CONFIG_DIR="${SCRIPT_DIR}/config/deemix"
ARL_FILE="$CONFIG_DIR/.arl"

mkdir -p "$MUSIC_DIR" "$CONFIG_DIR"

if [ ! -f "$ARL_FILE" ] || [ ! -s "$ARL_FILE" ]; then
    echo "Fichier ARL non trouvé."
    echo "Veuillez mettre votre cookie ARL Deezer dans le fichier :"
    echo "  $ARL_FILE"
    echo ""
    echo "Pour obtenir votre ARL :"
    echo "1. Connectez-vous sur deezer.com sur votre navigateur."
    echo "2. Appuyez sur F12 -> Application/Stockage -> Cookies -> deezer.com."
    echo "3. Copiez la valeur du cookie nommé 'arl'."
    echo "4. Exécutez : echo 'VOTRE_ARL' > $ARL_FILE"
    exit 1
fi

ARL=$(cat "$ARL_FILE" | tr -d '\r\n ')

if [ -z "$ARL" ]; then
    echo "Le fichier $ARL_FILE est vide. Veuillez y placer votre token ARL Deezer."
    exit 1
fi

if [ "$#" -eq 0 ]; then
    echo "Usage: ./deezer-download.sh <URL_DEEZER_1> [URL_DEEZER_2 ...]"
    echo "Exemples :"
    echo "  ./deezer-download.sh 'https://www.deezer.com/fr/track/90305559'"
    echo "  ./deezer-download.sh 'https://www.deezer.com/fr/playlist/9167387942'  # Coups de cœur"
    echo "  ./deezer-download.sh 'https://www.deezer.com/fr/profile/4430371162/loved'"
    exit 1
fi

for raw_url in "$@"; do
    # Résolution automatique des URLs de profil vers leur playlist Coups de Cœur
    RESOLVED_URL=$(docker run --rm --entrypoint python deemix-local -c "
import sys, re, requests
url = sys.argv[1]
match = re.search(r'/profile/(\d+)', url)
if match:
    user_id = match.group(1)
    try:
        r = requests.get(f'https://api.deezer.com/user/{user_id}/playlists', timeout=5).json()
        for pl in r.get('data', []):
            if pl.get('is_loved_track'):
                print(f'https://www.deezer.com/fr/playlist/{pl.get(\"id\")}')
                sys.exit(0)
    except Exception:
        pass
print(url)
" "$raw_url")

    echo "[Deezer] Téléchargement de : $RESOLVED_URL"
    docker run --rm \
      -v "$MUSIC_DIR:/music" \
      -v "$CONFIG_DIR:/root/.config/deemix" \
      deemix-local \
      -p /music \
      "$RESOLVED_URL"
done

echo "[Deezer] Téléchargement terminé !"
