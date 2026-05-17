import os
import telebot
from telebot import types

# Принудительный моментальный вывод в консоль Amvera
print("=== ИНИЦИАЛИЗАЦИЯ: ЗАПУСК СКРИПТА ===", flush=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    print("=== КРИТИЧЕСКАЯ ОШИБКА: ТОКЕН В ОКРУЖЕНИИ НЕ НАЙДЕН! ===", flush=True)
    raise ValueError("Скрипт остановлен: нет токена.")

print(f"=== ТОКЕН УСПЕШНО СЧИТАН (Длина: {len(BOT_TOKEN)} симв.) ===", flush=True)
bot = telebot.TeleBot(BOT_TOKEN)

# ОБНОВЛЕННАЯ БАЗА ДАННЫХ ТРЕКОВ И ЖАНРОВ (Без VK и с новыми ссылками)
TRACKS = {
    "lofi": {
        "title": "☕ Lo-Fi Фокус (Состояние Потока)",
        "image": "https://images.unsplash.com/photo-1518495973542-4542c06a5843?q=80&w=600&auto=format&fit=crop",
        "science": "<b>🧠 Научное обоснование:</b> Монотонный ритм (70-90 BPM) совпадает с альфа-ритмами мозга. Виниловый треск работает как акустический маскиратор, блокируя резкие внешние раздражители.",
        "ya": "https://music.yandex.ru/search?text=lofi+hip+hop&utm_source=chatgpt.com",
        "yt": "https://www.youtube.com/live/jfKfPfyJRdk?utm_source=chatgpt.com"
    },
    "phonk": {
        "title": "⚡ Дрифт-Фонк (Дофаминовый Буст)",
        "image": "https://images.unsplash.com/photo-1614850523459-c2f4c699c52e?q=80&w=600&auto=format&fit=crop",
        "science": "<b>🔥 Научное обоснование:</b> Быстрый, энергичный ритм без слов стимулирует выработку дофамина. Отлично подходит для преодоления прокрастинации и выполнения рутинной, быстрой работы (верстка, сборка, задачи).",
        "ya": "https://music.yandex.ru/search?text=phonk&utm_source=chatgpt.com",
        "yt": "https://youtu.be/_xUxFLEP6gc?si=RUrpyEByhucxZv1a"
    },
    "ambient": {
        "title": "🌌 Классический Эмбиент (Глубокое Погружение)",
        "image": "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?q=80&w=600&auto=format&fit=crop",
        "science": "<b>🌊 Научное обоснование:</b> Полное отсутствие структуры и темп ниже 60 BPM освобождают до 20% ресурсов рабочей памяти мозга. Идеально для сложного анализа, физики и математики.",
        "ya": "https://music.yandex.ru/search?text=ambient&utm_source=chatgpt.com",
        "yt": "https://www.youtube.com/watch?v=s77L_XWfFxo"  # Исправлено на качественный эмбиент-стрим
    },
    "nature": {
        "title": "🌿 Звуки Природы и Розовый Шум",
        "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=600&auto=format&fit=crop",
        "science": "<b>🍃 Научное обоснование:</b> Эволюционно мозг воспринимает звуки дождя, леса или водопада как сигнал полной безопасности. Это снижает уровень стрессового гормона кортизола и убирает тревожность перед экзаменами.",
        "ya": "https://music.yandex.ru/search?text=%D0%B7%D0%B2%D1%83%D0%BA%D0%B8+%D0%BF%D1%80%D0%B8%D1%80%D0%BE%D0%B4%D1%8B&utm_source=chatgpt.com",
        "yt": "https://www.youtube.com/watch?v=mPZkdNFkNps&utm_source=chatgpt.com"
    },
    "neoclassic": {
        "title": "🎹 Неоклассика (Творческий Подъем)",
        "image": "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?q=80&w=600&auto=format&fit=crop",
        "science": "<b>🎼 Научное обоснование:</b> Инструментальная music (фортепиано, скрипка) активирует одновременно оба полушария мозга. Повышает пластичность мышления и помогает находить нестандартные решения задач.",
        "ya": "https://music.yandex.ru/search?text=%D0%BD%D0%B5%D0%BE%D0%BA%D0%BB%D0%B0%D1%81%D1%81%D0%B8%D0%BA%D0%B0&utm_source=chatgpt.com",
        "yt": "https://youtu.be/R3xAbAVUxEM?si=Xses6twt6gRDhZ9i"
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

# Обработка нажатий на инлайн-кнопки жанров (Две новые кнопки: YouTube и Яндекс)
@bot.callback_query_handler(func=lambda call: call.data.startswith("mode_"))
def handle_genre_selection(call):
    genre_key = call.data.replace("mode_", "")
    
    if genre_key in TRACKS:
        data = TRACKS[genre_key]
        
        caption = f"<b>{data['title']}</b>\n\n{data['science']}\n\nСлушать на удобной платформе:"
        
        # Оставляем только две кнопки: YouTube и Яндекс.Музыка
        links_markup = types.InlineKeyboardMarkup(row_width=1)
        btn_yt = types.InlineKeyboardButton("📺 Смотреть на YouTube", url=data['yt'])
        btn_ya = types.InlineKeyboardButton("🎧 Слушать на Яндекс.Музыка", url=data['ya'])
        
        links_markup.add(btn_yt, btn_ya)
        
        try:
            bot.send_photo(
                call.message.chat.id, 
                photo=data['image'], 
                caption=caption, 
                parse_mode="html", 
                reply_markup=links_markup
            )
            bot.answer_callback_query(call.id)
        except Exception as e:
            print(f"Ошибка при отправке карточки: {e}", flush=True)
            bot.send_message(call.message.chat.id, caption, parse_mode="html", reply_markup=links_markup)
            bot.answer_callback_query(call.id)

# Бесконечный запуск бота (Long Polling)
print("=== БОТ УСПЕШНО ЗАПУЩЕН И ГОТОВ К РАБОТЕ ===", flush=True)
bot.polling(none_stop=True)
