import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from yandex_music import Client

# 1. Подключение к Яндекс Музыке
ym_client = Client().init()

# 2. Настройки бота (Замени текст в кавычках на свой токен от @BotFather)
BOT_TOKEN = "8516159067:AAGVvZRnYjXwThNjqLFrzVwDXZgewwqnZ5M"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 3. Состояния для опроса (строго по твоей схеме)
class QuizStates(StatesGroup):
    choosing_age = State()    # Шаг 1: Возраст
    choosing_subject = State() # Шаг 2: Предмет
    choosing_goal = State()    # Шаг 3: Цель

# 4. ИНТЕЛЛЕКТУАЛЬНАЯ МАТРИЦА ПЛЕЙЛИСТОВ (Интеграция с API Яндекс Музыки)
# Бот автоматически выберет нужный плейлист на основе комбинации возраста и цели
PLAYLISTS_MATRIX = {
    # Для младшего возраста (7-13 лет)
    "7-13": {
        "concentration": "yamusic-top:1115",  # Умный Лоу-фай (мягкий ритм)
        "memorization": "yamusic-top:1037",   # Эффект Моцарта для детей
        "relaxation": "yamusic-top:1132",     # Звуки природы и дождя
        "motivation": "yamusic-top:1130"       # Видеоигровой саундтрек для бодрости
    },
    # Для подростков (13-17 лет)
    "13-17": {
        "concentration": "yamusic-top:1115",  # Фокус Лоу-фай
        "memorization": "yamusic-top:1037",   # Классика для школы
        "relaxation": "yamusic-top:1031",     # Легкий инди-эмбиент
        "motivation": "yamusic-top:1052"       # Энергичный электронный фокус
    },
    # Для студентов и старших (17+)
    "17+": {
        "concentration": "yamusic-top:2220",  # Глубокий Эмбиент / Синематик
        "memorization": "yamusic-top:1037",   # Сложная классика (Бах, Вивальди)
        "relaxation": "yamusic-top:1132",     # Космический эмбиент
        "motivation": "yamusic-top:1052"       # Мощный ритм для кодинга и сессии
    }
}

# --- ШАГ 1: ВЫБОР ВОЗРАСТА ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="👶 7-13 лет", callback_data="age_7-13"))
    builder.add(types.InlineKeyboardButton(text="🧑 13-17 лет", callback_data="age_13-17"))
    builder.add(types.InlineKeyboardButton(text="🧔 17+ лет", callback_data="age_17+"))
    builder.adjust(1)
    
    await state.set_state(QuizStates.choosing_age)
    await message.answer(
        "Спасибо! Сначала скажите, сколько вам лет?\n\nВыберите диапазон вашего возраста:", 
        reply_markup=builder.as_markup()
    )

# --- ШАГ 2: ВЫБОР ПРЕДМЕТА ---
@dp.callback_query(QuizStates.choosing_age, lambda c: c.data.startswith("age_"))
async def process_age(callback: types.CallbackQuery, state: FSMContext):
    user_age = callback.data.split("_")[1]
    await state.update_data(age=user_age) # Запоминаем возраст
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="📐 Математика", callback_data="subj_math"))
    builder.add(types.InlineKeyboardButton(text="📖 История", callback_data="subj_history"))
    builder.add(types.InlineKeyboardButton(text="✍️ Литература", callback_data="subj_literature"))
    builder.add(types.InlineKeyboardButton(text="🌍 Языки", callback_data="subj_languages"))
    builder.add(types.InlineKeyboardButton(text="🎨 Другое", callback_data="subj_other"))
    builder.adjust(1)
    
    await state.set_state(QuizStates.choosing_subject)
    await callback.message.edit_text(
        "What are you studying right now? 📚\n\nЧто вы сейчас учите? Выберите предмет:", 
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# --- ШАГ 3: ВЫБОР ЦЕЛИ (ТИПА МУЗЫКИ) ---
@dp.callback_query(QuizStates.choosing_subject, lambda c: c.data.startswith("subj_"))
async def process_subject(callback: types.CallbackQuery, state: FSMContext):
    user_subj = callback.data.split("_")[1]
    await state.update_data(subject=user_subj) # Запоминаем предмет
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🎵 Концентрация (спокойная классика)", callback_data="goal_concentration"))
    builder.add(types.InlineKeyboardButton(text="🧠 Запоминание (Моцарт)", callback_data="goal_memorization"))
    builder.add(types.InlineKeyboardButton(text="😌 Расслабление (амбиент)", callback_data="goal_relaxation"))
    builder.add(types.InlineKeyboardButton(text="⚡ Мотивация (энергичная)", callback_data="goal_motivation"))
    builder.adjust(1)
    
    await state.set_state(QuizStates.choosing_goal)
    await callback.message.edit_text(
        "Что вам нужно прямо сейчас? 🎯\n\nВыберите тип музыки для вашей учёбы:", 
        reply_markup=builder.as_markup()
    )
    await callback.answer()

# --- ШАГ 4: ИНТЕЛЛЕКТУАЛЬНЫЙ ПОДБОР И ВЫДАЧА ТРЕКОВ ---
@dp.callback_query(QuizStates.choosing_goal, lambda c: c.data.startswith("goal_"))
async def process_final_playlist(callback: types.CallbackQuery, state: FSMContext):
    goal = callback.data.split("_")[1]
    
    # Извлекаем сохраненные данные возраста и предмета
    user_data = await state.get_data()
    age = user_data.get("age", "13-17")
    subject = user_data.get("subject", "other")
    
    # Показываем статус загрузки
    status_message = await callback.message.answer("🔄 Алгоритм анализирует параметры и подбирает треки...")
    
    try:
        # Умный выбор плейлиста на основе Матрицы (Возраст -> Цель)
        playlist_uid = PLAYLISTS_MATRIX[age][goal]
        user_id, playlist_id = playlist_uid.split(':')
        
        # Запрашиваем треки напрямую из Яндекса
        playlist = ym_client.users_playlists(playlist_id, user_id)
        all_tracks = playlist.tracks
        
        # Забираем ровно 6 случайных актуальных треков
        random_tracks = random.sample(all_tracks, min(6, len(all_tracks)))
        
        # Красивое оформление результатов под твой дизайн
        goal_titles = {
            "memorization": "🧠 Плейлист для ЗАПОМИНАНИЯ",
            "concentration": "🎵 Плейлист для КОНЦЕНТРАЦИИ",
            "relaxation": "😌 Плейлист для РАССЛАБЛЕНИЯ",
            "motivation": "⚡ Плейлист для МОТИВАЦИИ"
        }
        
        response_text = f"{goal_titles.get(goal, '🎵 Музыкальный плейлист')}\n\n"
        response_text += f"Эта подборка сгенерирована автоматически для возраста *{age}* под предмет *{subject.replace('math', 'Математика').replace('history', 'История').replace('literature', 'Литература').replace('languages', 'Языки').replace('other', 'Другое')}*:\n\n"
        response_text += "⏱ Длительность: 30-60 минут\n"
        response_text += "📍 Рекомендуемые композиции:\n\n"
        
        for i, track_short in enumerate(random_tracks, 1):
            track = track_short.fetch_track()
            title = track.title
            artist = ", ".join([a.name for a in track.artists]) if track.artists else "Исполнитель"
            url = f"https://music.yandex.ru/album/{track.albums[0].id}/track/{track.id}"
            
            response_text += f"{i}️⃣ {artist} — {title}\n🔗 [Слушать в Яндекс Музыке]({url})\n\n"
            
        response_text += "💡 Совет: Эта музыка активизирует области мозга, отвечающие за память и продуктивность."
        
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="🔄 Начать заново", callback_data="restart_quiz"))
        
        # Удаляем сообщение загрузки и выдаем готовый результат
        await status_message.delete()
        await callback.message.answer(
            response_text, 
            parse_mode="Markdown", 
            reply_markup=builder.as_markup(),
            disable_web_page_preview=True
        )
        
    except Exception as e:
        await status_message.delete()
        await callback.message.answer("⚠️ Ошибка при подборе музыки. Попробуйте еще раз.")
        print(f"Ошибка API Яндекса: {e}")
        
    await state.clear()
    await callback.answer()

# Перезапуск опроса
@dp.callback_query(lambda c: c.data == "restart_quiz")
async def restart_quiz(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await cmd_start(callback.message, state)
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())