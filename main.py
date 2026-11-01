import hashlib
import html
import json
import os
import secrets
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv, set_key

# Playback data is read through the Subsonic REST API.
BASE_DIR = Path(__file__).resolve().parent
DOTENV_PATH = BASE_DIR / ".env"
load_dotenv(DOTENV_PATH)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()
TELEGRAM_MESSAGE_ID = os.getenv("TELEGRAM_MESSAGE_ID", "").strip()
SUBSONIC_URL = os.getenv("SUBSONIC_URL", "").strip().rstrip("/")
SUBSONIC_USERNAME = os.getenv("SUBSONIC_USERNAME", "").strip()
SUBSONIC_PASSWORD = os.getenv("SUBSONIC_PASSWORD", "")
UPDATE_INTERVAL = max(5, int(os.getenv("UPDATE_INTERVAL", "5")))
LANGUAGE = os.getenv("LANGUAGE", "ru").lower()
API_VERSION = "1.16.1"
CLIENT_NAME = "SubsonicTelegramStatus"

try:
    with (BASE_DIR / "locales" / f"{LANGUAGE}.json").open(encoding="utf-8") as file:
        LANG = json.load(file)
except (OSError, json.JSONDecodeError):
    LANGUAGE = "ru"
    with (BASE_DIR / "locales" / "ru.json").open(encoding="utf-8") as file:
        LANG = json.load(file)


def missing_settings():
    required = {
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "TELEGRAM_CHANNEL_ID": TELEGRAM_CHANNEL_ID,
        "SUBSONIC_URL": SUBSONIC_URL,
        "SUBSONIC_USERNAME": SUBSONIC_USERNAME,
        "SUBSONIC_PASSWORD": SUBSONIC_PASSWORD,
    }
    return [name for name, value in required.items() if not value]


def subsonic_params():
    """Build the Subsonic token-and-salt authentication parameters."""
    salt = secrets.token_hex(12)
    token = hashlib.md5((SUBSONIC_PASSWORD + salt).encode("utf-8")).hexdigest()
    return {
        "u": SUBSONIC_USERNAME,
        "t": token,
        "s": salt,
        "v": API_VERSION,
        "c": CLIENT_NAME,
        "f": "json",
    }


def get_now_playing():
    """Fetch current playback from the Subsonic API getNowPlaying endpoint."""
    endpoint = f"{SUBSONIC_URL}/rest/getNowPlaying.view"
    response = requests.get(endpoint, params=subsonic_params(), timeout=10)
    response.raise_for_status()
    body = response.json().get("subsonic-response", {})
    if body.get("status") != "ok":
        error = body.get("error", {})
        raise RuntimeError(error.get("message", "Subsonic API returned an error"))
    entries = body.get("nowPlaying", {}).get("entry", [])
    if isinstance(entries, dict):
        entries = [entries]
    for entry in entries:
        if entry.get("username") == SUBSONIC_USERNAME:
            return entry
    return None


def format_duration(seconds):
    seconds = max(0, int(seconds or 0))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02}:{seconds:02}" if hours else f"{minutes}:{seconds:02}"


def display_value(value, fallback):
    if value is None or not str(value).strip() or str(value).strip().lower() == "null":
        return fallback
    return str(value)


def format_message(entry):
    if not entry:
        return LANG["inactive"]
    title = html.escape(display_value(entry.get("title"), LANG["unknown_track"]))
    artist = html.escape(display_value(entry.get("artist"), LANG["unknown_artist"]))
    album = html.escape(display_value(entry.get("album"), LANG["unknown_album"]))
    duration = format_duration(entry.get("duration", 0))
    text = (
        f"{LANG['now_playing']}"
        f"<b>{LANG['track']}:</b> {title}\n"
        f"<b>{LANG['artist']}:</b> {artist}\n"
        f"<b>{LANG['album']}:</b> {album}\n"
        f"<b>{LANG['duration']}:</b> {duration}"
    )
    return text

def telegram_request(method, payload):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    response = requests.post(url, json=payload, timeout=10)
    data = response.json()
    if not data.get("ok"):
        if method == "editMessageText" and "message is not modified" in data.get("description", "").lower():
            return True, None
        raise RuntimeError(data.get("description", f"Telegram HTTP {response.status_code}"))
    return True, data.get("result")


def remember_message(message_id):
    global TELEGRAM_MESSAGE_ID
    TELEGRAM_MESSAGE_ID = str(message_id)
    try:
        set_key(str(DOTENV_PATH), "TELEGRAM_MESSAGE_ID", TELEGRAM_MESSAGE_ID)
    except Exception as exc:
        print(f"Could not save TELEGRAM_MESSAGE_ID; set it manually: {exc}")


def publish(text):
    global TELEGRAM_MESSAGE_ID
    if TELEGRAM_MESSAGE_ID:
        try:
            telegram_request("editMessageText", {
                "chat_id": TELEGRAM_CHANNEL_ID,
                "message_id": int(TELEGRAM_MESSAGE_ID),
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            })
            return
        except RuntimeError as exc:
            if "there is no text in the message to edit" not in str(exc).lower():
                raise

    _, result = telegram_request("sendMessage", {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    })
    remember_message(result["message_id"])


def main():
    missing = missing_settings()
    if missing:
        print("Missing configuration in .env: " + ", ".join(missing))
        sys.exit(1)
    parsed = urlparse(SUBSONIC_URL)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        print("SUBSONIC_URL must be an http(s) URL, for example https://music.example.com")
        sys.exit(1)

    print(f"Starting Subsonic-to-Telegram status service ({SUBSONIC_URL})")
    last_message = None
    while True:
        try:
            entry = get_now_playing()
            message = format_message(entry)
            if message != last_message:
                publish(message)
                last_message = message
        except Exception as exc:
            print(f"Status update failed: {exc}")
        time.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
