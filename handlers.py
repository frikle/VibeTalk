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
                      delete_word, get_word_count)
from ai_client import ask_ai, API_KEY
from keyboards import (get_main_menu_keyboard, scenarios_keyboard, travel_keyboard,
                       study_keyboard, fun_keyboard, free_keyboard, mode_keyboard,
                       level_keyboard, settings_keyboard, my_words_keyboard)

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