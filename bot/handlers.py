from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import FSInputFile

from bot.keyboards import (
    main_menu,
    catalog_menu,
    favorites_menu,
    cart_menu,
    product_inline_keyboard,
    favorite_item_keyboard,
)

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
#        МЕНЮ
# =========================
@router.message(lambda m: m.text == "🛍 Каталог")
async def catalog(message: types.Message):
    await message.answer("Оберіть категорію:", reply_markup=catalog_menu())


@router.message(lambda m: m.text == "⬅️ Назад")
async def back(message: types.Message):
    await message.answer("Повертаємось до меню:", reply_markup=main_menu())


# =========================
#   ПОКАЗ ТОВАРІВ ПО КАТЕГОРІЇ
# =========================
async def send_product_list(message: types.Message, category_id: int):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT id, name, description, price, main_image, product_url FROM products WHERE category_id=%s",
        (category_id,),
    )
    products = cur.fetchall()

    cur.close()
    conn.close()

    if not products:
        await message.answer("Поки немає товарів у цій категорії 💛")
        return

    for p in products:
        photo = FSInputFile(f"images/{p['main_image']}")
        caption_lines = [
            p["name"],
            f"💰 *{p['price']} грн*"
        ]

        if p.get("description"):
            caption_lines.append("")
            caption_lines.append(p["description"])

        caption = "\n".join(caption_lines)

        await message.answer_photo(
            photo,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=product_inline_keyboard(p["id"], p.get("product_url")),
        )


@router.message(lambda m: m.text in ["🧵 Худі", "👚 Футболки", "🎽 Корсети", "🎀 Заколки"])
async def show_products(message: types.Message):
    mapping = {
        "🧵 Худі": 1,
        "👚 Футболки": 2,
        "🎽 Корсети": 3,
        "🎀 Заколки": 4
    }
    category_id = mapping[message.text]
    await send_product_list(message, category_id)


# =========================
#        ВИБРАНЕ
# =========================
@router.message(lambda m: m.text == "💖 Вибране")
async def favorites(message: types.Message):
    telegram_id = message.from_user.id

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT p.*
        FROM favorites f
        JOIN users u ON u.id = f.user_id
        JOIN products p ON p.id = f.product_id
        WHERE u.telegram_id = %s
    """, (telegram_id,))

    items = cur.fetchall()
    cur.close()
    conn.close()

    if not items:
        await message.answer("У вас поки немає вибраних товарів 💛")
        return

    for p in items:
        photo = FSInputFile(f"images/{p['main_image']}")
        caption = f"{p['name']}\n💰 {p['price']} грн"
        if p['description']:
            caption += f"\n\n{p['description']}"

        await message.answer_photo(
            photo,
            caption=caption,
            reply_markup=favorite_item_keyboard(p["id"])
        )

    await message.answer("Що робимо далі? 🙂", reply_markup=favorites_menu())


# ОЧИСТИТИ ВИБРАНЕ
@router.message(lambda m: m.text == "🗑 Очистити вибране")
async def clear_favorites(message: types.Message):
    telegram_id = message.from_user.id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE telegram_id=%s", (telegram_id,))
    user = cur.fetchone()

    if user:
        user_id = user[0]
        cur.execute("DELETE FROM favorites WHERE user_id=%s", (user_id,))
        conn.commit()

    cur.close()
    conn.close()

    await message.answer("Вибране очищено 💛", reply_markup=main_menu())


# ДОДАТИ У ВИБРАНЕ
@router.callback_query(lambda c: c.data.startswith("fav_add_"))
async def fav_add(callback: types.CallbackQuery):
    product_id = int(callback.data.replace("fav_add_", ""))
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


# ВИДАЛИТИ З ВИБРАНОГО
@router.callback_query(lambda c: c.data.startswith("fav_remove_"))
async def fav_remove(callback: types.CallbackQuery):
    product_id = int(callback.data.replace("fav_remove_", ""))
    telegram_id = callback.from_user.id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE telegram_id=%s", (telegram_id,))
    user = cur.fetchone()

    if user:
        user_id = user[0]
        cur.execute(
            "DELETE FROM favorites WHERE user_id=%s AND product_id=%s",
            (user_id, product_id)
        )
        conn.commit()

    cur.close()
    conn.close()

    await callback.answer("❌ Видалено!")
    await callback.message.delete()


# =========================
#         КОШИК
# =========================
# ДОДАТИ В КОШИК
@router.callback_query(lambda c: c.data.startswith("cart_add_"))
async def add_to_cart(callback: types.CallbackQuery):
    product_id = int(callback.data.replace("cart_add_", ""))
    telegram_id = callback.from_user.id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE telegram_id=%s", (telegram_id,))
    user = cur.fetchone()

    if user:
        user_id = user[0]

        cur.execute(
            "SELECT quantity FROM cart_items WHERE user_id=%s AND product_id=%s",
            (user_id, product_id)
        )
        row = cur.fetchone()

        if row:
            qty = row[0] + 1
            cur.execute(
                "UPDATE cart_items SET quantity=%s WHERE user_id=%s AND product_id=%s",
                (qty, user_id, product_id)
            )
        else:
            cur.execute(
                "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                (user_id, product_id, 1)
            )

        conn.commit()

    cur.close()
    conn.close()

    await callback.answer("🧺 Додано в кошик!")


# ПОКАЗАТИ КОШИК
@router.message(lambda m: m.text in ["🛒 Кошик", "🛒 Перейти в кошик"])
async def show_cart(message: types.Message):
    telegram_id = message.from_user.id

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT p.id, p.name, p.price, ci.quantity
        FROM cart_items ci
        JOIN users u ON u.id = ci.user_id
        JOIN products p ON p.id = ci.product_id
        WHERE u.telegram_id = %s
    """, (telegram_id,))

    items = cur.fetchall()
    cur.close()
    conn.close()

    if not items:
        await message.answer("Ваш кошик порожній 🧺")
        return

    total = 0
    ids_for_url = []
    lines = ["🛒 *Ваш кошик:*", ""]

    for i, item in enumerate(items, start=1):
        subtotal = item["price"] * item["quantity"]
        total += subtotal
        ids_for_url.append(str(item["id"]))

        lines.append(
            f"{i}) {item['name']} — {item['price']} грн × {item['quantity']} = {subtotal} грн"
        )

    lines.append("")
    lines.append(f"Разом: *{total} грн*")

    cart_url = f"https://isdanchuk.github.io/Kolosky_Bot/cart/?ids={','.join(ids_for_url)}"
    lines.append("")
    lines.append(f"🌐 Переглянути на сайті:\n{cart_url}")

    await message.answer(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=cart_menu()
    )


# =========================
#      ОФОРМЛЕННЯ ЗАМОВЛЕННЯ
# =========================

@router.message(lambda m: m.text == "✉️ Оформити у Telegram")
async def order_tg(message: types.Message):
    await message.answer(
        "Щоб оформити замовлення, напишіть адміну:\n@kolo_sky_admin 💛\n\n"
        "Скопіюйте опис вашого кошика і надішліть йому 🌾"
    )


@router.message(lambda m: m.text == "📩 Оформити в Direct")
async def order_ig(message: types.Message):
    await message.answer(
        "Оформлення у Direct:\nhttps://instagram.com/kolo.sky 💛\n\n"
        "Скопіюйте опис кошика і надішліть нам 💛"
    )


@router.message(lambda m: m.text == "🌐 Відкрити корзину на сайті")
async def open_cart_site(message: types.Message):
    telegram_id = message.from_user.id

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT p.id
        FROM cart_items ci
        JOIN users u ON u.id = ci.user_id
        JOIN products p ON p.id = ci.product_id
        WHERE u.telegram_id = %s
    """, (telegram_id,))

    ids = [str(row[0]) for row in cur.fetchall()]

    cur.close()
    conn.close()

    if not ids:
        await message.answer("Кошик порожній 🧺")
        return

    cart_url = f"https://isdanchuk.github.io/Kolosky_Bot/cart/?ids={','.join(ids)}"
    await message.answer(f"🌐 Ваша корзина на сайті:\n{cart_url}")


# =========================
#     ПРО НАС
# =========================
@router.message(lambda m: m.text == "ℹ️ Про нас")
async def about(message: types.Message):
    await message.answer(
        "🌾 *KOLO.SKY* — український бренд етно-одягу.\n"
        "Ми створюємо унікальні вироби ручної роботи 💛",
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
        "📦 Замовлення оформлюються у Direct або Telegram 💛"
    )
