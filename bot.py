"""Telegram-бот, который открывает Mini App «Конвертер валют».

Запуск:
    pip install python-telegram-bot          # v20+
    export BOT_TOKEN=<токен от @BotFather>
    export MINIAPP_URL=https://your-domain.com/index.html   # обязательно https
    python bot.py
"""

import json
import logging
import os
import sys

try:                                  # необязательно: подхватывает переменные из файла .env
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
    WebAppInfo,
)
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Логи в консоль: видно, что бот запустился и какие апдейты приходят.
logging.basicConfig(format="%(asctime)s %(name)s %(levelname)s: %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)   # иначе httpx засоряет вывод
log = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Подставьте сюда свой URL (или задайте переменную MINIAPP_URL).
MINIAPP_URL = os.getenv("MINIAPP_URL", "https://your-domain.com/index.html")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")                 # опционально: продакшен вместо polling
PORT = int(os.getenv("PORT", 8080))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start — присылает кнопки, открывающие Mini App."""
    # Inline-кнопка живёт в самом сообщении.
    inline = InlineKeyboardMarkup(
        [[InlineKeyboardButton("💱 Открыть конвертер валют", web_app=WebAppInfo(url=MINIAPP_URL))]]
    )
    await update.message.reply_text(
        "Привет! 👋\nОткрой конвертер валют прямо в Telegram:", reply_markup=inline
    )

    # Кнопка клавиатуры (снизу): только из неё Telegram разрешает tg.sendData(),
    # то есть кнопка «Поделиться результатом» внутри app пришлёт данные сюда, в чат.
    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("💱 Конвертер", web_app=WebAppInfo(url=MINIAPP_URL))]],
        resize_keyboard=True,
    )
    await update.message.reply_text("Кнопка снизу — чтобы делиться результатом.", reply_markup=keyboard)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help — короткая справка. Функция названа help_command, чтобы не перекрыть встроенный help()."""
    await update.message.reply_text(
        "💱 Конвертер валют\n\n"
        "/start — открыть приложение\n"
        "/help — эта справка\n\n"
        "Внутри приложения:\n"
        "• выберите валюты и введите сумму — пересчёт идёт на лету\n"
        "• «Поменять местами» — меняет «Из» и «В»\n"
        "• «Избранное» — сохраняет пару валют (до 5)\n"
        "• «Поделиться» — отправляет результат в чат\n"
        "• история хранит последние конвертации\n\n"
        "Курсы обновляются раз в час, офлайн показываются последние сохранённые."
    )


async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Данные из tg.sendData() внутри Mini App — отвечаем красивым сообщением."""
    try:
        data = json.loads(update.message.web_app_data.data)
        amount, result = float(data["amount"]), float(data["result"])
        src, dst = str(data["from"])[:3], str(data["to"])[:3]   # данные от клиента — не доверяем
    except (ValueError, KeyError, TypeError) as err:
        log.warning("плохие данные из Mini App: %s", err)
        await update.message.reply_text("Не получилось прочитать результат 🤷")
        return

    rate = result / amount if amount else 0
    await update.message.reply_text(
        f"🔄 Конвертация: {amount:,.2f} {src} → {result:,.2f} {dst}\n"
        f"💱 Курс: 1 {src} = {rate:.4f} {dst}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Попробуй сам", web_app=WebAppInfo(url=MINIAPP_URL))]]
        ),
    )


def main() -> None:
    """Собирает приложение и запускает бота."""
    if not BOT_TOKEN:
        sys.exit("Ошибка: не задан BOT_TOKEN.\nПолучите токен у @BotFather и выполните:\n"
                 '  export BOT_TOKEN="123456:ABC-..."')
    if MINIAPP_URL.startswith("https://your-domain.com"):
        log.warning("MINIAPP_URL — заглушка. Кнопка не откроется, пока не подставите свой https-URL.")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))

    if WEBHOOK_URL:                       # продакшен
        log.info("запуск в режиме webhook на порту %s", PORT)
        app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=WEBHOOK_URL)
    else:                                 # локальная разработка
        log.info("запуск в режиме polling, Ctrl+C для остановки")
        app.run_polling()


if __name__ == "__main__":
    main()
