import asyncio
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# ===== Конфигурация =====
BOT_TOKEN = '7265483449:AAHcydzBcNTUsh_BWVjfsF-BcDyHr7iox_Y'
BASE_URL = 'http://127.0.0.1:5000'

# ===== FSM состояния =====
class PollState(StatesGroup):
    waiting_for_poll_name = State()

# ===== Создание таблицы, если её нет =====
def init_db():
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS poll (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT UNIQUE,
                created_at TIMESTAMP
            )
        ''')
        conn.commit()

# ===== DB функции =====
def add_poll(topic: str):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO poll (topic, created_at) VALUES (?, ?)", (topic, datetime.now()))
        conn.commit()

def get_active_polls():
    cutoff = datetime.now() - timedelta(days=2)
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM poll WHERE created_at < ?", (cutoff,))
        cur.execute("SELECT topic, created_at FROM poll")
        return cur.fetchall()

# ===== Инициализация бота и диспетчера =====
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ===== Хендлеры =====

@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Создать опрос", callback_data="create_poll"),
            InlineKeyboardButton(text="📋 Доступные опросы", callback_data="show_polls")
        ]
    ])
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.callback_query(F.data.in_({"create_poll", "show_polls"}))
async def handle_callback(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "create_poll":
        await callback.message.answer("Введите тему опроса:")
        await state.set_state(PollState.waiting_for_poll_name)

    elif callback.data == "show_polls":
        polls = get_active_polls()
        if not polls:
            await callback.message.answer("Нет доступных опросов.")
            return

        for topic, _ in polls:
            link = f"{BASE_URL}/topic/{topic}"  # telegram_id убран
            await callback.message.answer(f"📌 *{topic}*\n🔗 {link}", parse_mode="Markdown")

@dp.message(PollState.waiting_for_poll_name)
async def receive_poll_name(message: types.Message, state: FSMContext):
    topic = message.text.strip().replace(" ", "_")
    add_poll(topic)
    link = f"{BASE_URL}/topic/{topic}"  # telegram_id убран
    await message.answer(f"Опрос создан!\n🔗 {link}")
    await state.clear()

# ===== Запуск бота =====
async def main():
    init_db()
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())





