# bot.py
import os 
import asyncio
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from database import create_tables
from handlers import register_handlers
from ai_client import BOT_TOKEN


# Простой веб-сервер для прохождения проверки порта на Render
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"VibeTalk Bot is running!")
    
    # Чтобы подавить лишние логи ошибок HEAD-запросов от UptimeRobot/Render
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()


async def main():
    """Точка входа: инициализация бота, диспетчера и запуск Long Polling."""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Создание таблиц в базе данных
    await create_tables()
    logger.info("База данных инициализирована")

    # Инициализация бота
    bot = Bot(token=BOT_TOKEN)

    # Регистрация командного меню (выпадающие подсказки при вводе "/")
    await bot.set_my_commands([
        BotCommand(command="start", description="🏠 Главное меню (настройки и темы)"),
        BotCommand(command="mode", description="👨‍🏫 Сменить режим (Учитель / Друг)"),
        BotCommand(command="level", description="📊 Изменить уровень английского"),
        BotCommand(command="topics", description="📚 Выбрать тему диалога"),
        BotCommand(command="random", description="🎲 Случайный сценарий"),
        BotCommand(command="custom", description="✍️ Свой сценарий"),
        BotCommand(command="words", description="📖 Словарик (мои слова)"),
    ])
    logger.info("Командное меню зарегистрировано")

    # Инициализация диспетчера
    dp = Dispatcher()

    # Регистрация всех хэндлеров
    register_handlers(dp)
    logger.info("Хэндлеры зарегистрированы")

    # Запрос на удаление вебхука и запуск Long Polling
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"delete_webhook: {e}")
    logger.info("Бот запущен! Ожидание сообщений...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    # 1. Сначала запускаем фоновый веб-сервер, чтобы порт 10000 открылся моментально
    threading.Thread(target=run_server, daemon=True).start()
    
    # 2. Затем запускаем самого Telegram-бота
    asyncio.run(main())
    