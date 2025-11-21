from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile

from bot.keyboards import main_menu, catalog_menu, favorite_button
from bot.utils import register_user, get_products_by_category
from bot.db_connect import get_connection

router = Router()


def register_handlers(dp):
    dp.include_router(router)


# =========================
#        START
# =========================
@router.message(Command("start"))
async def start(message: types.Message):
    register_user(message.from_user.id, message.from_user.username)

    await message.answer(
        "Вітаємо у магазині 🌾 *Kolo.sky*!\n\nОбери меню нижче 👇",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )


# =========================
#        КАТАЛОГ
# =========================
@router.message(lambda m: m.text == "🛍 Каталог")
async def catalog(message: types.Message):
    await message.answer("Оберіть категорію:", reply_markup=catalog_menu())


@router.message(lambda m: m.text == "⬅️ Назад")
async def back(message: types.Message):
    await message.answer("Повертаємось до меню:", reply_markup=main_menu())


@router.message(lambda m: m.text in ["🧵 Худі", "👚 Футболки", "🎽 Корсети", "🎀 Заколки"])
async def show_products(message: types.Message):
    mapping = {
        "🧵 Худі": 1,
        "👚 Футболки": 2,
        "🎽 Корсети": 3,
        "🎀 Заколки": 4
    }
    category_id = mapping[message.text]

    products = get_products_by_category(category_id)

    if not products:
        await message.answer("Поки немає товарів у цій категорії 💛")
        return

    for p in products:
        photo = FSInputFile(f"images/{p['main_image']}")

        caption = (
            f"{p['name']}\n"
            f"💰 *{p['price']} грн*\n\n"
            f"{p['description']}"
        )

        await message.answer_photo(
            photo,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=favorite_button(p['id'])
        )


# =========================
#        ВИБРАНЕ
# =========================
@router.message(lambda m: m.text == "💖 Вибране")
async def favorites(message: types.Message):
    telegram_id = message.from_user.id

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT products.*
        FROM favorites
        JOIN users ON users.id = favorites.user_id
        JOIN products ON products.id = favorites.product_id
        WHERE users.telegram_id = %s
    """, (telegram_id,))

    items = cur.fetchall()
    cur.close()
    conn.close()

    if not items:
        await message.answer("У вас поки немає вибраних товарів 💛")
        return

    for p in items:
        photo = FSInputFile(f"images/{p['main_image']}")
        await message.answer_photo(
            photo,
            caption=f"💖 {p['name']} — {p['price']} грн"
        )


# =========================
#     ПРО НАС
# =========================
@router.message(lambda m: m.text == "ℹ️ Про нас")
async def about(message: types.Message):
    await message.answer(
        "🌾 *KOLO.SKY* — український бренд етно-одягу.\n"
        "Ми створюємо унікальні вироби ручної роботи, натхненні культурою та традиціями.\n\n"
        "Кожен товар — це любов, якість та стиль 💛",
        parse_mode="Markdown"
    )


# =========================
#     КОНТАКТИ
# =========================
@router.message(lambda m: m.text == "📞 Контакти")
async def contacts(message: types.Message):
    await message.answer(
        "📸 Instagram: https://www.instagram.com/kolo.sky\n"
        "📬 Telegram: @kolo_sky_admin\n"
        "📦 Замовлення оформлюються у директ в інстаграм або в телеграмі @kolo_sky_admin 💛"
    )


# =========================
#     CALLBACK: ADD TO FAV
# =========================
@router.callback_query(lambda c: c.data.startswith("fav_"))
async def add_to_fav(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    telegram_id = callback.from_user.id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE telegram_id=%s", (telegram_id,))
    user = cur.fetchone()

    if user:
        user_id = user[0]
        cur.execute(
            "INSERT IGNORE INTO favorites (user_id, product_id) VALUES (%s, %s)",
            (user_id, product_id)
        )
        conn.commit()

    cur.close()
    conn.close()

    await callback.answer("💖 Додано!")
