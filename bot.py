# bot.py
import os 
import asyncio
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from database import create_tables, get_pool_count
from handlers import register_handlers
from ai_client import BOT_TOKEN, pregenerate_quiz_questions
from database import add_quiz_question_to_pool


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


async def _pregenerate_quiz_pool():
    """Фоновое пополнение пула вопросов для квиза.
    Генерирует вопросы для уровней, где пул меньше 20."""
    await asyncio.sleep(5)  # Небольшая задержка после запуска

    for level in ["A1", "A2", "B1", "B2", "C1"]:
        count = await get_pool_count(level)
        if count < 20:
            try:
                logger.info(f"Предгенерация вопросов для уровня {level} (текущий пул: {count})...")
                questions = await pregenerate_quiz_questions(level, count=20)
                added = 0
                for q in questions:
                    success = await add_quiz_question_to_pool(
                        level, q["question"], q["options"],
                        q["correct_answer"], q.get("explanation", "")
                    )
                    if success:
                        added += 1
                logger.info(f"Уровень {level}: добавлено {added} новых вопросов")
            except Exception as e:
                logger.error(f"Ошибка предгенерации для {level}: {e}")


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

    # Предгенерация вопросов для квиза (если пул пуст)
    asyncio.create_task(_pregenerate_quiz_pool())

    # Инициализация бота
    bot = Bot(token=BOT_TOKEN)

    # Регистрация командного меню (выпадающие подсказки при вводе "/")
    await bot.set_my_commands([
        BotCommand(command="start", description="🏠 Главное меню (настройки и темы)"),
        BotCommand(command="mode", description="👨‍🏫 Сменить режим (Учитель / Друг)"),
        BotCommand(command="level", description="📊 Изменить уровень английского"),
        BotCommand(command="topics", description="📚 Выбрать тему диалога"),
        BotCommand(command="quiz", description="📝 Квиз (проверь свои знания)"),
        BotCommand(command="quiz_reset", description="🗑 Сбросить историю квиза"),
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
    