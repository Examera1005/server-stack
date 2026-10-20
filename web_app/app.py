#!/usr/bin/env python3
import os
import re
import secrets
import shutil
import sqlite3
import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse
import requests
from flask import (
    Flask, render_template, request, jsonify,
    make_response, send_from_directory, session, redirect, url_for
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max payload
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=90)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

MUSIC_DIR = os.getenv("MUSIC_DIR", "/music")
CONFIG_DIR = os.getenv("DEEMIX_CONFIG_DIR", "/root/.config/deemix")
NAVIDROME_PORT = os.getenv("NAVIDROME_PORT", "4533")
NAVIDROME_INTERNAL_URL = os.getenv("NAVIDROME_INTERNAL_URL", "http://navidrome:4533").rstrip("/")
DATA_DIR = "/data" if os.path.isdir("/data") else os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DATA_DIR, "history.db")
SECRET_KEY_FILE = os.path.join(DATA_DIR, ".secret_key")

# Cached Subsonic credentials to trigger instant Navidrome scans over HTTP
_SCAN_AUTH = {}

def load_or_create_secret_key():
    env_key = os.getenv("SECRET_KEY")
    if env_key:
        return env_key
    try:
        if os.path.isfile(SECRET_KEY_FILE):
            with open(SECRET_KEY_FILE, "r") as f:
                key = f.read().strip()
                if len(key) >= 32:
                    return key
        key = secrets.token_hex(32)
        with open(SECRET_KEY_FILE, "w") as f:
            f.write(key)
        return key
    except Exception:
        return secrets.token_hex(32)

app.secret_key = load_or_create_secret_key()

_LOGIN_ATTEMPTS = {}
MAX_LOGIN_ATTEMPTS = 6
LOGIN_WINDOW_SECONDS = 60

def is_rate_limited(ip):
    now = time.time()
    attempts = [t for t in _LOGIN_ATTEMPTS.get(ip, []) if now - t < LOGIN_WINDOW_SECONDS]
    _LOGIN_ATTEMPTS[ip] = attempts
    return len(attempts) >= MAX_LOGIN_ATTEMPTS

def record_failed_attempt(ip):
    now = time.time()
    _LOGIN_ATTEMPTS.setdefault(ip, []).append(now)

def verify_navidrome_credentials(username, password):
    if not username or not password:
        return None
    try:
        resp = requests.post(
            f"{NAVIDROME_INTERNAL_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=5
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get("subsonicToken") and data.get("subsonicSalt"):
                _SCAN_AUTH["u"] = data.get("username") or username
                _SCAN_AUTH["t"] = data["subsonicToken"]
                _SCAN_AUTH["s"] = data["subsonicSalt"]
            return data.get("name") or data.get("username") or username
    except Exception as e:
        app.logger.error(f"Navidrome auth check error: {e}")
    return None

TARGET_CONFIG = {
    "main": {"dir": MUSIC_DIR, "label": "Bibliothèque Navidrome"}
}

VALID_TARGETS = set(TARGET_CONFIG.keys())
VALID_STATUSES = {"downloading", "completed", "failed"}
VALID_ITEM_TYPES = {"track", "album", "artist", "custom"}
VALID_SEARCH_TYPES = {"track", "artist", "album"}
ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.flac', '.m4a', '.ogg', '.wav', '.opus', '.aac'}
PUBLIC_PATHS = {'/login', '/favicon.ico', '/manifest.json', '/apple-touch-icon.png', '/apple-touch-icon-precomposed.png'}

@app.before_request
def require_auth():
    path = request.path
    if path in PUBLIC_PATHS or path.startswith('/static/'):
        return None
    if not session.get("user"):
        if path.startswith('/api/'):
            return jsonify({"error": "Non authentifié", "auth_required": True}), 401
        return redirect(url_for("login"))
    return None

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user"):
        return redirect(url_for("index"))

    error = None
    if request.method == "POST":
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
        if is_rate_limited(client_ip):
            error = "Trop de tentatives. Veuillez patienter 1 minute."
        else:
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            display_name = verify_navidrome_credentials(username, password)
            if display_name:
                session.clear()
                session.permanent = True
                session["user"] = display_name
                _LOGIN_ATTEMPTS.pop(client_ip, None)
                return redirect(url_for("index"))
            else:
                record_failed_attempt(client_ip)
                error = "Identifiant ou mot de passe Navidrome incorrect."

    return render_template("login.html", error=error, navidrome_port=NAVIDROME_PORT)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

def is_valid_url(url):
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if len(url) > 2048 or url.startswith("-"):
        return False
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False

def sanitize_string(val, max_len=255):
    if not val or not isinstance(val, str):
        return ""
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', val).strip()
    return cleaned[:max_len]

def safe_filename(val):
    cleaned = re.sub(r'[\\/:*?"<>|\x00-\x1f]', '_', (val or '').strip())
    return cleaned[:120] or "Unknown"

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        with get_db() as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA busy_timeout=5000;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT DEFAULT '',
                    cover_url TEXT DEFAULT '',
                    url TEXT NOT NULL,
                    target TEXT NOT NULL,
                    item_type TEXT DEFAULT 'track',
                    status TEXT NOT NULL DEFAULT 'downloading',
                    error_message TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_history_target ON history(target);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_history_status ON history(status);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_history_created_at ON history(created_at);")
            conn.commit()
    except Exception as e:
        app.logger.error(f"DB Init error: {e}")

init_db()

def prune_old_history(max_records=1000):
    try:
        with get_db() as conn:
            conn.execute("""
                DELETE FROM history 
                WHERE id NOT IN (
                    SELECT id FROM history ORDER BY id DESC LIMIT ?
                )
            """, (max_records,))
            conn.commit()
    except Exception as e:
        app.logger.warning(f"History pruning error: {e}")

def add_history_entry(title, artist, cover_url, url, target="main", item_type="track", status="downloading"):
    title = sanitize_string(title, 255) or "Musique"
    artist = sanitize_string(artist, 255)
    cover_url = cover_url.strip()[:1024] if is_valid_url(cover_url) else ""
    url = url.strip()[:2048]
    target = "main"
    item_type = item_type if item_type in VALID_ITEM_TYPES else "track"
    status = status if status in VALID_STATUSES else "downloading"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO history (title, artist, cover_url, url, target, item_type, status, error_message, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, '', ?, ?)
        """, (title, artist, cover_url, url, target, item_type, status, now, now))
        conn.commit()
        entry_id = cur.lastrowid

    prune_old_history()
    return entry_id

def update_history_status(entry_id, status, error_message=""):
    if not isinstance(entry_id, int) or entry_id <= 0:
        return
    status = status if status in VALID_STATUSES else "failed"
    error_message = sanitize_string(error_message, 500)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        conn.execute("""
            UPDATE history
            SET status = ?, error_message = ?, updated_at = ?
            WHERE id = ?
        """, (status, error_message, now, entry_id))
        conn.commit()

def get_history_entries(target=None, status=None, limit=100):
    limit = max(1, min(int(limit), 200))
    query = "SELECT id, title, artist, cover_url, url, target, item_type, status, error_message, created_at, updated_at FROM history WHERE 1=1"
    params = []
    if status and status in VALID_STATUSES:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

def delete_history_entry(entry_id):
    if not isinstance(entry_id, int) or entry_id <= 0:
        return
    with get_db() as conn:
        conn.execute("DELETE FROM history WHERE id = ?", (entry_id,))
        conn.commit()

def clear_all_history():
    with get_db() as conn:
        conn.execute("DELETE FROM history")
        conn.commit()

def trigger_navidrome_scan(target_dest="main"):
    if _SCAN_AUTH.get("u") and _SCAN_AUTH.get("t") and _SCAN_AUTH.get("s"):
        try:
            requests.get(
                f"{NAVIDROME_INTERNAL_URL}/rest/startScan.view",
                params={
                    "u": _SCAN_AUTH["u"],
                    "t": _SCAN_AUTH["t"],
                    "s": _SCAN_AUTH["s"],
                    "v": "1.16.1",
                    "c": "StreamVault",
                    "f": "json"
                },
                timeout=5
            )
            app.logger.info("Navidrome scan triggered via Subsonic HTTP API")
        except Exception as e:
            app.logger.warning(f"Navidrome auto-scan will handle update ({e})")

@app.after_request
def apply_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

@app.route("/")
def index():
    resp = make_response(render_template("index.html", navidrome_port=NAVIDROME_PORT, current_user=session.get("user", "")))
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp

@app.route("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicon-32x32.png")

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
        return jsonify({"error": "Erreur lors du chargement des tendances"}), 500

@app.route("/api/search")
def search():
    query = sanitize_string(request.args.get("q", ""), 150)
    search_type = request.args.get("type", "track")
    if search_type not in VALID_SEARCH_TYPES:
        search_type = "track"

    if not query:
        return jsonify({"data": []})

    try:
        if search_type == "artist":
            url = "https://api.deezer.com/search/artist"
        elif search_type == "album":
            url = "https://api.deezer.com/search/album"
        else:
            url = "https://api.deezer.com/search/track"
        
        resp = requests.get(url, params={"q": query, "limit": 30}, timeout=5).json()
        return jsonify(resp)
    except Exception as e:
        app.logger.error(f"Search error: {e}")
        return jsonify({"error": "Erreur lors de la recherche"}), 500

@app.route("/api/artist/<artist_id>")
def get_artist(artist_id):
    if not artist_id or not re.match(r'^\d+$', str(artist_id)):
        return jsonify({"error": "Identifiant artiste invalide"}), 400

    try:
        info = requests.get(f"https://api.deezer.com/artist/{artist_id}", timeout=5).json()
        top = requests.get(f"https://api.deezer.com/artist/{artist_id}/top", params={"limit": 25}, timeout=5).json()
        albums = requests.get(f"https://api.deezer.com/artist/{artist_id}/albums", params={"limit": 25}, timeout=5).json()
        return jsonify({
            "artist": info,
            "top_tracks": top.get("data", []),
            "albums": albums.get("data", [])
        })
    except Exception as e:
        app.logger.error(f"Artist error: {e}")
        return jsonify({"error": "Erreur lors de la récupération de l'artiste"}), 500

@app.route("/api/album/<album_id>")
def get_album(album_id):
    if not album_id or not re.match(r'^\d+$', str(album_id)):
        return jsonify({"error": "Identifiant album invalide"}), 400

    try:
        album_info = requests.get(f"https://api.deezer.com/album/{album_id}", timeout=5).json()
        return jsonify(album_info)
    except Exception as e:
        app.logger.error(f"Album error: {e}")
        return jsonify({"error": "Erreur lors de la récupération de l'album"}), 500

def get_metadata_from_url(url, fallback_title, fallback_artist="", fallback_cover=""):
    meta = {"title": fallback_title, "artist": fallback_artist or "Artiste", "album": fallback_title, "cover": fallback_cover}
    try:
        track_match = re.search(r'track/(\d+)', url)
        if track_match:
            r = requests.get(f"https://api.deezer.com/track/{track_match.group(1)}", timeout=5).json()
            meta["artist"] = r.get("artist", {}).get("name") or meta["artist"]
            meta["title"] = r.get("title") or meta["title"]
            meta["album"] = r.get("album", {}).get("title") or meta["title"]
            meta["cover"] = r.get("album", {}).get("cover_big") or meta["cover"]
            return meta
        
        album_match = re.search(r'album/(\d+)', url)
        if album_match:
            r = requests.get(f"https://api.deezer.com/album/{album_match.group(1)}", timeout=5).json()
            meta["artist"] = r.get("artist", {}).get("name") or meta["artist"]
            meta["title"] = r.get("title") or meta["title"]
            meta["album"] = meta["title"]
            meta["cover"] = r.get("cover_big") or meta["cover"]
    except Exception as e:
        app.logger.error(f"Error fetching Deezer metadata for {url}: {e}")
    return meta

def tag_m4a_file(file_path, meta):
    try:
        from mutagen.mp4 import MP4, MP4Cover
        audio = MP4(file_path)
        audio["\xa9nam"] = [meta["title"]]
        audio["\xa9ART"] = [meta["artist"]]
        audio["aART"] = [meta["artist"]]
        audio["\xa9alb"] = [meta["album"]]
        if meta.get("cover") and is_valid_url(meta["cover"]):
            img_data = requests.get(meta["cover"], timeout=5).content
            audio["covr"] = [MP4Cover(img_data, imageformat=MP4Cover.FORMAT_JPEG)]
        audio.save()
    except Exception as e:
        app.logger.warning(f"M4A tagging warning: {e}")

def perform_download(entry_id, target_url, title, artist, cover_url, music_dest, target_dest="main"):
    if not is_valid_url(target_url):
        update_history_status(entry_id, "failed", error_message="URL invalide ou non autorisée")
        return

    # Attempt 1: Local Deemix CLI (if .arl is present)
    arl_file = os.path.join(CONFIG_DIR, ".arl")
    if os.path.isfile(arl_file) and os.path.getsize(arl_file) > 0:
        app.logger.info(f"[Download #{entry_id}] Trying Deemix for: {target_url}")
        deemix_cmd = ["deemix", "-p", music_dest, target_url]
        try:
            res = subprocess.run(deemix_cmd, capture_output=True, text=True, timeout=120)
            if res.returncode == 0 and "Paste here your arl" not in res.stdout and "Paste here your arl" not in res.stderr:
                app.logger.info(f"[Download #{entry_id}] Deemix download successful for: {title}")
                update_history_status(entry_id, "completed")
                trigger_navidrome_scan(target_dest)
                return
            else:
                app.logger.warning(f"[Download #{entry_id}] Deemix failed (code {res.returncode}): {res.stderr or res.stdout}")
        except Exception as e:
            app.logger.warning(f"[Download #{entry_id}] Deemix exception: {e}")

    # Fallback: Fast native M4A audio stream via yt-dlp + Mutagen tagging (no ffmpeg required)
    meta = get_metadata_from_url(target_url, title, artist, cover_url)
    query = f"{meta['artist']} - {meta['title']}"
    out_dir = os.path.join(music_dest, safe_filename(meta["artist"]), safe_filename(meta["album"]))
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{safe_filename(meta['artist'])} - {safe_filename(meta['title'])}.m4a")

    app.logger.info(f"[Download #{entry_id}] Fallback to yt-dlp M4A with query: '{query}' -> {out_file}")
    ytdlp_cmd = [
        "yt-dlp",
        "-f", "ba[ext=m4a]/ba",
        "--no-playlist",
        "-o", out_file,
        f"ytsearch1:{query}"
    ]
    try:
        res = subprocess.run(ytdlp_cmd, capture_output=True, text=True, timeout=120)
        if res.returncode == 0 and os.path.isfile(out_file):
            tag_m4a_file(out_file, meta)
            app.logger.info(f"[Download #{entry_id}] yt-dlp download successful for: {query}")
            update_history_status(entry_id, "completed")
            trigger_navidrome_scan(target_dest)
        else:
            err_msg = (res.stderr or res.stdout or f"Échec code {res.returncode}").strip()
            if len(err_msg) > 200:
                err_msg = err_msg[-200:]
            app.logger.error(f"[Download #{entry_id}] yt-dlp failed (code {res.returncode}): {err_msg}")
            update_history_status(entry_id, "failed", error_message=err_msg)
    except Exception as e:
        app.logger.error(f"[Download #{entry_id}] yt-dlp exception: {e}")
        update_history_status(entry_id, "failed", error_message=str(e)[:200])

@app.route("/api/download", methods=["POST"])
def download():
    data = request.json or {}
    target_url = data.get("url", "").strip()
    title = sanitize_string(data.get("title", "Musique"), 255)
    artist = sanitize_string(data.get("artist", ""), 255)
    cover_url = data.get("cover_url", "").strip()
    item_type = data.get("item_type", "track")
    target_dest = "main"

    if not is_valid_url(target_url):
        return jsonify({"error": "URL invalide ou manquante"}), 400

    dest_info = TARGET_CONFIG[target_dest]
    music_dest = dest_info["dir"]
    dest_label = dest_info["label"]

    entry_id = add_history_entry(title, artist, cover_url, target_url, target_dest, item_type, "downloading")
    app.logger.info(f"Download requested: {title} ({target_url}) -> {dest_label} [ID {entry_id}]")

    t = threading.Thread(target=perform_download, args=(entry_id, target_url, title, artist, cover_url, music_dest, target_dest))
    t.daemon = True
    t.start()

    return jsonify({
        "status": "ok",
        "id": entry_id,
        "entry": {
            "id": entry_id,
            "title": title,
            "artist": artist,
            "cover_url": cover_url if is_valid_url(cover_url) else "",
            "url": target_url,
            "target": target_dest,
            "item_type": item_type,
            "status": "downloading",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "message": f"Téléchargement lancé pour : {title}"
    })

@app.route("/api/history")
def list_history():
    status = request.args.get("status", "all")
    try:
        limit = int(request.args.get("limit", 100))
    except (ValueError, TypeError):
        limit = 100

    entries = get_history_entries(status=status, limit=limit)
    return jsonify({"history": entries, "total": len(entries)})

@app.route("/api/history/retry", methods=["POST"])
def retry_history():
    data = request.json or {}
    entry_id = data.get("id")
    try:
        entry_id = int(entry_id) if entry_id is not None else None
    except (ValueError, TypeError):
        entry_id = None

    target_url = data.get("url", "").strip()
    title = sanitize_string(data.get("title", ""), 255)
    artist = sanitize_string(data.get("artist", ""), 255)
    cover_url = data.get("cover_url", "").strip()
    item_type = data.get("item_type", "track")
    target_dest = "main"

    if entry_id and entry_id > 0:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM history WHERE id = ?", (entry_id,)).fetchone()
            if row:
                row_dict = dict(row)
                target_url = target_url or row_dict.get("url", "")
                title = title or row_dict.get("title", "Musique")
                artist = artist or row_dict.get("artist", "")
                cover_url = cover_url or row_dict.get("cover_url", "")
                item_type = item_type or row_dict.get("item_type", "track")

    if not title:
        title = "Musique"

    if not is_valid_url(target_url):
        return jsonify({"error": "URL invalide ou introuvable pour cette musique"}), 400

    dest_info = TARGET_CONFIG[target_dest]
    music_dest = dest_info["dir"]

    new_id = add_history_entry(title, artist, cover_url, target_url, target_dest, item_type, "downloading")
    t = threading.Thread(target=perform_download, args=(new_id, target_url, title, artist, cover_url, music_dest, target_dest))
    t.daemon = True
    t.start()

    return jsonify({
        "status": "ok",
        "id": new_id,
        "entry": {
            "id": new_id,
            "title": title,
            "artist": artist,
            "cover_url": cover_url if is_valid_url(cover_url) else "",
            "url": target_url,
            "target": target_dest,
            "item_type": item_type,
            "status": "downloading",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "message": f"Relance du téléchargement pour : {title}"
    })

@app.route("/api/history/<int:entry_id>", methods=["DELETE"])
def delete_history(entry_id):
    if entry_id <= 0:
        return jsonify({"error": "ID invalide"}), 400
    try:
        delete_history_entry(entry_id)
        return jsonify({"status": "ok", "message": "Entrée supprimée de l'historique."})
    except Exception:
        return jsonify({"error": "Erreur lors de la suppression"}), 500

@app.route("/api/history/clear", methods=["POST"])
def clear_history_route():
    try:
        clear_all_history()
        return jsonify({"status": "ok", "message": "Historique vidé avec succès."})
    except Exception:
        return jsonify({"error": "Erreur lors du nettoyage de l'historique"}), 500

@app.route("/api/library")
def list_library():
    query = sanitize_string(request.args.get("q", ""), 100).lower()
    base_dir = TARGET_CONFIG["main"]["dir"]

    tracks = []
    base_path = Path(base_dir).resolve()

    if base_path.exists() and base_path.is_dir():
        for root, dirs, files in os.walk(base_path):
            for file in sorted(files):
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in ALLOWED_AUDIO_EXTENSIONS:
                    full_path = Path(root) / file
                    try:
                        rel_path = str(full_path.relative_to(base_path))
                    except ValueError:
                        continue
                        
                    if query and query not in rel_path.lower():
                        continue

                    try:
                        size_mb = round(full_path.stat().st_size / (1024 * 1024), 2)
                        tracks.append({
                            "name": file,
                            "rel_path": rel_path,
                            "size_mb": size_mb
                        })
                    except Exception:
                        continue

    return jsonify({"tracks": tracks, "total": len(tracks)})

@app.route("/api/delete", methods=["POST"])
def delete_track():
    data = request.json or {}
    rel_paths = data.get("rel_paths")
    if rel_paths is None:
        rel_path = data.get("rel_path", "").strip()
        rel_paths = [rel_path] if rel_path else []
    elif isinstance(rel_paths, str):
        rel_paths = [rel_paths.strip()]

    if not isinstance(rel_paths, list) or len(rel_paths) == 0:
        return jsonify({"error": "Aucun fichier spécifié"}), 400

    if len(rel_paths) > 500:
        return jsonify({"error": "Limite de 500 fichiers par requête dépassée"}), 400

    base_dir = TARGET_CONFIG["main"]["dir"]
    base_path = Path(base_dir).resolve()

    deleted_count = 0
    errors = []

    for rel_path in rel_paths:
        if not rel_path or not isinstance(rel_path, str):
            continue
        rel_path = rel_path.strip()
        try:
            target_path = (base_path / rel_path).resolve()
        except Exception:
            errors.append(f"{rel_path}: Chemin invalide")
            continue

        if not target_path.is_relative_to(base_path) or target_path == base_path:
            errors.append(f"{rel_path}: Accès non autorisé")
            continue

        if not target_path.exists():
            continue

        if target_path.is_file():
            if target_path.suffix.lower() not in ALLOWED_AUDIO_EXTENSIONS:
                errors.append(f"{rel_path}: Type de fichier non autorisé")
                continue

        try:
            if target_path.is_dir():
                shutil.rmtree(target_path)
            else:
                target_path.unlink()
                parent = target_path.parent
                if parent != base_path and parent.exists() and not any(parent.iterdir()):
                    try:
                        parent.rmdir()
                    except Exception:
                        pass
            deleted_count += 1
        except Exception as e:
            errors.append(f"{rel_path}: {str(e)}")

    if deleted_count > 0:
        t = threading.Thread(target=trigger_navidrome_scan, args=("main",))
        t.daemon = True
        t.start()

    msg = f"{deleted_count} morceau(x) supprimé(s) !" if deleted_count > 1 else "Musique supprimée et Navidrome nettoyé !"
    return jsonify({
        "status": "ok",
        "deleted_count": deleted_count,
        "errors": errors,
        "message": msg
    })

@app.route('/apple-touch-icon.png')
@app.route('/apple-touch-icon-precomposed.png')
def apple_touch_icon():
    return send_from_directory('static', 'apple-touch-icon.png')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4535, debug=False)
