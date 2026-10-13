# ai_client.py
import os
import aiohttp
import asyncio
import re
from typing import Optional

# НАСТРОЙКИ
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEY = os.getenv("API_KEY")
API_BASE_URL = "https://api.groq.com/openai/v1"
MODEL_NAME = "openai/gpt-oss-20b"

MAX_RETRIES = 1
RETRY_DELAY = 1  # секунды


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


async def generate_quiz_session_question(target_level: str, excluded_topics: list) -> dict:
    """Генерирует один вопрос для сессии квиза через Groq API.

    Модель сама оценивает истинную сложность вопроса (determined_level)
    и возвращает строго валидный JSON.

    Args:
        target_level: Целевой уровень (A1, A2, B1, B2, C1).
        excluded_topics: Список вопросов, которые уже задавались.

    Returns:
        dict: determined_level, question, options, correct_answer, explanation.
    """
    excluded_text = ""
    if excluded_topics:
        excluded_list = "\n".join(f"- {q}" for q in excluded_topics)
        excluded_text = (
            f"\n\nВАЖНО: НЕ повторяй следующие вопросы:\n{excluded_list}\n"
            "Придумай совершенно новый вопрос!"
        )

    level_requirements = {
        "A1": "Present Simple, Past Simple, Present Continuous. Простые слова (house, food, family). Короткие предложения.",
        "A2": "Present Perfect, Future Simple, модальные глаголы (can, must). Бытовая лексика. Простые связки.",
        "B1": "Present Perfect vs Past Simple, Passive Voice (present/past), Conditionals 0/1/2, относительные придаточные (who/which/that), герундий vs инфинитив. Средняя длина предложений.",
        "B2": "Conditionals 2/3, Perfect tenses (Past Perfect, Future Perfect), сложный Passive, инверсия, субъунктив (I wish / If I were), сложные связки (despite, whereas), нюансированная лексика.",
        "C1": "Сложные идиомы, инверсия (Never had I...), эллипсис, параллельные конструкции, продвинутая лексика (mitigate, albeit, comprehensive), регистр и стилистика, subtle grammar distinctions.",
    }
    level_req = level_requirements.get(target_level, level_requirements["B1"])

    system_prompt = (
        "Ты — опытный ESL-преподаватель (English as a Second Language). "
        "Твоя задача — создать ОДИН вопрос с множественным выбором (multiple choice) "
        "для проверки знаний английского языка.\n\n"
        f"Целевой уровень студента: {target_level}\n\n"
        f"ТРЕБОВАНИЯ К УРОВНЮ {target_level}:\n{level_req}\n\n"
        "ОЦЕНИ САМ: после формулировки вопроса ОБЯЗАТЕЛЬНО определи его ИСТИННУЮ сложность "
        "и запиши в поле determined_level (одно из: A1, A2, B1, B2, C1). "
        "Если вопрос слишком простой или сложный для target_level — скорректируй его.\n\n"
        "Формат ответа — СТРОГО валидный JSON, без markdown-обёрток, без лишнего текста:\n"
        "{\n"
        '  "determined_level": "B1",\n'
        '  "question": "текст вопроса на английском",\n'
        '  "options": ["вариант1", "вариант2", "вариант3", "вариант4"],\n'
        '  "correct_answer": "один из вариантов ТОЧНО как в options",\n'
        '  "explanation": "объяснение на русском языке"\n'
        "}\n\n"
        "ПРАВИЛА:\n"
        "- question — предложение с пропуском (____) или вопрос-выбор правильного варианта.\n"
        "- options — ровно 4 варианта, все грамматически возможны, но только 1 правильный.\n"
        "- correct_answer — ДОЛЖЕН точно совпадать с одним из элементов options.\n"
        "- explanation — краткое объяснение на русском (грамматическое правило или лексическое значение).\n"
        "- Вопросы на ГРАММАТИКУ, ЛЕКСИКУ или УПОТРЕБЛЕНИЕ.\n"
        "- НЕ задавай примитивные вопросы типа 'She ___ to school' для уровней B1 и выше.\n"
        f"{excluded_text}"
    )

    user_message = f"Создай один вопрос для уровня {target_level}."

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
        "temperature": 0.95,
        "max_tokens": 250,
    }

    timeout = aiohttp.ClientTimeout(total=15)

    for attempt in range(MAX_RETRIES):
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    data = await response.json()

                    if response.status == 200 and "choices" in data:
                        raw_text = data["choices"][0]["message"]["content"].strip()
                        print(f"[QUIZ DEBUG] Ответ API: {raw_text[:300]}")

                        import json

                        # Способ 1: прямой парсинг
                        try:
                            result = json.loads(raw_text)
                        except json.JSONDecodeError:
                            # Способ 2: извлечь JSON из markdown-обёртки
                            json_match = re.search(r'\{[\s\S]*\}', raw_text)
                            if json_match:
                                try:
                                    result = json.loads(json_match.group(0))
                                except json.JSONDecodeError:
                                    # Способ 3: убрать markdown-обёртку
                                    cleaned = re.sub(r'^```json\s*|\s*```$', '', raw_text, flags=re.MULTILINE).strip()
                                    result = json.loads(cleaned)
                            else:
                                raise

                        # Валидация структуры
                        required_keys = ("determined_level", "question", "options", "correct_answer", "explanation")
                        if all(k in result for k in required_keys):
                            if isinstance(result["options"], list) and len(result["options"]) == 4:
                                if result["correct_answer"] in result["options"]:
                                    if result["determined_level"] in ("A1", "A2", "B1", "B2", "C1"):
                                        print(f"[QUIZ DEBUG] Вопрос сгенерирован! Уровень: {result['determined_level']}")
                                        return result

                        print(f"[QUIZ DEBUG] Невалидная структура: {list(result.keys()) if isinstance(result, dict) else type(result)}")
                        raise ValueError("Невалидная структура JSON от API")

                    if response.status == 429:
                        print(f"429 ошибка (лимит), попытка {attempt + 1}/{MAX_RETRIES}")
                        await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                        continue

                    error_msg = data.get("error", {}).get("message", str(data))
                    print(f"[QUIZ DEBUG] Ошибка API {response.status}: {error_msg}")
                    raise Exception(f"Ошибка API {response.status}: {error_msg}")

        except asyncio.TimeoutError:
            print(f"Таймаут квиза, попытка {attempt + 1}/{MAX_RETRIES}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise Exception("Groq API не отвечает (таймаут)")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Ошибка парсинга JSON: {e}, попытка {attempt + 1}/{MAX_RETRIES}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)
                continue
            raise Exception(f"Не удалось сгенерировать вопрос: {e}")

        except Exception as e:
            if "429" in str(e) and attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                continue
            raise

    raise Exception("Groq API недоступен после нескольких попыток")
