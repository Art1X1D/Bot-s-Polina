from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import os

# 🔑 Получаем токен из переменной окружения (для Railway/Render)
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Переменная окружения BOT_TOKEN не задана!")

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

# 💝 Подарки — только заполненные категории
GIFTS = {
    "home": [
        {
            "photo": "https://ir.ozone.ru/s3/multimedia-1-h/7512943697.jpg",
            "caption": "Уютный плед для дома 🏡",
            "url": "https://t.me/pike_msk_bot?start=home_1"
        }
    ],
    "style": [
        {
            "photo": "https://ir.ozone.ru/s3/multimedia-1-h/7512943697.jpg",
            "caption": "Чёрный фон",
            "url": "https://t.me/pike_msk_bot?start=style_1"
        }
    ],
    "hobbies": [
        {
            "photo": "https://papershoot.ru/paper-camera/tproduct/1208941196-929640940941-vintage-1925",
            "caption": "Бумажная камера со сменными кейсами",
            "url": "https://papershoot.ru/catalog"
        }
    ],
    "sport": [
        {
            "photo": "https://market.yandex.ru/card/flyaga-silikonovaya-myagkaya-s-remeshkom-dlya-gidratora-dlya-bega-500ml",
            "caption": "Мягкая фляга для бега и походов",
            "url": "https://market.yandex.ru/card/flyaga-silikonovaya-myagkaya-s-remeshkom-dlya-gidratora-dlya-bega-500ml"
        }
    ],
    "health": [
        {
            "photo": "https://aliexpress.ru/item/1005006255577739.html",
            "caption": "Ручной тренажер для большого тенниса",
            "url": "https://www.wildberries.ru/catalog/331956677/detail.aspx"
        }
    ],
    # Остальные категории можно добавить позже
}

class GiftState(StatesGroup):
    choosing_category = State()
    showing_gifts = State()

def categories_kb():
    builder = InlineKeyboardBuilder()
    for key, label in CATEGORIES.items():
        # Показываем только категории, где есть подарки
        if key in GIFTS and GIFTS[key]:
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
    if cat not in GIFTS or not GIFTS[cat]:
        await callback.answer("Подарков в этой категории пока нет 😢", show_alert=True)
        return

    await state.update_data(category=cat, gifts=GIFTS[cat], gift_index=0)
    await state.set_state(GiftState.showing_gifts)

    item = GIFTS[cat][0]
    media = InputMediaPhoto(media=item["photo"], caption=item["caption"])
    await callback.message.edit_media(media=media, reply_markup=gift_nav_kb(cat, 0, len(GIFTS[cat])))

@router.callback_query(GiftState.showing_gifts, F.data.startswith("gift:"))
async def navigate_gifts(callback: CallbackQuery, state: FSMContext):
    _, cat, idx_str = callback.data.split(":")
    index = int(idx_str)
    gifts = GIFTS.get(cat, [])
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
