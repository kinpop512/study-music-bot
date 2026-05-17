import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from yandex_music import Client
import os

# 1. Подключение к Яндекс Музыке с проверкой токена
yandex_token = os.environ.get("YANDEX_TOKEN")

if yandex_token:
    # Явно указываем библиотеке, что передаем session_id
    ym_client = Client(session_id=yandex_token).init()
else:
    ym_client = Client().init()

# 2. Настройки бота
BOT_TOKEN = "8516159067:AAGVvZRnYjXwThNjqLFrzVwDXZgewwqnZ5M"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 3. Состояния для опроса
class QuizStates(StatesGroup):
    choosing_age = State()    # Шаг 1: Возраст
    choosing_subject = State() # Шаг 2: Предмет
    choosing_goal = State()    # Шаг 3: Цель

# 4. ИНТЕЛЛЕКТУАЛЬНАЯ МАТРИЦА ПЛЕЙЛИСТОВ
PLAYLISTS_MATRIX = {
    "7-13": {
        "concentration": "1115",  # Умный Лоу-фай
        "memorization": "1037",   # Эффект Моцарта
        "relaxation": "1132",     # Звуки природы
        "motivation": "1130"      # Видеоигровой саундтрек
    },
    "13-17": {
        "concentration": "1115",  # Фокус Лоу-фай
        "memorization": "1037",   # Классика для школы
        "relaxation": "1031",     # Легкий инди-эмбиент
        "motivation": "1052"      # Энергичный электронный фокус
    },
    "17+": {
        "concentration": "2220",  # Глубокий Эмбиент
        "memorization": "1037",   # Сложная классика
        "relaxation": "1132",     # Космический эмбиент
        "motivation": "1052"      # Мощный ритм для кодинга
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
    await state.update_data(age=user_age)
    
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

# --- ШАГ 3: ВЫБОР ЦЕЛИ ---
@dp.callback_query(QuizStates.choosing_subject, lambda c: c.data.startswith("subj_"))
async def process_subject(callback: types.CallbackQuery, state: FSMContext):
    user_subj = callback.data.split("_")[1]
    await state.update_data(subject=user_subj)
    
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
    
    user_data = await state.get_data()
    age = user_data.get("age", "13-17")
    subject = user_data.get("subject", "other")
    
    status_message = await callback.message.answer("🔄 Алгоритм анализирует параметры и подбирает треки...")
    
    try:
        # Получаем ID официального топ-плейлиста Яндекса
        playlist_id = PLAYLISTS_MATRIX[age][goal]
        
        # Исправленный метод запроса официальных подборок Яндекса
        playlist_data = ym_client.playlists_list(playlist_id)
        if not playlist_data:
            raise Exception("Не удалось загрузить плейлист")
            
        playlist = playlist_data[0]
        all_tracks = playlist.tracks
        
        # Забираем до 6 случайных треков из плейлиста
        random_tracks = random.sample(all_tracks, min(6, len(all_tracks)))
        
        goal_titles = {
            "memorization": "🧠 Плейлист для ЗАПОМИНАНИЯ",
            "concentration": "🎵 Плейлист для КОНЦЕНТРАЦИИ",
            "relaxation": "😌 Плейлист для РАССЛАБЛЕНИЯ",
            "motivation": "⚡ Плейлист для МОТИВАЦИИ"
        }
        
        subj_ru = subject.replace('math', 'Математика').replace('history', 'История').replace('literature', 'Литература').replace('languages', 'Языки').replace('other', 'Другое')
        
        # Перевели на HTML для полной безопасности верстки
        response_text = f"<b>{goal_titles.get(goal, '🎵 Музыкальный плейлист')}</b>\n\n"
        response_text += f"Эта подборка сгенерирована автоматически для возраста <b>{age}</b> под предмет <b>{subj_ru}</b>:\n\n"
        response_text += "⏱ Длительность: 30-60 минут\n"
        response_text += "📍 Рекомендуемые композиции:\n\n"
        
        for i, track_short in enumerate(random_tracks, 1):
            track = track_short.fetch_track()
            title = track.title
            artist = ", ".join([a.name for a in track.artists]) if track.artists else "Исполнитель"
            url = f"https://music.yandex.ru/album/{track.albums[0].id}/track/{track.id}"
            
            # Экранируем символы через HTML-теги для надежности
            response_text += f"{i}️⃣ {artist} — {title}\n🔗 <a href='{url}'>Слушать в Яндекс Музыке</a>\n\n"
            
        response_text += "💡 <i>Совет: Эта музыка активизирует области мозга, отвечающие за память и продуктивность.</i>"
        
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="🔄 Начать заново", callback_data="restart_quiz"))
        
        await status_message.delete()
        await callback.message.answer(
            response_text, 
            parse_mode="HTML", 
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
    try:
        await callback.message.delete()
    except:
        pass
    await cmd_start(callback.message, state)
    await callback.answer()

# --- ДОБАВКА ДЛЯ БЕСПЛАТНОГО ОБЛАКА RENDER ---
from aiohttp import web

async def handle(request):
    return web.Response(text="Бот работает!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
