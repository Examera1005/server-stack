#!/usr/bin/env python3
import os
import sqlite3
import datetime

# Path to Navidrome SQLite database & target user
DB_PATH = os.getenv("NAVIDROME_DB_PATH", "./config/navidrome/navidrome.db")
USERNAME = os.getenv("NAVIDROME_USER", "admin")

def star_all_favourites():
    if not os.path.exists(DB_PATH):
        print(f"Base de données non trouvée à l'emplacement : {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Obtenir l'ID de l'utilisateur
    cursor.execute("SELECT id FROM user WHERE user_name = ?;", (USERNAME,))
    user_row = cursor.fetchone()
    if not user_row:
        print(f"Utilisateur '{USERNAME}' non trouvé dans la base de données Navidrome.")
        conn.close()
        return

    user_id = user_row[0]

    # 2. Récupérer tous les fichiers de la playlist Favourite tracks
    cursor.execute("SELECT id FROM media_file WHERE path LIKE '%Favourite tracks%';")
    track_ids = [row[0] for row in cursor.fetchall()]

    print(f"Nombre de morceaux trouvés : {len(track_ids)}")

    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

    starred_count = 0
    for track_id in track_ids:
        cursor.execute("SELECT starred FROM annotation WHERE user_id = ? AND item_id = ? AND item_type = 'media_file';", (user_id, track_id))
        existing = cursor.fetchone()

        if existing is None:
            cursor.execute(
                "INSERT INTO annotation (user_id, item_id, item_type, play_count, rating, starred, starred_at) VALUES (?, ?, 'media_file', 0, 0, 1, ?);",
                (user_id, track_id, now_str)
            )
            starred_count += 1
        elif existing[0] != 1:
            cursor.execute(
                "UPDATE annotation SET starred = 1, starred_at = ? WHERE user_id = ? AND item_id = ? AND item_type = 'media_file';",
                (now_str, user_id, track_id)
            )
            starred_count += 1

    conn.commit()
    conn.close()

    print(f"✅ {starred_count} nouveaux morceaux ont été marqués comme Favoris ❤️ dans Navidrome !")

if __name__ == "__main__":
    star_all_favourites()
