#!/usr/bin/env bash
# ==============================================================================
# Script de Suppression de Musique de la Bibliothèque Navidrome
# ==============================================================================

MUSIC_DIR="${MUSIC_DIR:-/mnt/hdd/media/library/music}"

if [ "$#" -eq 0 ]; then
    echo "Usage: ./delsong.sh <Nom_du_morceau_ou_artiste>"
    exit 1
fi

QUERY="$1"
echo "Recherche des morceaux correspondant à '$QUERY'..."
echo ""

mapfile -t FILES < <(find "$MUSIC_DIR" -type f -iname "*${QUERY}*")

if [ "${#FILES[@]}" -eq 0 ]; then
    echo "Aucun morceau trouvé correspondant à '$QUERY'."
    exit 0
fi

echo "Fichiers trouvés :"
for f in "${FILES[@]}"; do
    echo " - $f"
    rm -f "$f"
    echo "   -> Supprimé !"
done

echo ""
echo "Suppression terminée. Navidrome met à jour la bibliothèque automatiquement !"
