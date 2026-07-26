#!/usr/bin/env bash
# ==============================================================================
# Script de Synchronisation Automatique de Playlists Spotify -> Navidrome
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MUSIC_DIR="${MUSIC_DIR:-/mnt/hdd/media/library/music}"
PLAYLISTS_FILE="${SCRIPT_DIR}/config/spotdl/playlists.txt"
OUTPUT_FORMAT="/music/{artist}/{album}/{artist} - {title}.{output-ext}"

mkdir -p "$MUSIC_DIR" "$(dirname "$PLAYLISTS_FILE")"

# Si des arguments sont passés, on les télécharge directement. Sinon, on lit le fichier playlists.txt
if [ "$#" -gt 0 ]; then
    URLS=("$@")
else
    if [ ! -f "$PLAYLISTS_FILE" ]; then
        echo "# Ajoutez vos URLs de playlists Spotify ici (une par ligne) :" > "$PLAYLISTS_FILE"
        echo "# https://open.spotify.com/playlist/..." >> "$PLAYLISTS_FILE"
        echo "Fichier $PLAYLISTS_FILE créé. Ajoutez vos liens dedans."
        exit 0
    fi
    mapfile -t URLS < <(grep -v '^#' "$PLAYLISTS_FILE" | grep -v '^$')
fi

if [ "${#URLS[@]}" -eq 0 ]; then
    echo "Aucune URL à synchroniser."
    exit 0
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Début de la synchronisation de ${#URLS[@]} playlist(s)..."

for url in "${URLS[@]}"; do
    echo "Processing: $url"
    docker run --rm \
      -v "$MUSIC_DIR:/music" \
      spotdl/spotify-downloader \
      download "$url" \
      --output "$OUTPUT_FORMAT" \
      --scan-for-songs \
      --overwrite skip
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Synchronisation terminée avec succès !"
