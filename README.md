<div align="center">
  <img width="464" height="238" alt="image" src="" />
  <h1>Subsonic API to Telegram Status Bot</h1>
  <p><b>A Python script to broadcast your currently playing Subsonic API track directly to a Telegram channel message in real-time.</b></p>
  <div>
	  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"></a>
	  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-red.svg?style=flat-square"></a>
  </div>
</div>

A Python service that mirrors the authenticated user's current track in a Telegram channel through the Subsonic API's `getNowPlaying` endpoint.

## 🛠 Installation & Setup

1. Create a Telegram bot with [@BotFather](https://t.me/BotFather), add it as a channel administrator with permission to post, edit, and delete messages, and note the channel username or ID.
2. Create an account on your Subsonic API server for the bot. It must be allowed to access your music library. Playback is visible when the player reports it to the server (with scrobbling/play reporting enabled in the player).
3. Install Python 3.10 or newer and dependencies:

   ```sh
   python -m venv .venv
   # Windows PowerShell: .\.venv\Scripts\Activate.ps1
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and set `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`, `SUBSONIC_URL`, `SUBSONIC_USERNAME`, and `SUBSONIC_PASSWORD`. `SUBSONIC_URL` is the server base address, such as `https://music.example.com`, without `/rest`.
5. Run the service:

   ```sh
   python main.py
   ```

The bot creates a text status message on first run and saves its ID to `.env`; later it edits that same message when the displayed track changes. Set `UPDATE_INTERVAL` (minimum 5 seconds) and `LANGUAGE` (`en` or `ru`) as needed.

## License

This project is licensed under the [MIT License](LICENSE).
