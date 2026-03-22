from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🔑 ТОКЕН
BOT_TOKEN = "8279208591:AAFCjLhs7IKew1dPZc2O8WwKrJodkaX4T70"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# 🏷️ Категории
CATEGORIES = {
    "home": "🏡 Для дома",
    "sport": "⚽️ Спорт",
    "travel": "🗺️ Путешественникам",
    "hobbies": "🧩 Увлечения",
    "style": "👜 Стиль",
    "health": "🧘‍♀️ Здоровье и красота",
    "edible": "🥨 Съедобное",
    "experiences": "🧭 Впечатления",
    "pets": "🐶 Питомцы",
    "date": "🍸 Куда сводить",
}

# 💝 Подарки — ВСЕГДА список словарей!
GIFTS = {
    "home": [
        {
            "photo": "https://ir.ozone.ru/s3/multimedia-1-h/7512943697.jpg",
            "caption": "Уютный плед для дома 🏡",
            "url": "https://t.me/pike_msk_bot?start=home_1"
        }
    ],
    "sport": [
        {
            "photo": "https://ir.ozone.ru/s3/multimedia-1-h/7512943697.jpg",
            "caption": "Спортивная бутылка для воды ⚽️",
            "url": "https://t.me/pike_msk_bot?start=sport_1"
        }
    ],
    "travel": [
        {
            "photo": "https://ir.ozone.ru/s3/multimedia-1-h/7512943697.jpg",
            "caption": "Складной чемодан для путешествий 🗺️",
            "url": "https://t.me/pike_msk_bot?start=travel_1"
        }
    ],
    "hobbies": [
        {
            "photo": "https://ir.ozone.ru/s3/multimedia-1-h/7512943697.jpg",
            "caption": "Набор для творчества 🧩",
            "url": "https://t.me/pike_msk_bot?start=hobbies_1"
        }
    ],
    "style": [
        {
            "photo": "https://ir.ozone.ru/s3/multimedia-1-h/7512943697.jpg",
            "caption": "Чёрный фон",
            "url": "https://t.me/pike_msk_bot?start=style_1"
        }
    ],
    "health": [
        {
            "photo": "https://ir.ozone.ru/s3/multimedia-1-h/7512943697.jpg",
            "caption": "Массажер для шеи 🧘‍♀️",
            "url": "https://t.me/pike_msk_bot?start=health_1"
        }
    ],
    "edible": [
        {
            "photo": "https://ir.ozone.ru/s3/multimedia-1-h/7512943697.jpg",
            "caption": "Подарочный набор пекаря 🥨",
            "url": "https://t.me/pike_msk_bot?start=edible_1"
        }
    ],
    "experiences": [
        {
            "photo": "https://ir.ozone.ru/s3/multimedia-1-h/7512943697.jpg",
            "caption": "Сертификат на мастер-класс 🧭",
            "url": "https://t.me/pike_msk_bot?start=experiences_1"
        }
    ],
    "pets": [
        {
            "photo": "https://ir.ozone.ru/s3/multimedia-1-h/7512943697.jpg",
            "caption": "Игрушка для собаки 🐶",
            "url": "https://t.me/pike_msk_bot?start=pets_1"
        }
    ],
    "date": [
        {
            "photo": "https://ir.ozone.ru/s3/multimedia-1-h/7512943697.jpg",
            "caption": "Сертификат в романтическое кафе 🍸",
            "url": "https://t.me/pike_msk_bot?start=date_1"
        }
    ],
}

class GiftState(StatesGroup):
    choosing_category = State()
    showing_gifts = State()

def categories_kb():
    builder = InlineKeyboardBuilder()
    for key, label in CATEGORIES.items():
        builder.button(text=label, callback_data=f"cat:{key}")
    builder.adjust(2)
    return builder.as_markup()

def gift_nav_kb(category: str, index: int, total: int):
    builder = InlineKeyboardBuilder()
    if index > 0:
        builder.button(text="🔙 Назад", callback_data=f"gift:{category}:{index-1}")
    builder.button(text="💳 Купить", url=GIFTS[category][index]["url"])
    if index < total - 1:
        builder.button(text="▶️ Вперёд", callback_data=f"gift:{category}:{index+1}")
    builder.button(text="🏠 Главное меню", callback_data="main_menu")
    
    # Настройка кнопок: максимум 2 в первой строке (навигация), остальное — отдельно
    if total == 1:
        builder.adjust(1, 1)
    elif index == 0 or index == total - 1:
        builder.adjust(2, 1)
    else:
        builder.adjust(2, 1, 1)
    return builder.as_markup()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Это бот Telegram-канала «Что тебе подарить?». "
        "Здесь есть добрые и нужные подарки на весь год 🪄\n\n"
        "Какой ищем подарок?",
        reply_markup=categories_kb()
    )
    await state.set_state(GiftState.choosing_category)

@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "Привет! Это бот Telegram-канала «Что тебе подарить?». "
        "Здесь есть добрые и нужные подарки на весь год 🪄\n\n"
        "Какой ищем подарок?",
        reply_markup=categories_kb()
    )
    await state.set_state(GiftState.choosing_category)

@router.callback_query(GiftState.choosing_category, F.data.startswith("cat:"))
async def show_first_gift(callback: CallbackQuery, state: FSMContext):
    cat = callback.data.split(":")[1]
    gifts = GIFTS.get(cat, [])
    if not gifts:
        await callback.answer("Подарков пока нет 😢", show_alert=True)
        return

    await state.update_data(category=cat, gifts=gifts, gift_index=0)
    await state.set_state(GiftState.showing_gifts)

    item = gifts[0]
    media = InputMediaPhoto(media=item["photo"], caption=item["caption"])
    await callback.message.edit_media(media=media, reply_markup=gift_nav_kb(cat, 0, len(gifts)))

@router.callback_query(GiftState.showing_gifts, F.data.startswith("gift:"))
async def navigate_gifts(callback: CallbackQuery, state: FSMContext):
    _, cat, idx_str = callback.data.split(":")
    index = int(idx_str)
    gifts = GIFTS[cat]
    if index < 0 or index >= len(gifts):
        return

    item = gifts[index]
    media = InputMediaPhoto(media=item["photo"], caption=item["caption"])
    await state.update_data(gift_index=index)
    await callback.message.edit_media(media=media, reply_markup=gift_nav_kb(cat, index, len(gifts)))

async def main():
    print("✅ Бот запущен!")
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал Ctrl+C. Завершаем...")
    finally:
        await bot.session.close()
        print("👋 Бот остановлен.")

if __name__ == "__main__":
    asyncio.run(main())
