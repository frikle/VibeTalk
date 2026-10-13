# handlers.py
import asyncio
import random
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)

from database import (add_user, get_user, update_user, add_word, get_words,
                      delete_word, get_word_count, get_quiz_history,
                      is_quiz_question_exists, add_quiz_question)
from ai_client import ask_ai, API_KEY, generate_quiz_session_question
from keyboards import (get_main_menu_keyboard, scenarios_keyboard, travel_keyboard,
                       study_keyboard, fun_keyboard, free_keyboard, mode_keyboard,
                       level_keyboard, settings_keyboard, my_words_keyboard,
                       quiz_difficulty_keyboard, quiz_answer_keyboard,
                       quiz_result_keyboard, quiz_final_keyboard)

# Встроенный словарь для частых слов (чтобы не запрашивать ИИ каждый раз)
BUILTIN_DICTIONARY = {
    "great": "отличный, великолепный",
    "good": "хороший",
    "bad": "плохой",
    "hello": "привет",
    "hi": "привет",
    "hey": "привет",
    "there": "там, туда",
    "here": "здесь, сюда",
    "movie": "фильм",
    "film": "фильм",
    "trailer": "трейлер",
    "release": "выпуск, релиз",
    "watch": "смотреть",
    "see": "видеть",
    "go": "идти",
    "come": "приходить",
    "want": "хотеть",
    "need": "нуждаться",
    "like": "нравиться",
    "love": "любить",
    "hate": "ненавидеть",
    "think": "думать",
    "know": "знать",
    "understand": "понимать",
    "speak": "говорить",
    "talk": "разговаривать",
    "say": "сказать",
    "tell": "рассказать",
    "ask": "спросить",
    "answer": "ответить",
    "question": "вопрос",
    "problem": "проблема",
    "idea": "идея",
    "place": "место",
    "city": "город",
    "street": "улица",
    "road": "дорога",
    "way": "путь, способ",
    "time": "время",
    "day": "день",
    "night": "ночь",
    "morning": "утро",
    "evening": "вечер",
    "today": "сегодня",
    "tomorrow": "завтра",
    "yesterday": "вчера",
    "now": "сейчас",
    "later": "позже",
    "soon": "скоро",
    "always": "всегда",
    "never": "никогда",
    "sometimes": "иногда",
    "often": "часто",
    "usually": "обычно",
    "really": "действительно",
    "very": "очень",
    "too": "тоже, слишком",
    "so": "так, поэтому",
    "but": "но",
    "and": "и",
    "or": "или",
    "if": "если",
    "when": "когда",
    "where": "где, куда",
    "who": "кто",
    "what": "что",
    "why": "почему",
    "how": "как",
    "because": "потому что",
    "for": "для, за",
    "with": "с",
    "without": "без",
    "about": "о, об",
    "in": "в",
    "on": "на",
    "at": "у, в",
    "to": "к, в",
    "from": "от, из",
    "by": "у, посредством",
    "of": "из, о",
    "up": "вверх",
    "down": "вниз",
    "out": "из, вне",
    "off": "с, выкл",
    "over": "над, через",
    "under": "под",
    "between": "между",
    "through": "через",
    "around": "вокруг",
    "near": "рядом, около",
    "far": "далеко",
    "left": "лево, налево",
    "right": "право, направо",
    "front": "перед",
    "back": "назад, спина",
    "next": "следующий",
    "last": "последний",
    "first": "первый",
    "new": "новый",
    "old": "старый",
    "young": "молодой",
    "big": "большой",
    "small": "маленький",
    "long": "длинный",
    "short": "короткий",
    "high": "высокий",
    "low": "низкий",
    "fast": "быстрый",
    "slow": "медленный",
    "hot": "горячий",
    "cold": "холодный",
    "warm": "тёплый",
    "cool": "прохладный",
    "easy": "лёгкий",
    "hard": "трудный, твёрдый",
    "difficult": "сложный",
    "simple": "простой",
    "important": "важный",
    "interesting": "интересный",
    "beautiful": "красивый",
    "ugly": "уродливый",
    "happy": "счастливый",
    "sad": "грустный",
    "angry": "злой",
    "tired": "уставший",
    "hungry": "голодный",
    "thirsty": "жаждущий",
    "ready": "готовый",
    "sure": "уверенный",
    "sorry": "извини",
    "please": "пожалуйста",
    "thanks": "спасибо",
    "yes": "да",
    "no": "нет",
    "maybe": "может быть",
    "ok": "окей",
    "okay": "окей",
    "welcome": "добро пожаловать",
    "special": "особый, специальный",
    "discount": "скидка",
    "order": "заказ",
    "toppings": "начинка, ингредиенты для пиццы",
    "pizzeria": "пиццерия",
    "kitchen": "кухня",
    "bake": "печь, выпекать",
    "delicious": "вкусный",
    "ring": "звонить, звонок",
    "genre": "жанр",
    "exam": "экзамен",
    "which": "который, какой",
    "hope": "надежда",
    "prepared": "подготовленный",
    "topic": "тема",
    "start": "начинать",
    "browsing": "просматривая",
    "exciting": "захватывающий, увлекательный",
    "usually": "обычно",
    "enjoy": "наслаждаться, получать удовольствие",
    "goodbye": "до свидания",
    "bye": "пока",
    "food": "еда",
    "drink": "напиток",
    "water": "вода",
    "coffee": "кофе",
    "tea": "чай",
    "bread": "хлеб",
    "meat": "мясо",
    "fish": "рыба",
    "milk": "молоко",
    "cheese": "сыр",
    "egg": "яйцо",
    "rice": "рис",
    "pasta": "паста",
    "pizza": "пицца",
    "burger": "бургер",
    "salad": "салат",
    "soup": "суп",
    "dessert": "десерт",
    "cake": "торт",
    "chocolate": "шоколад",
    "sugar": "сахар",
    "salt": "соль",
    "pepper": "перец",
    "money": "деньги",
    "price": "цена",
    "cheap": "дешёвый",
    "expensive": "дорогой",
    "free": "бесплатный",
    "buy": "покупать",
    "sell": "продавать",
    "pay": "платить",
    "cost": "стоить",
    "work": "работа",
    "job": "работа",
    "office": "офис",
    "meeting": "встреча",
    "project": "проект",
    "team": "команда",
    "boss": "босс",
    "colleague": "коллега",
    "friend": "друг",
    "family": "семья",
    "mother": "мать",
    "father": "отец",
    "parent": "родитель",
    "child": "ребёнок",
    "son": "сын",
    "daughter": "дочь",
    "brother": "брат",
    "sister": "сестра",
    "husband": "муж",
    "wife": "жена",
    "house": "дом",
    "home": "дом",
    "room": "комната",
    "bathroom": "ванная",
    "bedroom": "спальня",
    "door": "дверь",
    "window": "окно",
    "table": "стол",
    "chair": "стул",
    "bed": "кровать",
    "sofa": "диван",
    "tv": "телевизор",
    "computer": "компьютер",
    "phone": "телефон",
    "internet": "интернет",
    "music": "музыка",
    "song": "песня",
    "book": "книга",
    "story": "история",
    "word": "слово",
    "language": "язык",
    "english": "английский",
    "russian": "русский",
    "learn": "учить",
    "study": "изучать",
    "teach": "преподавать",
    "read": "читать",
    "write": "писать",
    "listen": "слушать",
    "hear": "слышать",
    "look": "смотреть",
    "play": "играть",
    "run": "бежать",
    "walk": "гулять, ходить",
    "swim": "плавать",
    "fly": "летать",
    "drive": "водить",
    "travel": "путешествовать",
    "trip": "поездка",
    "vacation": "отпуск",
    "holiday": "праздник",
    "birthday": "день рождения",
    "party": "вечеринка",
    "gift": "подарок",
    "card": "открытка",
    "letter": "письмо",
    "email": "электронная почта",
    "message": "сообщение",
    "news": "новости",
    "weather": "погода",
    "sun": "солнце",
    "moon": "луна",
    "star": "звезда",
    "sky": "небо",
    "cloud": "облако",
    "rain": "дождь",
    "snow": "снег",
    "wind": "ветер",
    "storm": "шторм",
    "thunder": "гром",
    "lightning": "молния",
    "rainbow": "радуга",
    "sea": "море",
    "ocean": "океан",
    "river": "река",
    "lake": "озеро",
    "mountain": "гора",
    "forest": "лес",
    "tree": "дерево",
    "flower": "цветок",
    "grass": "трава",
    "animal": "животное",
    "dog": "собака",
    "cat": "кошка",
    "bird": "птица",
    "horse": "лошадь",
    "cow": "корова",
    "pig": "свинья",
    "sheep": "овца",
    "chicken": "курица",
    "duck": "утка",
    "rabbit": "кролик",
    "mouse": "мышь",
    "bear": "медведь",
    "lion": "лев",
    "tiger": "тигр",
    "elephant": "слон",
    "monkey": "обезьяна",
    "snake": "змея",
    "frog": "лягушка",
    "health": "здоровье",
    "doctor": "врач",
    "hospital": "больница",
    "medicine": "лекарство",
    "pain": "боль",
    "head": "голова",
    "hand": "рука",
    "finger": "палец",
    "leg": "нога",
    "foot": "ступня",
    "eye": "глаз",
    "ear": "ухо",
    "nose": "нос",
    "mouth": "рот",
    "tooth": "зуб",
    "heart": "сердце",
    "blood": "кровь",
    "body": "тело",
    "life": "жизнь",
    "death": "смерть",
    "world": "мир",
    "country": "страна",
    "people": "люди",
    "person": "человек",
    "man": "мужчина",
    "woman": "женщина",
    "boy": "мальчик",
    "girl": "девочка",
    "baby": "младенец",
    "name": "имя",
    "number": "номер, число",
    "color": "цвет",
    "red": "красный",
    "blue": "синий",
    "green": "зелёный",
    "yellow": "жёлтый",
    "black": "чёрный",
    "white": "белый",
    "brown": "коричневый",
    "pink": "розовый",
    "purple": "фиолетовый",
    "orange": "оранжевый",
    "grey": "серый",
    "silver": "серебряный",
    "gold": "золотой",
    "size": "размер",
    "shape": "форма",
    "circle": "круг",
    "square": "квадрат",
    "line": "линия",
    "point": "точка",
    "side": "сторона",
    "end": "конец",
    "beginning": "начало",
    "middle": "середина",
    "top": "верх",
    "bottom": "низ",
    "center": "центр",
    "corner": "угол",
    "edge": "край",
    "surface": "поверхность",
    "inside": "внутри",
    "outside": "снаружи",
    "above": "выше",
    "below": "ниже",
    "before": "до",
    "after": "после",
    "during": "во время",
    "while": "пока",
    "since": "с",
    "until": "до",
    "already": "уже",
    "yet": "ещё",
    "still": "всё ещё",
    "again": "снова",
    "once": "однажды",
    "twice": "дважды",
    "single": "один",
    "double": "двойной",
    "half": "половина",
    "quarter": "четверть",
    "whole": "целый",
    "part": "часть",
    "piece": "кусок",
    "bit": "кусочек",
    "lot": "много",
    "many": "много",
    "much": "много",
    "few": "мало",
    "little": "мало",
    "several": "несколько",
    "some": "некоторые",
    "any": "любой",
    "all": "все",
    "every": "каждый",
    "each": "каждый",
    "both": "оба",
    "either": "любой из двух",
    "neither": "ни один из двух",
    "none": "ни один",
    "nothing": "ничего",
    "something": "что-то",
    "anything": "что-нибудь",
    "everything": "всё",
    "someone": "кто-то",
    "anyone": "кто-нибудь",
    "everyone": "все",
    "no one": "никто",
    "nobody": "никто",
    "somebody": "кто-то",
    "anybody": "кто-нибудь",
    "everybody": "все",
    "myself": "себя, сам",
    "yourself": "себя, сам",
    "himself": "себя, сам",
    "herself": "себя, сама",
    "itself": "себя, само",
    "ourselves": "себя, сами",
    "themselves": "себя, сами",
    "this": "это, этот",
    "that": "то, тот",
    "these": "эти",
    "those": "те",
    "same": "тот же",
    "different": "другой, различный",
    "similar": "похожий",
    "other": "другой",
    "another": "ещё один",
    "such": "такой",
    "as": "как, в качестве",
    "than": "чем",
    "then": "затем, потом",
    "where": "где, куда",
    "whether": "ли",
    "nor": "ни",
    "although": "хотя",
    "though": "хотя",
    "even": "даже",
    "unless": "если не",
    "however": "однако",
    "whatever": "что бы ни",
    "whoever": "кто бы ни",
    "whichever": "какой бы ни",
    "most": "большинство",
    "enough": "достаточно",
    "quite": "довольно",
    "rather": "скорее",
    "pretty": "довольно",
    "fairly": "довольно",
    "truly": "действительно",
    "actually": "на самом деле",
    "certainly": "конечно",
    "definitely": "определённо",
    "probably": "вероятно",
    "possibly": "возможно",
    "perhaps": "возможно",
    "surely": "наверняка",
    "clearly": "очевидно",
    "obviously": "очевидно",
    "apparently": "по-видимому",
    "naturally": "естественно",
    "of course": "конечно",
    "at least": "по крайней мере",
    "at most": "самое большее",
    "at best": "в лучшем случае",
    "at worst": "в худшем случае",
    "at first": "сначала",
    "at last": "наконец",
    "at once": "сразу",
    "at all": "вообще",
    "at all costs": "любой ценой",
    "at any rate": "во всяком случае",
    "at the same time": "в то же время",
    "at the moment": "в данный момент",
    "at present": "в настоящее время",
    "at the beginning": "в начале",
    "at the end": "в конце",
    "at the top": "наверху",
    "at the bottom": "внизу",
    "at once": "немедленно",
    "at first sight": "с первого взгляда",
    "at first glance": "с первого взгляда",
}


async def get_translation(word: str) -> str:
    """Переводит слово через Groq и возвращает чистый перевод."""
    prompt = f"Translate the English word '{word}' into Russian. Return ONLY the translation (1-2 words), nothing else."
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                data = await resp.json()
                if resp.status == 200 and "choices" in data:
                    return data["choices"][0]["message"]["content"].strip()
                else:
                    print("Groq error details:", data)
                    return "перевод недоступен"
    except Exception as e:
        print(f"Exception: {e}")
        return "ошибка связи"


class CustomScenarioState(StatesGroup):
    """FSM для ожидания описания своего сценария."""
    waiting_for_scenario = State()


class QuizState(StatesGroup):
    """FSM для управления сессией квиза (10 вопросов)."""
    waiting_for_difficulty = State()
    waiting_for_answer = State()


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню VibeTalk."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍🏫 Режим: Учитель", callback_data="set:mode")],
        [InlineKeyboardButton(text="📊 Уровень: B1", callback_data="set:level")],
        [InlineKeyboardButton(text="🎭 Выбор темы диалога", callback_data="menu:scenarios")],
        [InlineKeyboardButton(text="🎲 Случайный сценарий", callback_data="random")],
        [InlineKeyboardButton(text="✍️ Свой сценарий", callback_data="custom")],
        [InlineKeyboardButton(text="📚 Словарик (мои слова)", callback_data="my_words")],
    ])
    return keyboard


def scenarios_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора темы диалога."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✈️ Travel & Life", callback_data="cat:travel")],
        [InlineKeyboardButton(text="💼 Study & Career", callback_data="cat:study")],
        [InlineKeyboardButton(text="🎬 Fun & Roleplay", callback_data="cat:fun")],
        [InlineKeyboardButton(text="💬 Free Talk", callback_data="cat:free")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")],
    ])
    return keyboard


def travel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="☕️ В кафе", callback_data="scen:cafe")],
        [InlineKeyboardButton(text="🏨 В отеле", callback_data="scen:hotel")],
        [InlineKeyboardButton(text="✈️ В аэропорту", callback_data="scen:airport")],
        [InlineKeyboardButton(text="🚕 В такси", callback_data="scen:taxi")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")],
    ])


def study_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Собеседование", callback_data="scen:it_interview")],
        [InlineKeyboardButton(text="🎓 Защита проекта", callback_data="scen:project_defense")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")],
    ])


def fun_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎸 Покупка гитары", callback_data="scen:guitar")],
        [InlineKeyboardButton(text="🍕 Заказ пиццы", callback_data="scen:pizza")],
        [InlineKeyboardButton(text="🎬 Обсуждение фильма", callback_data="scen:movie")],
        [InlineKeyboardButton(text="🎮 Игры и хобби", callback_data="scen:games")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")],
    ])


def free_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Обсуждение игр", callback_data="scen:games")],
        [InlineKeyboardButton(text="🎬 Обсуждение фильмов", callback_data="scen:movies")],
        [InlineKeyboardButton(text="🎵 Обсуждение музыки", callback_data="scen:music")],
        [InlineKeyboardButton(text="💬 Сленг и идиомы", callback_data="scen:slang")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")],
    ])


def mode_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора режима общения."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍🏫 Учитель (с исправлениями)", callback_data="mode:teacher")],
        [InlineKeyboardButton(text="🤝 Друг (свободное общение)", callback_data="mode:friend")],
    ])


def level_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора уровня языка."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="A1", callback_data="level:A1"),
         InlineKeyboardButton(text="A2", callback_data="level:A2")],
        [InlineKeyboardButton(text="B1", callback_data="level:B1"),
         InlineKeyboardButton(text="B2", callback_data="level:B2")],
        [InlineKeyboardButton(text="C1", callback_data="level:C1")],
    ])


def settings_keyboard() -> InlineKeyboardMarkup:
    """Клавиатка настроек."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍🏫/🤝 Режим общения", callback_data="set:mode")],
        [InlineKeyboardButton(text="📊 Уровень языка", callback_data="set:level")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")],
    ])


def my_words_keyboard(words: list) -> InlineKeyboardMarkup:
    """Клавиатура для раздела Мои слова."""
    keyboard = []
    for word in words:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📌 {word['word']} — {word['translation']}",
                callback_data=f"word:{word['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


SCENARIOS = {
    "cafe": "☕️ В кафе — вы заказываете кофе и десерт, общаетесь с бариста",
    "hotel": "🏨 В отеле — вы заселяетесь, уточняете условия, решаете проблему с номером",
    "airport": "✈️ В аэропорту — регистрация на рейс, досмотр, поиск гейта",
    "taxi": "🚕 В такси — вы едете в незнакомом городе, общаетесь с водителем",
    "it_interview": "💼 Собеседование на работу — вас спрашивают об опыте, навыках и проектах",
    "project_defense": "🎓 Защита проекта — вы представляете проект комиссии",
    "guitar": "🎸 Покупка гитары — вы выбираете инструмент в магазине",
    "pizza": "🍕 Заказ пиццы — вы заказываете пиццу по телефону",
    "movie": "🎬 Обсуждение фильма — вы обсуждаете новый фильм с другом",
    "games": "🎮 Игры и хобби — разговор о видеоиграх, консолях и новинках",
    "movies": "🎬 Обсуждение фильмов — разговор о кино, актёрах и новинках",
    "music": "🎵 Обсуждение музыки — разговор о музыке, исполнителях и концертах",
    "slang": "💬 Сленг и идиомы — разговор о современном сленге и выражениях",
}

# === FALLBACK: Встроенные вопросы для квиза (если AI не смог сгенерировать) ===

QUIZ_FALLBACK_QUESTIONS = [
    {
        "question": "She ____ to school every day.",
        "options": ["go", "goes", "going", "gone"],
        "correct_answer": "goes",
        "explanation": "В Present Simple с 3-м лицом ед. ч. (he, she, it) глагол получает окончание -s: goes."
    },
    {
        "question": "I ____ this movie last week.",
        "options": ["see", "saw", "seen", "seeing"],
        "correct_answer": "saw",
        "explanation": "Past Simple от глагола see — saw. Last week указывает на прошедшее время."
    },
    {
        "question": "There ____ many people at the party.",
        "options": ["was", "were", "is", "be"],
        "correct_answer": "were",
        "explanation": "Many people — множественное число, поэтому were."
    },
    {
        "question": "He is ____ than his brother.",
        "options": ["tall", "taller", "tallest", "more tall"],
        "correct_answer": "taller",
        "explanation": "Сравнительная степень прилагательного tall — taller."
    },
    {
        "question": "We have lived here ____ 2015.",
        "options": ["for", "since", "from", "at"],
        "correct_answer": "since",
        "explanation": "Since используется с точкой во времени (since 2015). For — с периодом (for 10 years)."
    },
    {
        "question": "If it rains, we ____ at home.",
        "options": ["stay", "stayed", "will stay", "would stay"],
        "correct_answer": "will stay",
        "explanation": "First Conditional: if + Present Simple, will + инфинитив."
    },
    {
        "question": "She has ____ finished her homework.",
        "options": ["yet", "already", "still", "since"],
        "correct_answer": "already",
        "explanation": "Already используется в Present Perfect для указания, что действие уже завершено."
    },
    {
        "question": "This book ____ by Orwell.",
        "options": ["wrote", "written", "was written", "is wrote"],
        "correct_answer": "was written",
        "explanation": "Пассивный залог в Past Simple: was/were + V3. Write → wrote → written."
    },
    {
        "question": "I'm looking forward ____ you.",
        "options": ["to see", "seeing", "see", "to seeing"],
        "correct_answer": "to seeing",
        "explanation": "Look forward to + герундий (V-ing). Предлог to здесь не инфинитивный."
    },
    {
        "question": "He asked me ____ I was busy.",
        "options": ["that", "if", "what", "about"],
        "correct_answer": "if",
        "explanation": "В косвенном вопросе без вопросительного слова используется if/whether."
    },
    {
        "question": "The meeting is ____ Monday.",
        "options": ["in", "on", "at", "by"],
        "correct_answer": "on",
        "explanation": "Предлог on используется с днями недели: on Monday."
    },
    {
        "question": "I've been studying English ____ three years.",
        "options": ["since", "for", "from", "during"],
        "correct_answer": "for",
        "explanation": "For используется с периодом времени (three years). Since — с точкой (since 2023)."
    },
    {
        "question": "____ you ever been to London?",
        "options": ["Did", "Do", "Have", "Are"],
        "correct_answer": "Have",
        "explanation": "Present Perfect образуется с have/has + V3. Ever — маркер Present Perfect."
    },
    {
        "question": "She's been working here ____ 2020.",
        "options": ["for", "since", "from", "by"],
        "correct_answer": "since",
        "explanation": "Since + точка во времени (since 2020). For + период (for 4 years)."
    },
    {
        "question": "The ____ of the building is impressive.",
        "options": ["high", "height", "higher", "highest"],
        "correct_answer": "height",
        "explanation": "Существительное height (высота), не прилагательное high."
    },
    {
        "question": "I'd rather ____ at home tonight.",
        "options": ["to stay", "stay", "staying", "stayed"],
        "correct_answer": "stay",
        "explanation": "I'd rather + инфинитив без to (bare infinitive)."
    },
    {
        "question": "Neither my friends ____ I like coffee.",
        "options": ["or", "nor", "and", "but"],
        "correct_answer": "nor",
        "explanation": "Пара neither... nor... (ни... ни...)."
    },
    {
        "question": "He drove ____ the city center.",
        "options": ["through", "across", "cross", "over"],
        "correct_answer": "through",
        "explanation": "Through — сквозь/через что-то трёхмерное (through the city)."
    },
    {
        "question": "She apologized ____ late.",
        "options": ["to be", "for being", "being", "be"],
        "correct_answer": "for being",
        "explanation": "Apologize for + герундий (V-ing)."
    },
    {
        "question": "By next year, I ____ my degree.",
        "options": ["will finish", "will have finished", "finish", "have finished"],
        "correct_answer": "will have finished",
        "explanation": "Future Perfect: will have + V3. By next year — маркер Future Perfect."
    },
]

RANDOM_SCENARIOS = [
    ("Вы — турист, который заблудился в незнакомом городе. ИИ — местный житель, который помогает найти дорогу.", "🚶 Заблудившийся турист"),
    ("Вы — покупатель в магазине гитар. ИИ — продавец-консультант, который помогает выбрать инструмент.", "🎸 Покупка гитары"),
    ("Вы — пациент на приёме у врача. ИИ — врач, который расспрашивает о симптомах.", "🏥 Визит к врачу"),
    ("Вы — гость на вечеринке. ИИ — хозяин дома, который знакомит вас с другими гостями.", "🎉 Вечеринка"),
    ("Вы — клиент в ресторане. ИИ — официант, который принимает заказ и отвечает на вопросы.", "🍽️ Ужин в ресторане"),
    ("Вы — студент, который сдаёт экзамен. ИИ — экзаменатор, который задаёт вопросы.", "📝 Сдача экзамена"),
    ("Вы — человек, который нашёл кошелёк на улице. ИИ — владелец кошелька, который хочет его вернуть.", "👛 Найденный кошелёк"),
    ("Вы — журналист, который берёт интервью у знаменитости. ИИ — знаменитость.", "🎤 Интервью со звездой"),
    ("Вы — человек, который звоет в службу поддержки. ИИ — оператор колл-центра.", "📞 Звонок в поддержку"),
    ("Вы — путешественник во времени из 1920 года. ИИ — современный человек, который объясняет, как пользоваться смартфоном.", "⏳ Путешественник во времени"),
]


def get_random_scenario() -> tuple:
    return random.choice(RANDOM_SCENARIOS)


async def _send_quiz_question(message, user_id: int, state: FSMContext, is_new_message: bool = False):
    """Генерирует и отправляет один вопрос квиза (helper для сессии).

    При is_new_message=True отправляет новое сообщение, иначе edit_text.
    """
    data = await state.get_data()
    level = data.get("quiz_level", "B1")
    question_num = data.get("question_num", 1)

    excluded = await get_quiz_history(user_id)

    # До 2 попыток сгенерировать уникальный вопрос
    quiz_data = None
    for _ in range(2):
        try:
            candidate = await generate_quiz_session_question(level, excluded)
            if not await is_quiz_question_exists(user_id, candidate["question"]):
                quiz_data = candidate
                break
        except Exception as e:
            print(f"[QUIZ] Ошибка генерации: {e}")
            continue

    # Fallback: встроенный пул
    if not quiz_data:
        history = await get_quiz_history(user_id)
        available = [q for q in QUIZ_FALLBACK_QUESTIONS if q["question"] not in history]
        if available:
            quiz_data = random.choice(available)
        else:
            text = "Не удалось сгенерировать вопрос. Сбрось историю: /quiz_reset"
            if is_new_message:
                await message.answer(text)
            else:
                await message.edit_text(text)
            return

    # Сохраняем правильный ответ и объяснение в FSM
    await state.update_data(
        correct_answer=quiz_data["correct_answer"],
        explanation=quiz_data.get("explanation", ""),
        determined_level=quiz_data.get("determined_level", level)
    )

    # Записываем вопрос в историю (anti-repetition)
    await add_quiz_question(user_id, quiz_data["question"])

    question_text = (
        f"Вопрос {question_num} / 10\n\n"
        f"{quiz_data['question']}\n\n"
        f"Выбери правильный ответ:"
    )

    if is_new_message:
        await message.answer(
            question_text,
            reply_markup=quiz_answer_keyboard(quiz_data["options"], question_num)
        )
    else:
        await message.edit_text(
            question_text,
            reply_markup=quiz_answer_keyboard(quiz_data["options"], question_num)
        )


def register_handlers(dp: Dispatcher):
    """Регистрирует все хэндлеры бота."""

    @dp.message(CommandStart())
    async def cmd_start(message: Message, state: FSMContext):
        await state.clear()
        user_id = message.from_user.id
        await add_user(user_id)
        user = await get_user(user_id)

        welcome_text = (
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            "Я — твой умный ИИ-тренажер английского языка. "
            "Помогу тебе практиковать английский в различных ситуациях!\n\n"
            f"📋 Текущие настройки:\n"
            f"• Режим: {'👨\u200d🏫 Учитель' if user['mode'] == 'teacher' else '🤝 Друг'}\n"
            f"• Уровень: {user['level']}\n"
            f"• Сценарий: {user['scenario']}\n\n"
            "Выбери действие из меню ниже:"
        )
        await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(user['mode'], user['level']))

    @dp.message(Command("help"))
    async def cmd_help(message: Message):
        help_text = (
            "📚 <b>Справка по боту</b>\n\n"
            "<b>Команды:</b>\n"
            "/start — перезапустить бота\n"
            "/help — показать эту справку\n"
            "/settings — изменить настройки (режим, уровень)\n"
            "/menu — показать меню сценариев\n\n"
            "<b>Режимы:</b>\n"
            "👨\u200d🏫 <b>Учитель</b> — исправляет ошибки и объясняет правила\n"
            "🤝 <b>Друг</b> — свободное общение без исправлений\n\n"
            "<b>Уровни:</b>\n"
            "A1, A2 — начальный\n"
            "B1, B2 — средний\n"
            "C1 — продвинутый\n\n"
            "<b>Сценарии:</b>\n"
            "Выбери готовый сценарий, создай свой или получи случайный!\n\n"
            "<b>Мои слова:</b>\n"
            "Ответь (Reply) на сообщение бота со словом из разбора, чтобы сохранить его в свой словарь!"
        )
        await message.answer(help_text, parse_mode="HTML")

    @dp.message(Command("settings"))
    async def cmd_settings(message: Message):
        await message.answer("⚙️ Настройки:", reply_markup=settings_keyboard())

    @dp.message(Command("menu"))
    async def cmd_menu(message: Message):
        user = await get_user(message.from_user.id)
        await message.answer("🎭 Главное меню VibeTalk:", reply_markup=get_main_menu_keyboard(user['mode'], user['level']))

    @dp.message(Command("mode"))
    async def cmd_mode(message: Message):
        await message.answer(
            "👨‍🏫/🤝 Выбери режим общения:",
            reply_markup=mode_keyboard()
        )

    @dp.message(Command("level"))
    async def cmd_level(message: Message):
        await message.answer(
            "📊 Выбери свой уровень английского:",
            reply_markup=level_keyboard()
        )

    @dp.message(Command("topics"))
    async def cmd_topics(message: Message):
        await message.answer(
            "🎭 Выбор темы диалога:",
            reply_markup=scenarios_keyboard()
        )

    @dp.message(Command("random"))
    async def cmd_random(message: Message, state: FSMContext):
        scenario_text, scenario_name = get_random_scenario()
        user_id = message.from_user.id
        await update_user(user_id, scenario=scenario_name, custom_context=scenario_text)
        await state.clear()
        user = await get_user(user_id)
        await message.answer(
            f"🎲 Случайный сценарий: {scenario_name}\n\n"
            f"{scenario_text}\n\n"
            "Просто пиши сообщения на английском — я отыграю свою роль!",
            reply_markup=get_main_menu_keyboard(user['mode'], user['level'])
        )

    # === КВИЗ: Сессия из 10 вопросов ===

    @dp.callback_query(F.data == "quiz_start")
    async def callback_quiz_start(callback: CallbackQuery, state: FSMContext):
        """Запускает квиз из главного меню — показывает выбор сложности."""
        await state.set_state(QuizState.waiting_for_difficulty)
        await callback.message.edit_text(
            "Квиз: 10 вопросов\n\n"
            "Выбери уровень сложности:",
            reply_markup=quiz_difficulty_keyboard()
        )
        await callback.answer()

    @dp.message(Command("quiz"))
    async def cmd_quiz(message: Message, state: FSMContext):
        """Запускает квиз: сначала спрашивает сложность."""
        await state.set_state(QuizState.waiting_for_difficulty)
        await message.answer(
            "📝 <b>Квиз: 10 вопросов</b>\n\n"
            "Выбери уровень сложности:",
            parse_mode="HTML",
            reply_markup=quiz_difficulty_keyboard()
        )

    @dp.message(Command("quiz_reset"))
    async def cmd_quiz_reset(message: Message):
        """Сбрасывает историю квиза пользователя."""
        user_id = message.from_user.id
        await clear_quiz_history(user_id)
        await message.answer("История квиза очищена! Теперь вопросы могут повторяться.")

    @dp.callback_query(F.data.startswith("quiz_diff:"))
    async def callback_quiz_difficulty(callback: CallbackQuery, state: FSMContext):
        """Пользователь выбрал сложность — начинаем сессию из 10 вопросов."""
        level = callback.data.split(":")[1]
        user_id = callback.from_user.id

        user = await get_user(user_id)
        if not user:
            await add_user(user_id)

        # Инициализируем сессию
        await state.set_state(QuizState.waiting_for_answer)
        await state.update_data(
            quiz_level=level,
            question_num=1,
            correct_count=0,
            wrong_count=0
        )

        # Генерируем первый вопрос
        await _send_quiz_question(callback.message, user_id, state, is_new_message=False)
        await callback.answer()

    @dp.callback_query(F.data == "quiz_restart")
    async def callback_quiz_restart(callback: CallbackQuery, state: FSMContext):
        """Перезапуск квиза — снова спрашиваем сложность."""
        await state.set_state(QuizState.waiting_for_difficulty)
        await callback.message.edit_text(
            "📝 <b>Квиз: 10 вопросов</b>\n\n"
            "Выбери уровень сложности:",
            parse_mode="HTML",
            reply_markup=quiz_difficulty_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data.startswith("quiz_ans:"))
    async def callback_quiz_answer(callback: CallbackQuery, state: FSMContext):
        """Обрабатывает ответ пользователя и показывает результат."""
        _, question_num_str, user_answer = callback.data.split(":", 2)
        question_num = int(question_num_str)
        data = await state.get_data()
        correct_answer = data.get("correct_answer", "")
        explanation = data.get("explanation", "")
        correct_count = data.get("correct_count", 0)
        wrong_count = data.get("wrong_count", 0)

        # Подсчёт очков
        if user_answer == correct_answer:
            correct_count += 1
            result_text = "Правильно! Молодец!"
        else:
            wrong_count += 1
            result_text = "Неверно!"

        # Обновляем счёт в FSM
        await state.update_data(correct_count=correct_count, wrong_count=wrong_count)

        is_last = question_num >= 10

        if is_last:
            # Финальный экран
            total = correct_count + wrong_count
            score_pct = (correct_count / total * 100) if total > 0 else 0

            if score_pct >= 90:
                feedback = "Великолепно! Ты почти идеален!"
            elif score_pct >= 70:
                feedback = "Очень хорошо! Продолжай в том же духе!"
            elif score_pct >= 50:
                feedback = "Неплохо, но есть куда расти."
            else:
                feedback = "Не сдавайся! Попробуй ещё раз с более простым уровнем."

            await state.clear()
            await callback.message.edit_text(
                f"Квиз завершён!\n\n"
                f"Правильные ответы: {correct_count} / {total}\n"
                f"Ошибки: {wrong_count}\n\n"
                f"{feedback}",
                reply_markup=quiz_final_keyboard()
            )
        else:
            # Показываем результат и кнопку «Следующий вопрос»
            emoji = "✅" if user_answer == correct_answer else "❌"
            await callback.message.edit_text(
                f"{emoji} {result_text}\n\n"
                f"Твой ответ: {user_answer}\n"
                f"Правильный ответ: {correct_answer}\n\n"
                f"Объяснение: {explanation}\n\n"
                f"Вопрос {question_num} из 10. Счёт: {correct_count} верно, {wrong_count} ошибок.",
                reply_markup=quiz_result_keyboard()
            )

        await callback.answer()

    @dp.callback_query(F.data == "quiz_next")
    async def callback_quiz_next(callback: CallbackQuery, state: FSMContext):
        """Генерирует следующий вопрос в сессии."""
        data = await state.get_data()
        question_num = data.get("question_num", 0) + 1

        if question_num > 10:
            # На всякий случай — если что-то пошло не так
            await state.clear()
            await callback.message.edit_text(
                "Квиз завершён! Спасибо за участие!",
                reply_markup=quiz_final_keyboard()
            )
            await callback.answer()
            return

        await state.update_data(question_num=question_num)
        await _send_quiz_question(callback.message, callback.from_user.id, state, is_new_message=False)
        await callback.answer()

    @dp.callback_query(F.data == "quiz_end")
    async def callback_quiz_end(callback: CallbackQuery, state: FSMContext):
        """Досрочное завершение квиза — показываем итог."""
        data = await state.get_data()
        correct_count = data.get("correct_count", 0)
        wrong_count = data.get("wrong_count", 0)
        total = correct_count + wrong_count

        await state.clear()
        await callback.message.edit_text(
            f"Квиз досрочно завершён!\n\n"
            f"Правильные ответы: {correct_count} / {total}\n"
            f"Ошибки: {wrong_count}",
            reply_markup=quiz_final_keyboard()
        )
        await callback.answer()

    @dp.message(Command("custom"))
    async def cmd_custom(message: Message, state: FSMContext):
        await state.set_state(CustomScenarioState.waiting_for_scenario)
        await message.answer(
            "✍️ Опиши свою ситуационную игру.\n\n"
            "Например:\n"
            "• «Покупка гитары в магазине»\n"
            "• «Обсуждение музыки с другом»\n"
            "• «Заказ еды на доставку»\n\n"
            "Напиши описание, и я создам для тебя уникальный сценарий!"
        )

    @dp.message(Command("words"))
    async def cmd_words(message: Message):
        user_id = message.from_user.id
        words = await get_words(user_id)
        count = await get_word_count(user_id)

        if not words:
            text = "📚 Твой личный словарь\n\nПока пусто. Ответь (Reply) на сообщение бота со словом из разбора, чтобы сохранить его!"
        else:
            text = f"📚 Твой личный словарь ({count} слов):\n\n"
            for word in words:
                text += f"• {word['word']} — {word['translation']}\n"

        await message.answer(
            text,
            reply_markup=my_words_keyboard(words) if words else InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back")]
            ])
        )

    @dp.callback_query(F.data == "back")
    async def callback_back(callback: CallbackQuery):
        """Возврат в главное меню."""
        user = await get_user(callback.from_user.id)
        
        if not user:
            mode = "teacher"
            level = "Intermediate"
        else:
            mode = user['mode']
            level = user['level']
            
        await callback.message.edit_text(
            "🎭 Главное меню VibeTalk:", 
            reply_markup=get_main_menu_keyboard(mode, level)
        )
        await callback.answer()

    @dp.callback_query(F.data == "menu:scenarios")
    async def callback_menu_scenarios(callback: CallbackQuery):
        await callback.message.edit_text("🎭 Выбор темы диалога:", reply_markup=scenarios_keyboard())
        await callback.answer()

    @dp.callback_query(F.data.startswith("cat:"))
    async def callback_category(callback: CallbackQuery):
        category = callback.data.split(":")[1]
        if category == "travel":
            await callback.message.edit_text("✈️ Travel & Life:", reply_markup=travel_keyboard())
        elif category == "study":
            await callback.message.edit_text("💼 Study & Career:", reply_markup=study_keyboard())
        elif category == "fun":
            await callback.message.edit_text("🎬 Fun & Roleplay:", reply_markup=fun_keyboard())
        elif category == "free":
            await callback.message.edit_text("💬 Free Talk:", reply_markup=free_keyboard())
        await callback.answer()

    @dp.callback_query(F.data.startswith("scen:"))
    async def callback_scenario(callback: CallbackQuery, state: FSMContext):
        scenario_key = callback.data.split(":")[1]
        scenario_name = SCENARIOS.get(scenario_key, scenario_key)
        user_id = callback.from_user.id
        await update_user(user_id, scenario=scenario_name, custom_context=None)
        await state.clear()
        await callback.message.edit_text(
            f"✅ Сценарий выбран: <b>{scenario_name}</b>\n\n"
            "Теперь просто пиши сообщения на английском — я отвечу в рамках сценария!\n"
            "Используй /menu чтобы сменить сценарий или /settings для настроек.",
            parse_mode="HTML"
        )
        await callback.answer()

    @dp.callback_query(F.data == "custom")
    async def callback_custom(callback: CallbackQuery, state: FSMContext):
        await state.set_state(CustomScenarioState.waiting_for_scenario)
        await callback.message.edit_text(
            "✍️ Опиши свою ситуационную игру.\n\n"
            "Например:\n"
            "• «Покупка гитары в магазине»\n"
            "• «Обсуждение музыки с другом»\n"
            "• «Заказ еды на доставку»\n\n"
            "Напиши описание, и я создам для тебя уникальный сценарий!"
        )
        await callback.answer()

    @dp.callback_query(F.data == "random")
    async def callback_random(callback: CallbackQuery, state: FSMContext):
        scenario_text, scenario_name = get_random_scenario()
        user_id = callback.from_user.id
        await update_user(user_id, scenario=scenario_name, custom_context=scenario_text)
        await state.clear()
        await callback.message.edit_text(
            f"🎲 <b>Случайный сценарий: {scenario_name}</b>\n\n"
            f"{scenario_text}\n\n"
            "Просто пиши сообщения на английском — я отыграю свою роль!",
            parse_mode="HTML"
        )
        await callback.answer()

    @dp.callback_query(F.data == "set:mode")
    async def callback_set_mode(callback: CallbackQuery):
        await callback.message.edit_text(
            "👨\u200d🏫/🤝 Выбери режим общения:",
            reply_markup=mode_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data == "set:level")
    async def callback_set_level(callback: CallbackQuery):
        await callback.message.edit_text(
            "📊 Выбери свой уровень английского:",
            reply_markup=level_keyboard()
        )
        await callback.answer()

    @dp.callback_query(F.data.startswith("mode:"))
    async def callback_mode(callback: CallbackQuery):
        mode = callback.data.split(":")[1]
        user_id = callback.from_user.id
        await update_user(user_id, mode=mode)
        mode_name = "👨\u200d🏫 Учитель" if mode == "teacher" else "🤝 Друг"
        await callback.message.edit_text(
            f"✅ Режим изменён: {mode_name}",
            reply_markup=get_main_menu_keyboard(mode, (await get_user(user_id))['level'])
        )
        await callback.answer()

    @dp.callback_query(F.data.startswith("level:"))
    async def callback_level(callback: CallbackQuery):
        level = callback.data.split(":")[1]
        user_id = callback.from_user.id
        await update_user(user_id, level=level)
        await callback.message.edit_text(
            f"✅ Уровень изменён: {level}",
            reply_markup=get_main_menu_keyboard((await get_user(user_id))['mode'], level)
        )
        await callback.answer()

    @dp.callback_query(F.data == "my_words")
    async def callback_my_words(callback: CallbackQuery):
        user_id = callback.from_user.id
        words = await get_words(user_id)
        count = await get_word_count(user_id)

        if not words:
            text = "📚 <b>Твой личный словарь</b>\n\nПока пусто. Ответь (Reply) на сообщение бота со словом из разбора, чтобы сохранить его!"
        else:
            text = f"📚 <b>Твой личный словарь</b> ({count} слов):\n\n"
            for word in words:
                text += f"• <b>{word['word']}</b> — {word['translation']}\n"

        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=my_words_keyboard(words) if words else InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back")]
            ])
        )
        await callback.answer()

    @dp.callback_query(F.data.startswith("word:"))
    async def callback_word_delete(callback: CallbackQuery):
        word_id = int(callback.data.split(":")[1])
        user_id = callback.from_user.id
        await delete_word(user_id, word_id)

        words = await get_words(user_id)
        count = await get_word_count(user_id)

        if not words:
            text = "📚 <b>Твой личный словарь</b>\n\nПока пусто. Ответь (Reply) на сообщение бота со словом из разбора, чтобы сохранить его!"
        else:
            text = f"📚 <b>Твой личный словарь</b> ({count} слов):\n\n"
            for word in words:
                text += f"• <b>{word['word']}</b> — {word['translation']}\n"

        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=my_words_keyboard(words) if words else InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в меню", callback_data="back")]
            ])
        )
        await callback.answer()

    @dp.message(CustomScenarioState.waiting_for_scenario)
    async def process_custom_scenario(message: Message, state: FSMContext):
        user_id = message.from_user.id
        custom_text = message.text
        await update_user(user_id, scenario="✍️ Свой сценарий", custom_context=custom_text)
        await state.clear()
        user = await get_user(user_id)
        await message.answer(
            f"✅ Сценарий создан!\n\n"
            f"📝 Описание: {custom_text}\n\n"
            "Теперь просто пиши сообщения на английском — я отыграю роль в рамках твоего сценария!",
            reply_markup=get_main_menu_keyboard(user['mode'], user['level'])
        )

    @dp.message(F.reply_to_message)
    async def process_reply_save_word(message: Message, state: FSMContext):
        user_id = message.from_user.id
        word_text = message.text.strip()

        if message.reply_to_message and message.reply_to_message.from_user:
            word = word_text.split('\n')[0].strip()

            if '—' in word:
                parts = word.split('—', 1)
                word = parts[0].strip()
                translation = parts[1].strip()
            else:
                translation = await get_translation(word)

            result = f"✅ Слово сохранено!\n• {word} — {translation}"

            added = await add_word(user_id, word, translation)
            if added:
                await message.answer(result)
            else:
                await message.answer(
                    f"ℹ️ Слово {word} уже есть в твоём словаре."
                )
        else:
            await process_message(message, state)

    @dp.message()
    async def process_message(message: Message, state: FSMContext):
        user_id = message.from_user.id
        user = await get_user(user_id)

        if not user:
            await add_user(user_id)
            user = await get_user(user_id)

        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        except Exception:
            pass

        max_retries = 3
        for retry in range(max_retries):
            try:
                response = await ask_ai(
                    user_message=message.text,
                    mode=user["mode"],
                    level=user["level"],
                    scenario=user["scenario"],
                    custom_context=user.get("custom_context")
                )
                await message.answer(response)
                return
            except Exception as e:
                if retry < max_retries - 1:
                    await asyncio.sleep(2 * (retry + 1))
                    continue
                await message.answer(
                    "😔 Извини, произошла ошибка при обращении к ИИ. "
                    "Попробуй ещё раз позже.\n"
                    f"Техническая информация: {str(e)[:100]}"
                )

        try:
            response = await ask_ai(
                user_message=message.text,
                mode=user["mode"],
                level=user["level"],
                scenario=user["scenario"],
                custom_context=user.get("custom_context")
            )
            await message.answer(response)
        except Exception as e:
            await message.answer(
                "😔 Извини, произошла ошибка при обращении к ИИ. "
                "Попробуй ещё раз позже.\n"
                f"Техническая информация: {str(e)[:100]}"
            )