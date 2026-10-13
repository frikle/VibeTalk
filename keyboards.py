# keyboards.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard(current_mode: str, current_level: str) -> InlineKeyboardMarkup:
    """Генерирует главное меню с текущими настройками пользователя."""
    mode_text = "👨‍🏫 Режим: Учитель" if current_mode == "teacher" else "🤝 Режим: Друг"
    level_text = f"📊 Уровень: {current_level}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=mode_text, callback_data="set:mode")],
        [InlineKeyboardButton(text=level_text, callback_data="set:level")],
        [InlineKeyboardButton(text="🎭 Выбор темы диалога", callback_data="menu:scenarios")],
        [InlineKeyboardButton(text="📝 Квиз (проверь себя)", callback_data="quiz_start")],
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


def quiz_answer_keyboard(options: list) -> InlineKeyboardMarkup:
    """Клавиатура для ответа на вопрос квиза (одна колонка, callback_data = quiz_ans:<текст ответа>)."""
    keyboard = []
    for option in options:
        keyboard.append([
            InlineKeyboardButton(text=option, callback_data=f"quiz_ans:{option}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def quiz_again_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура «Ещё вопрос» после ответа."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Следующий вопрос", callback_data="quiz_next")],
        [InlineKeyboardButton(text="🔙 В меню", callback_data="back")],
    ])
