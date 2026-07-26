#!/usr/bin/env python3
import os
import subprocess
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

MUSIC_DIR = os.getenv("MUSIC_DIR", "/mnt/hdd/media/library/music")
MUSIC_MAMAN_DIR = os.getenv("MUSIC_MAMAN_DIR", "/mnt/hdd/media/library/music_maman")
MUSIC_ROLAND_DIR = os.getenv("MUSIC_ROLAND_DIR", "/mnt/hdd/media/library/music_roland")
CONFIG_DIR = os.getenv("DEEMIX_CONFIG_DIR", "/home/thelio/server-stack/music/config/deemix")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.route("/api/trending")
def trending():
    try:
        resp = requests.get("https://api.deezer.com/chart", timeout=5).json()
        return jsonify({
            "tracks": resp.get("tracks", {}).get("data", [])[:12],
            "artists": resp.get("artists", {}).get("data", [])[:8],
            "albums": resp.get("albums", {}).get("data", [])[:8]
        })
    except Exception as e:
        app.logger.error(f"Trending error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/search")
def search():
    query = request.args.get("q", "").strip()
    search_type = request.args.get("type", "track") # track, artist, album
    if not query:
        return jsonify({"data": []})

    try:
        if search_type == "artist":
            url = f"https://api.deezer.com/search/artist?q={query}&limit=24"
        elif search_type == "album":
            url = f"https://api.deezer.com/search/album?q={query}&limit=24"
        else:
            url = f"https://api.deezer.com/search/track?q={query}&limit=30"
        
        resp = requests.get(url, timeout=5).json()
        return jsonify(resp)
    except Exception as e:
        app.logger.error(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/artist/<artist_id>")
def get_artist(artist_id):
    try:
        info = requests.get(f"https://api.deezer.com/artist/{artist_id}", timeout=5).json()
        top = requests.get(f"https://api.deezer.com/artist/{artist_id}/top?limit=25", timeout=5).json()
        albums = requests.get(f"https://api.deezer.com/artist/{artist_id}/albums?limit=25", timeout=5).json()
        return jsonify({
            "artist": info,
            "top_tracks": top.get("data", []),
            "albums": albums.get("data", [])
        })
    except Exception as e:
        app.logger.error(f"Artist error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/album/<album_id>")
def get_album(album_id):
    try:
        album_info = requests.get(f"https://api.deezer.com/album/{album_id}", timeout=5).json()
        return jsonify(album_info)
    except Exception as e:
        app.logger.error(f"Album error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/download", methods=["POST"])
def download():
    data = request.json or {}
    target_url = data.get("url", "").strip()
    title = data.get("title", "Musique")
    target_dest = data.get("target", "maman") # 'maman', 'roland', or 'thelio'

    if not target_url:
        return jsonify({"error": "URL manquante"}), 400

    if target_dest == "roland":
        music_dest = MUSIC_ROLAND_DIR
        dest_label = "Bibliothèque Roland"
    elif target_dest == "maman":
        music_dest = MUSIC_MAMAN_DIR
        dest_label = "Bibliothèque Maman"
    else:
        music_dest = MUSIC_DIR
        dest_label = "Bibliothèque Thélio"

    try:
        docker_bin = "/usr/bin/docker" if os.path.exists("/usr/bin/docker") else "docker"
        cmd = [
            docker_bin, "run", "--rm", "-d",
            "-v", f"{music_dest}:/music",
            "-v", f"{CONFIG_DIR}:/root/.config/deemix",
            "deemix-local", "-p", "/music", target_url
        ]
        app.logger.info(f"Running command: {' '.join(cmd)}")
        subprocess.Popen(cmd)
        return jsonify({"status": "ok", "message": f"Téléchargement lancé pour : {title} → {dest_label}"})
    except Exception as e:
        app.logger.error(f"Download exception: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4535, debug=False)
