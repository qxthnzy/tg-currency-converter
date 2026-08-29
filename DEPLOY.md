# 🚀 Развёртывание конвертера валют — пошагово

Инструкция от пустого компьютера до бота, который работает круглосуточно.
Проект состоит из двух частей, и разворачиваются они **по отдельности**:

| Часть | Что это | Где живёт |
|-------|---------|-----------|
| `index.html` | само приложение (Mini App) | статический хостинг с HTTPS |
| `bot.py` | бот, который присылает кнопку | ваш компьютер или VPS |

---

## 1. Подготовка

### Установить Git

```bash
git --version          # если версия вывелась — Git уже есть
```

- **macOS**: `brew install git` (или установится сам после `xcode-select --install`)
- **Ubuntu/Debian**: `sudo apt update && sudo apt install git`
- **Windows**: [git-scm.com/download/win](https://git-scm.com/download/win)

### Создать репозиторий на GitHub

1. [github.com/new](https://github.com/new)
2. Имя: `tg-currency-converter`, тип: **Public** (нужен для бесплатного GitHub Pages).
3. Не ставьте галочки «Add README» — файлы уже есть локально.

### Связать локальную папку с репозиторием

```bash
cd путь/к/проекту
git init
git add .
git commit -m "Currency converter mini app"
git branch -M main
git remote add origin https://github.com/<ваш-логин>/tg-currency-converter.git
git push -u origin main
```

> `.gitignore` уже исключает `.env` — токен в репозиторий не уедет.

---

## 2. Локальная разработка

### Python 3.9+

```bash
python3 --version      # нужна 3.9 или новее
```

Нет — скачайте с [python.org/downloads](https://www.python.org/downloads/).

### Зависимости

```bash
pip install -r requirements.txt
```

### Токен бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram.
2. `/newbot` → имя бота → username (обязан заканчиваться на `bot`).
3. Скопируйте токен вида `123456789:ABCdefGHIjklmnoPQRstUVwxyz`.

### Файл `.env`

```bash
cp .env.example .env
```

Откройте `.env` и впишите токен:

```
BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstUVwxyz
MINIAPP_URL=https://your-domain.com/index.html
```

`MINIAPP_URL` пока заглушка — настоящий адрес появится на шаге 3.

### Посмотреть приложение в браузере

```bash
python3 -m http.server 8000
```

→ [http://localhost:8000](http://localhost:8000). Вёрстка и конвертация работают,
но приветствие по имени и «Поделиться» — нет: они требуют Telegram.

### Открыть локальную версию прямо в Telegram (ngrok)

Telegram принимает только HTTPS-адреса, а `localhost` таким не является.
[ngrok](https://ngrok.com/download) выдаёт временный HTTPS-адрес для локального сервера:

```bash
# терминал 1 — раздаём файлы
python3 -m http.server 8000

# терминал 2 — публикуем их наружу
ngrok http 8000
```

ngrok покажет строку вида `Forwarding https://a1b2-c3d4.ngrok-free.app -> http://localhost:8000`.
Скопируйте HTTPS-адрес в `.env`:

```
MINIAPP_URL=https://a1b2-c3d4.ngrok-free.app/index.html
```

> Адрес меняется при каждом запуске ngrok — для постоянной работы нужен хостинг (шаг 3).

### Запуск и проверка

```bash
python bot.py
```

В логе появится `запуск в режиме polling`. Откройте бота в Telegram, отправьте `/start`
и нажмите «💱 Открыть конвертер валют». Остановить бота — `Ctrl+C`.

---

## 3. Загрузка HTML на хостинг

Нужен любой хостинг статики с HTTPS. Выберите **один** вариант.

### A) Vercel — рекомендуется

```bash
npm install -g vercel
vercel                 # логин через браузер, дальше Enter на все вопросы
vercel --prod
```

Готовая ссылка вида `https://converter-ivory.vercel.app/index.html`.
Плюс: каждый `git push` автоматически обновляет сайт (если подключить репозиторий на vercel.com).

### B) GitHub Pages — без установки чего-либо

1. Репозиторий → **Settings** → **Pages**.
2. Source: **Deploy from a branch**, Branch: `main`, папка `/ (root)` → **Save**.
3. Через 1–2 минуты ссылка: `https://<логин>.github.io/tg-currency-converter/index.html`

### C) Netlify — перетаскиванием

1. [app.netlify.com/drop](https://app.netlify.com/drop)
2. Перетащите папку проекта в окно браузера.
3. Netlify выдаст ссылку вида `https://random-name.netlify.app/index.html`.

### Проверьте результат

Откройте полученную ссылку в браузере — должен открыться конвертер.
Адрес обязан начинаться с `https://`, иначе Telegram его не примет.

---

## 4. Подставить адрес приложения

В этом проекте адрес **не хардкодится в коде** — бот читает его из переменной окружения,
чтобы один и тот же `bot.py` работал и локально, и на сервере.

Откройте `.env` и замените заглушку на ссылку из шага 3:

```
MINIAPP_URL=https://converter-ivory.vercel.app/index.html
```

И в `index.html`, в блоке `<script>`, впишите username своего бота — он уходит
в ссылку «Попробуй сам» внутри сообщения о конвертации:

```js
const BOT = 'my_converter_bot';
```

После правки `index.html` залейте его на хостинг заново (`vercel --prod` или `git push`).

Перезапустите бота и проверьте: `/start` → кнопка должна открыть приложение.

---

## 5. Запуск в production

### Вариант A: Replit (проще, бесплатно)

1. [replit.com](https://replit.com) → **Create Repl** → вкладка **Import from GitHub**.
2. Выберите свой репозиторий.
3. Слева **Secrets** (замок) → добавьте два секрета:
   - `BOT_TOKEN` = ваш токен
   - `MINIAPP_URL` = ссылка с шага 3
4. В поле команды запуска: `python bot.py` → **Run**.

> На бесплатном тарифе Repl засыпает без активности — для «всегда включённого» бота
> нужен платный Always-On или вариант B.

### Вариант B: свой VPS (надёжнее)

Подойдёт любой: Hetzner (от ~€4/мес), DigitalOcean, Timeweb, AWS Lightsail.
Берите Ubuntu 22.04 или новее.

```bash
ssh root@<ip-сервера>

apt update && apt install -y python3 python3-pip git
git clone https://github.com/<ваш-логин>/tg-currency-converter.git /root/converter
cd /root/converter
pip3 install -r requirements.txt

nano .env          # впишите BOT_TOKEN и MINIAPP_URL, сохранить: Ctrl+O, выйти: Ctrl+X
python3 bot.py     # проверка, что всё работает — затем Ctrl+C
```

Бот работает, но остановится, как только вы закроете SSH. Чтобы этого не было — шаг 6.

---

## 6. Systemd-сервис (для VPS)

Systemd запускает бота при старте сервера и поднимает после падения.

```bash
nano /etc/systemd/system/tg-converter.service
```

Содержимое:

```ini
[Unit]
Description=Telegram Currency Converter Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/converter
EnvironmentFile=/root/converter/.env
ExecStart=/usr/bin/python3 /root/converter/bot.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Включить и запустить:

```bash
sudo systemctl daemon-reload
sudo systemctl enable tg-converter     # автозапуск при перезагрузке сервера
sudo systemctl start tg-converter
sudo systemctl status tg-converter     # должно быть "active (running)"
```

> `EnvironmentFile` читает `.env` **без** кавычек и комментариев в конце строк —
> пишите `BOT_TOKEN=123:ABC`, а не `BOT_TOKEN="123:ABC"  # токен`.

---

## 7. Мониторинг

```bash
journalctl -u tg-converter -f          # логи в реальном времени, выход Ctrl+C
journalctl -u tg-converter -n 50       # последние 50 строк
systemctl status tg-converter          # запущен ли сейчас
```

Если бот упадёт, systemd перезапустит его автоматически (`Restart=on-failure`).

Частые сообщения в логах:

| Строка в логе | Что значит |
|---------------|------------|
| `запуск в режиме polling` | всё в порядке, бот работает |
| `Ошибка: не задан BOT_TOKEN` | `.env` не найден или пуст |
| `MINIAPP_URL — заглушка` | забыли подставить адрес приложения (шаг 4) |
| `Conflict: terminated by other getUpdates` | бот запущен дважды — остановите лишний процесс |

---

## 8. Обновление кода

На сервере:

```bash
cd /root/converter
git pull origin main
systemctl restart tg-converter
```

Если менялся `index.html` — обновите ещё и хостинг:

- **Vercel/Netlify с подключённым репозиторием**: обновится сам после `git push`.
- **Vercel вручную**: `vercel --prod`.
- **GitHub Pages**: обновится сам через 1–2 минуты после `git push`.

Изменения в `requirements.txt` требуют повторной установки:

```bash
pip3 install -r requirements.txt && systemctl restart tg-converter
```

---

## Чек-лист

- [ ] Репозиторий на GitHub, `.env` в `.gitignore`
- [ ] Токен получен у @BotFather и записан в `.env`
- [ ] `index.html` открывается по HTTPS-ссылке
- [ ] `MINIAPP_URL` в `.env` = эта ссылка
- [ ] `const BOT` в `index.html` = username бота
- [ ] `/start` в Telegram открывает приложение
- [ ] На VPS: `systemctl status tg-converter` → `active (running)`
