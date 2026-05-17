import os
import telebot
from telebot import types

# Инициализируем бота через переменную окружения Amvera
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Ошибка: Переменная BOT_TOKEN не найдена в окружении Amvera!")

bot = telebot.TeleBot(BOT_TOKEN)

# Новая расширенная база данных с картинками, наукой и гибридными ссылками
MUSIC_DATABASE = {
    "lofi": {
        "title": "☕ Lo-Fi Фокус (Состояние Потока)",
        "image": "https://images.unsplash.com/photo-1518495973542-4542c06a5843?q=80&w=600&auto=format&fit=crop", # Уютная атмосфера для учебы
        "science": "<b>🧠 Научное обоснование:</b> Монотонный ритм (70-90 BPM) совпадает с альфа-ритмами мозга. Виниловый треск работает как акустический маскиратор, блокируя резкие внешние раздражители.",
        "ya": "https://music.yandex.ru/users/music-blog/playlists/2253",
        "vk": "https://vk.com/audio?z=audio_playlist-2000392398_1392398",
        "alt": "https://rutube.ru/video/98d75e848fa58882ca9f56a5c1bc2605/"
    },
    "phonk": {
        "title": "⚡ Дрифт-Фонк (Дофаминовый Буст)",
        "image": "https://images.unsplash.com/photo-1614850523459-c2f4c699c52e?q=80&w=600&auto=format&fit=crop", # Динамичный неоновый фон
        "science": "<b>🔥 Научное обоснование:</b> Быстрый, энергичный ритм без слов стимулирует выработку дофамина. Отлично подходит для преодоления прокрастинации и выполнения рутинной, быстрой работы (верстка, сборка, задачи).",
        "ya": "https://music.yandex.ru/users/music-top/playlists/1054",
        "vk": "https://vk.com/audio?z=audio_playlist-2000072719_15072719",
        "alt": "https://rutube.ru/video/73ba8de69cfcfbc54b659c231a4a49c4/"
    },
    "ambient": {
        "title": "🌌 Классический Эмбиент (Глубокое Погружение)",
        "image": "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?q=80&w=600&auto=format&fit=crop", # Космический расслабляющий фон
        "science": "<b>🌊 Научное обоснование:</b> Полное отсутствие структуры и темп ниже 60 BPM освобождают до 20% ресурсов рабочей памяти мозга. Идеально для сложного анализа, физики и математики.",
        "ya": "https://music.yandex.ru/users/music-blog/playlists/1814",
        "vk": "https://vk.com/audio?z=audio_playlist-2000411804_411804",
        "alt": "https://rutube.ru/video/c18fb9958adfa6020c6a51241f81014a/"
    },
    "nature": {
        "title": "🌿 Звуки Природы и Розовый Шум",
        "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=600&auto=format&fit=crop", # Лесной пейзаж
        "science": "<b>🍃 Научное обоснование:</b> Эволюционно мозг воспринимает звуки дождя, леса или водопада как сигнал полной безопасности. Это снижает уровень стрессового гормона кортизола и убирает тревожность перед экзаменами.",
        "ya": "https://music.yandex.ru/users/yamusic-podcast/playlists/1036",
        "vk": "https://vk.com/audio?z=audio_playlist-2000216447_16447",
        "alt": "https://www.youtube.com/watch?v=mPZkdNFkNps"
    },
    "neoclassic": {
        "title": "🎹 Неоклассика (Творческий Подъем)",
        "image": "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?q=80&w=600&auto=format&fit=crop", # Фортепиано
        "science": "<b>🎼 Научное обоснование:</b> Инструментальная музыка (фортепиано, скрипка) активирует одновременно оба полушария мозга. Повышает пластичность мышления и помогает находить нестандартные решения задач.",
        "ya": "https://music.yandex.ru/users/yamusic-classical/playlists/1004",
        "vk": "https://vk.com/audio?z=audio_playlist-2000385556_1385556",
        "alt": "https://www.youtube.com/watch?v=kYor7asMv_M"
    }
}

# Функция создания постоянного меню внизу экрана
def get_main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_genres = types.KeyboardButton("🎵 Выбрать жанр")
    btn_about = types.KeyboardButton("🎓 О проекте")
    keyboard.add(btn_genres, btn_about)
    return keyboard

# Функция генерации инлайн-меню выбора жанров
def get_genres_inline():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_lofi = types.InlineKeyboardButton("☕ Фокус и Учеба (Lo-Fi)", callback_data="mode_lofi")
    btn_phonk = types.InlineKeyboardButton("⚡ Быстрый старт / Драйв (Phonk)", callback_data="mode_phonk")
    btn_ambient = types.InlineKeyboardButton("🌌 Глубокое погружение (Ambient)", callback_data="mode_ambient")
    btn_nature = types.InlineKeyboardButton("🌿 Звуки природы / Розовый шум", callback_data="mode_nature")
    btn_classic = types.InlineKeyboardButton("🎹 Творческий подъем (Неоклассика)", callback_data="mode_neoclassic")
    markup.add(btn_lofi, btn_phonk, btn_ambient, btn_nature, btn_classic)
    return markup

# Команда /start и обработка перезапусков
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Привет! 👋\n\n"
        "Я — <b>StudyTunesBot</b>, твой персональный нейро-музыкальный ассистент. "
        "Я помогаю подобрать фоновый звук для повышения продуктивности, опираясь на исследования в области когнитивной психологии.\n\n"
        "Используй меню внизу экрана или выбери режим прямо сейчас:"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="html", reply_markup=get_main_keyboard())
    bot.send_message(message.chat.id, "Доступные аудио-зоны для обучения:", reply_markup=get_genres_inline())

# Обработка текстовых команд с нижней клавиатуры
@bot.message_handler(content_types=['text'])
def handle_text_buttons(message):
    if message.text == "🎵 Выбрать жанр":
        bot.send_message(message.chat.id, "Выберите аудио-зону под вашу текущую задачу:", reply_markup=get_genres_inline())
        
    elif message.text == "🎓 О проекте":
        about_text = (
            "🎓 <b>Информационная справка о проекте</b>\n\n"
            "<b>Проект:</b> Разработка Telegram-бота 'StudyTunesBot' для оптимизации учебного процесса.\n"
            "<b>Разработчик:</b> Каиров Нуркамаль Алтынбекович, учащийся 10 класса.\n"
            "<b>Образовательное учреждение:</b> ГБОУ Школа №2070 (г. Москва).\n\n"
            "🎯 <b>Цель проекта:</b> Создание доступного инструмента для повышения концентрации внимания, "
            "снижения уровня когнитивной усталости и стресса у школьников и студентов во время самостоятельной подготовки.\n\n"
            "📋 <b>В основе бота лежит научный подход:</b> фильтрация частот, подбор определенного темпа (BPM) "
            "и полное исключение вербального (речевого) шума, который перегружает рабочую память мозга."
        )
        bot.send_message(message.chat.id, about_text, parse_mode="html")

# Обработка нажатий на инлайн-кнопки жанров (Отправка нового сообщения с КАРТИНКОЙ)
