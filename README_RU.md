<div align="center">
  <img width="514" height="215" alt="{C8DC20B8-1DAE-4C5E-9D97-587AAE8B20DB}" src="https://github.com/user-attachments/assets/13e16b46-97fe-4d7d-ab80-a0fa338c1678" />
  <h1>Subsonic API to Telegram Status Bot</h1>
  <p><b>Скрипт на Python для трансляции проигрываемого трека Subsonic в сообщение Telegram-канала в реальном времени.</b></p>
  <div>
	  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"></a>
	  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-red.svg?style=flat-square"></a>
  </div>
</div>

Python-сервис, который получает текущий трек авторизованного пользователя через Subsonic API и публикует его в Telegram-канале.

## Настройка

1. Создайте бота через [@BotFather](https://t.me/BotFather), добавьте его администратором канала с правами публикации, редактирования и удаления сообщений. Подготовьте username или ID канала.
2. Создайте отдельного пользователя на сервере Subsonic API с доступом к музыкальной библиотеке. Проигрыватель должен отправлять отчёты о воспроизведении на сервер (обычно для этого нужно включить scrobbling/play reporting в его настройках).
3. Установите Python 3.10 или новее и зависимости:

   ```sh
   python -m venv .venv
   # Windows PowerShell: .\.venv\Scripts\Activate.ps1
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Скопируйте `.env.example` в `.env` и укажите `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHANNEL_ID`, `SUBSONIC_URL`, `SUBSONIC_USERNAME` и `SUBSONIC_PASSWORD`. `SUBSONIC_URL` — базовый адрес сервера, например `https://music.example.com`, без `/rest`.
5. Запустите сервис:

   ```sh
   python main.py
   ```

При первом запуске бот создаст текстовое сообщение и сохранит его ID в `.env`. Далее он будет редактировать это же сообщение при изменении отображаемого трека. При необходимости задайте `UPDATE_INTERVAL` (не менее 5 секунд) и `LANGUAGE` (`ru` или `en`).

Бот использует endpoint `getNowPlaying` Subsonic API и аутентификацию по токену и salt. Он не подключается напрямую к базе данных сервера. API возвращает метаданные и длительность трека, но не надёжную текущую позицию, поэтому прогресс-бар не отображается.

## 📄 Лицензия

Этот проект распространяется под лицензией [MIT](LICENSE).
