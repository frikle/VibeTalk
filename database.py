# database.py
import aiosqlite
from typing import Optional, List

DB_NAME = "english_trainer.db"


async def create_tables():
    """Создает таблицы настроек пользователей и словаря, если они не существуют."""
    async with aiosqlite.connect(DB_NAME) as db:
        # Таблица настроек пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                mode TEXT DEFAULT 'teacher',
                level TEXT DEFAULT 'B1',
                scenario TEXT DEFAULT 'Free Talk / Свободное общение',
                custom_context TEXT DEFAULT NULL
            )
        """)
        # Таблица личного словаря пользователя
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                word TEXT NOT NULL,
                translation TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, word)
            )
        """)
        # Таблица истории вопросов квиза (для защиты от повторений)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_quiz_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                UNIQUE(user_id, question_text)
            )
        """)
        await db.commit()


async def get_user(user_id: int) -> Optional[dict]:
    """Возвращает настройки пользователя или None, если пользователь не найден."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def add_user(user_id: int):
    """Добавляет нового пользователя с настройками по умолчанию."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,)
        )
        await db.commit()


async def update_user(user_id: int, **kwargs):
    """Обновляет указанные поля настроек пользователя."""
    if not kwargs:
        return
    fields = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [user_id]
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            f"UPDATE users SET {fields} WHERE user_id = ?", values
        )
        await db.commit()


# === Методы для работы со словарём пользователя ===

async def add_word(user_id: int, word: str, translation: str) -> bool:
    """Добавляет слово в словарь пользователя. Возвращает True если добавлено, False если уже есть."""
    async with aiosqlite.connect(DB_NAME) as db:
        try:
            await db.execute(
                "INSERT INTO user_words (user_id, word, translation) VALUES (?, ?, ?)",
                (user_id, word.lower().strip(), translation.strip())
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            # Слово уже существует
            return False


async def get_words(user_id: int) -> List[dict]:
    """Возвращает все слова пользователя."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM user_words WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def delete_word(user_id: int, word_id: int):
    """Удаляет слово из словаря пользователя."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM user_words WHERE id = ? AND user_id = ?",
            (word_id, user_id)
        )
        await db.commit()


async def get_word_count(user_id: int) -> int:
    """Возвращает количество слов в словаре пользователя."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM user_words WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


# === Методы для работы с историей квиза ===

async def get_quiz_history(user_id: int) -> List[str]:
    """Возвращает список текстов вопросов, которые уже задавались пользователю."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT question_text FROM user_quiz_history WHERE user_id = ? ORDER BY created_at",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


async def is_quiz_question_exists(user_id: int, question_text: str) -> bool:
    """Проверяет, задавался ли уже этот вопрос пользователю."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT 1 FROM user_quiz_history WHERE user_id = ? AND question_text = ?",
            (user_id, question_text)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None


async def add_quiz_question(user_id: int, question_text: str):
    """Записывает вопрос в историю квиза пользователя."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO user_quiz_history (user_id, question_text) VALUES (?, ?)",
            (user_id, question_text)
        )
        await db.commit()


async def clear_quiz_history(user_id: int):
    """Очищает историю квиза пользователя."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "DELETE FROM user_quiz_history WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()
