# ai_client.py
import aiohttp
import asyncio
import re
from typing import Optional

# НАСТРОЙКИ
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
API_BASE_URL = "https://api.groq.com/openai/v1"
MODEL_NAME = "openai/gpt-oss-20b"

MAX_RETRIES = 3
RETRY_DELAY = 2  # секунды


def clean_text(text: str) -> str:
    """Очищает текст от проблемных Markdown-символов для Telegram."""
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'_+', '', text)
    text = re.sub(r'`+', '', text)
    return text.strip()


def build_system_prompt(mode: str, level: str, scenario: str,
                        custom_context: Optional[str] = None) -> str:
    """Формирует System Prompt с учетом режима, уровня и сценария."""
    level_desc = {
        "A1": "начальный уровень (элементарные фразы, простые предложения)",
        "A2": "начальный уровень (простые бытовые диалоги)",
        "B1": "средний уровень (уверенное общение на бытовые темы)",
        "B2": "уровень выше среднего (сложные конструкции, нюансированная речь)",
        "C1": "продвинутый уровень (свободная естественная речь, идиомы)",
    }
    level_text = level_desc.get(level, "средний уровень")

    if mode == "teacher":
        behavior = (
            "Ты — VibeTalk AI, продвинутый, вовлекающий и эмоциональный ИИ-тренажер для изучения английского языка.\n\n"
            "Твоя задача — помогать студенту учиться через практику.\n"
            "Если пользователь пишет на английском и допускает ошибку "
            "(грамматическую, лексическую, орфографическую), "
            "ты ОБЯЗАН добавить в конец ответа блок разбора на русском языке:\n\n"
            "ИНСТРУКЦИЯ ПО ФОРМАТУ ОТВЕТА:\n"
            "1. Напиши ответ от лица собеседника по ролям.\n"
            "2. Добавь блок «💡 Разбор и советы:» (ошибки строго на русском языке, затем ровно одно полезное слово в формате «• Полезные слова: 📌 слово – перевод»).\n"
            "3. СТРОГО ЗАПРЕЩЕНО добавлять в конце новые вопросы или продолжение диалога (например, \"What toppings do you prefer?\"). Ответ должен заканчиваться сразу после блока полезных слов. Жди ответ пользователя.\n\n"
            "ВАЖНО: Сначала напиши полный ответ на английском (2-4 предложения + вопрос), "
            "затем добавь разбор на русском. Не обрывай текст!\n"
            "После этого ответь на английском языке в рамках сценария. "
            "Если ошибок нет — просто общайся по сценарию на английском. "
            "НЕ используй символы * _ в своих ответах — только обычный текст и эмодзи."
        )
    else:
        behavior = (
            "Ты — VibeTalk AI, продвинутый, вовлекающий и эмоциональный ИИ-тренажер для изучения английского языка.\n\n"
            "Ты — дружелюбный собеседник, с которым приятно практиковать английский. "
            "Используй современный живой английский, сленг, идиомы и эмодзи. "
            "НЕ исправляй ошибки пользователя и не объясняй грамматику — "
            "пользователь тренирует свободу и беглость речи (speaking flow). "
            "Поддерживай разговор, задавай вопросы, реагируй эмоционально. "
            "НЕ используй символы * _ в своих ответах — только обычный текст и эмодзи."
        )

    scenario_text = (
        f"Выбранный сценарий: {scenario}. "
        "Ты отыгрываешь свою роль в рамках этого сценария. "
    )
    if custom_context:
        scenario_text += f"Дополнительный контекст от пользователя: {custom_context}. "

    prompt = (
        f"{behavior}\n"
        f"Уровень языка пользователя: {level} — {level_text}. "
        "Адаптируй сложность своего английского и длину реплик под этот уровень: "
        "на A1–A2 пиши коротко и просто, на B1–B2 используй разнообразные конструкции, "
        "на C1 пиши свободно и естественно, как носитель.\n"
        f"{scenario_text}"
        "Отвечай компактно (2-4 предложения), без лишних наставлений, чтобы диалог оставался живым. "
        "В конце ответа обязательно задавай открытый вопрос, чтобы поддержать диалог."
    )
    return prompt


async def ask_ai(user_message: str, mode: str, level: str, scenario: str,
                 custom_context: Optional[str] = None) -> str:
    """Отправляет запрос в Groq API с повторными попытками при ошибках."""
    system_prompt = build_system_prompt(mode, level, scenario, custom_context)

    url = f"{API_BASE_URL}/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.8,
        "max_tokens": 1200,
    }

    timeout = aiohttp.ClientTimeout(total=60)

    for attempt in range(MAX_RETRIES):
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    data = await response.json()

                    if response.status == 200 and "choices" in data:
                        text = data["choices"][0]["message"]["content"]
                        return clean_text(text)

                    # Если ошибка 429 (превышен лимит) — ждём и пробуем снова
                    if response.status == 429:
                        print(f"429 ошибка (лимит), попытка {attempt + 1}/{MAX_RETRIES}")
                        await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                        continue

                    # Другие ошибки
                    error_msg = data.get("error", {}).get("message", str(data))
                    raise Exception(f"Ошибка API {response.status}: {error_msg}")

        except asyncio.TimeoutError:
            print(f"Таймаут, попытка {attempt + 1}/{MAX_RETRIES}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise Exception("Groq API не отвечает (таймаут)")

        except Exception as e:
            if "429" in str(e) and attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise

    raise Exception("Groq API недоступен после нескольких попыток")
