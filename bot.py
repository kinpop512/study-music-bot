import os
import telebot
from telebot import types

# Инициализируем бота через переменную окружения Amvera
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Ошибка: Переменная BOT_TOKEN не найдена в окружении Amvera!")

bot = telebot.TeleBot(BOT_TOKEN)

# Перевели базу на безопасный HTML-формат. Больше никаких падений из-за ссылок VK!
MUSIC_DATABASE = {
    "lofi": {
        "title": "☕ Lo-Fi Фокус (Состояние Потока)",
        "science": "<b>🧠 Научное обоснование:</b> Монотонный ритм (70-90 BPM) совпадает с альфа-ритмами мозга. Виниловый треск («розовый шум») блокирует резкие внешние раздражители, помогая войти в состояние глубокой концентрации.",
        "links": [
            "🎵 Lo-Fi Стрим для учебы и кода (VK): https://vk.com/video-215289466_456239105",
            "☕ Музыка для подготовки к экзаменам (RuTube): https://rutube.ru/video/98d75e848fa58882ca9f56a5c1bc2605/"
        ]
    },
    "phonk": {
        "title": "⚡ Дрифт-Фонк (Дофаминовый Буст)",
        "science": "<b>🔥 Научное обоснование:</b> Быстрый, энергичный ритм без слов стимулирует выработку дофамина. Отлично подходит для преодоления прокрастинации и выполнения рутинной, быстрой работы.",
        "links": [
            "🚗 Энергичный Phonk для продуктивности (VK): https://vk.com/video-106593457_456240112",
            "🛹 Фонк Микс без рекламы (RuTube): https://rutube.ru/video/73ba8de69cfcfbc54b659c231a4a49c4/"
        ]
    },
    "ambient": {
        "title": "🌌 Эмбиент и Чиллстеп (Релаксация и Антистресс)",
        "science": "<b>🌊 Научное обоснование:</b> Темп ниже 60 BPM снижает уровень кортизола (гормона стресса) и стабилизирует пульс. Полное отсутствие человеческой речи освобождает до 20% ресурсов рабочей памяти мозга.",
        "links": [
            "🌠 Космический Ambient для отдыха (VK): https://vk.com/video-172154622_456239451",
            "🌿 Расслабляющий эмбиент-плейлист (RuTube): https://rutube.ru/video/c18fb9958adfa6020c6a51241f81014a/"
        ]
    }
}

# Команда /start
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # Заменяем имя на безопасное, убирая спецсимволы HTML, если они есть в нике
    user_name = message.from_user.first_name.replace("<", "&lt;").replace(">", "&gt;")
    
    welcome_text = (
        f"Привет, <b>{user_name}</b>! 👋\n\n"
        "Я — <b>StudyTunesBot</b>, твой персональный нейро-музыкальный ассистент. "
        "Я помогаю подобрать идеальный фоновый звук, опираясь на исследования в области когнитивной психологии.\n\n"
        "Выбери режим, который тебе нужен прямо сейчас:"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_lofi = types.InlineKeyboardButton("☕ Фокус и Учеба (Lo-Fi)", callback_data="mode_lofi")
    btn_phonk = types.InlineKeyboardButton("⚡ Быстрый старт / Драйв (Phonk)", callback_data="mode_phonk")
    btn_ambient = types.InlineKeyboardButton("🌌 Снятие стресса / Отдых (Ambient)", callback_data="mode_ambient")
    
    markup.add(btn_lofi, btn_phonk, btn_ambient)
    bot.send_message(message.chat.id, welcome_text, parse_mode="html", reply_markup=markup)

# Обработка нажатий на кнопки
@bot.callback_query_handler(func=lambda call: call.data.startswith("mode_"))
def handle_music_request(call):
    mode_key = call.data.split("_")[1]
    data = MUSIC_DATABASE.get(mode_key)
    
    if data:
        response_text = f"=== <b>{data['title']}</b> ===\n\n{data['science']}\n\n<b>Рекомендуемые стримы и плейлисты (доступны в РФ):</b>\n"
        for link in data['links']:
            response_text += f"• {link}\n"
            
        markup = types.InlineKeyboardMarkup()
        btn_back = types.InlineKeyboardButton("⬅️ Назад к категориям", callback_data="go_to_menu")
        markup.add(btn_back)
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            text=response_text,
            parse_mode="html", # Переключили на HTML
            disable_web_page_preview=False,
            reply_markup=markup
        )

# Кнопка возврата в меню
@bot.callback_query_handler(func=lambda call: call.data == "go_to_menu")
def go_to_menu(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_lofi = types.InlineKeyboardButton("☕ Фокус и Учеба (Lo-Fi)", callback_data="mode_lofi")
    btn_phonk = types.InlineKeyboardButton("⚡ Быстрый старт / Драйв (Phonk)", callback_data="mode_phonk")
    btn_ambient = types.InlineKeyboardButton("🌌 Снятие стресса / Отдых (Ambient)", callback_data="mode_ambient")
    markup.add(btn_lofi, btn_phonk, btn_ambient)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        text="Выбери режим, который тебе нужен прямо сейчас:",
        reply_markup=markup
    )

# Запуск бота
if __name__ == "__main__":
    print("Бот успешно запущен на сервере Amvera...")
    bot.infinity_polling()
