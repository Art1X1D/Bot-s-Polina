from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import os
from datetime import datetime

# === GOOGLE SHEETS INTEGRATION ===
try:
    import gspread
    from google.oauth2.service_account import Credentials
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet = client.open("theresgifts-stats").sheet1
    print("✅ Google Sheets подключён")
except Exception as e:
    print(f"⚠️ Google Sheets НЕ подключён: {e}")
    sheet = None

def log_to_sheet(user_id, action, category=None, url=None):
    if not sheet:
        return
    try:
        row = [
            datetime.now().isoformat(),
            str(user_id),
            action,
            category or "",
            url or ""
        ]
        sheet.append_row(row)
        print(f"📊 Запись в таблицу: {action} | {category}")
    except Exception as e:
        print(f"❌ Ошибка записи в Google Sheets: {e}")

# === TELEGRAM BOT SETUP ===
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

# 💝 Подарки — все URL очищены от пробелов
GIFTS = {
    "home": [
        {
            "photo": "https://optim.tildacdn.com/stor3533-3938-4764-b831-663332343431/-/format/webp/74328538.jpg.webp",
            "caption": "Уютный плед для дома 🏡",
            "url": "https://www.ozon.ru/product/fotofon-hromakey-1-5h2-metra-chernyy-606611928/?at=Rltyl7l9kFX2owV8CWlXGPRsJqAzBMtPpORxoFK7V1Rq"
        }
    ],
    "style": [
        {
            "photo": "https://ir.ozone.ru/s3/multimedia-1-h/7512943697.jpg",
            "caption": "Чёрный фон",
            "url": "https://www.ozon.ru/product/fotofon-hromakey-1-5h2-metra-chernyy-606611928/?at=Rltyl7l9kFX2owV8CWlXGPRsJqAzBMtPpORxoFK7V1Rq"
        }
    ],
    "hobbies": [
        {
            "photo": "https://optim.tildacdn.com/stor6638-3064-4331-b233-613063636338/-/format/webp/63972773.png.webp",
            "caption": "Бумажная камера со сменными кейсами",
            "url": "https://papershoot.ru/catalog"
        }
    ],
    "sport": [
        {
            "photo": "https://img-edg.joomcdn.net/eb767a9d1cf723fbc9cb3cd3682484a14a8ab921_original.jpeg",
            "caption": "Мягкая фляга для бега и походов",
            "url": "https://www.ozon.ru/product/myagkaya-flyaga-dlya-bega-i-pohodov-500ml-3486547021/?__rr=1&abt_att=1&origin_referer=www.bing.com"
        },
        {
            "photo": "https://ae04.alicdn.com/kf/S9c6601c12b87435abd95c850f1ca5db3k.jpg_640x640.jpg",
            "caption": "Ручной тренажер для большого тенниса",
            "url": "https://www.wildberries.ru/catalog/331956677/detail.aspx"
        }
    ],
    "health": [
        {
            "photo": "https://ae04.alicdn.com/kf/S9c6601c12b87435abd95c850f1ca5db3k.jpg_640x640.jpg",
            "caption": "Ручной тренажер для большого тенниса",
            "url": "https://www.wildberries.ru/catalog/331956677/detail.aspx"
        }
    ],
}

class GiftState(StatesGroup):
    choosing_category = State()
    showing_gifts = State()

def categories_kb():
    builder = InlineKeyboardBuilder()
    for key, label in CATEGORIES.items():
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
    log_to_sheet(message.from_user.id, "start")
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

    item = GIFTS[cat][0]
    try:
        media = InputMediaPhoto(media=item["photo"], caption=item["caption"])
        await callback.message.edit_media(media=media, reply_markup=gift_nav_kb(cat, 0, len(GIFTS[cat])))
        await state.update_data(category=cat, gifts=GIFTS[cat], gift_index=0)
        await state.set_state(GiftState.showing_gifts)
        log_to_sheet(callback.from_user.id, "category", category=cat)
    except Exception as e:
        print(f"Ошибка загрузки фото: {e}")
        await callback.answer("Не удалось загрузить подарок 😕", show_alert=True)

@router.callback_query(GiftState.showing_gifts, F.data.startswith("gift:"))
async def navigate_gifts(callback: CallbackQuery, state: FSMContext):
    _, cat, idx_str = callback.data.split(":")
    index = int(idx_str)
    gifts = GIFTS.get(cat, [])
    if index < 0 or index >= len(gifts):
        return

    item = gifts[index]
    try:
        media = InputMediaPhoto(media=item["photo"], caption=item["caption"])
        await callback.message.edit_media(media=media, reply_markup=gift_nav_kb(cat, index, len(gifts)))
        await state.update_data(gift_index=index)
        log_to_sheet(callback.from_user.id, "buy", category=cat, url=item["url"])
    except Exception as e:
        print(f"Ошибка при навигации: {e}")
        await callback.answer("Ошибка загрузки 😕", show_alert=True)

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
