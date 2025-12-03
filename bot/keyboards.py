from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Каталог"), KeyboardButton(text="💖 Вибране")],
            [KeyboardButton(text="🛒 Кошик")],
            [KeyboardButton(text="ℹ️ Про нас"), KeyboardButton(text="📞 Контакти")],
        ],
        resize_keyboard=True,
    )


def catalog_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧵 Худі"), KeyboardButton(text="👚 Футболки")],
            [KeyboardButton(text="🎽 Корсети"), KeyboardButton(text="🎀 Заколки")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )


def favorites_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛒 Перейти в кошик")],
            [KeyboardButton(text="🗑 Очистити вибране")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )


def cart_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✉️ Оформити у Telegram")],
            [KeyboardButton(text="📩 Оформити в Direct")],
            [KeyboardButton(text="🌐 Відкрити корзину на сайті")],
            [KeyboardButton(text="⬅️ Назад")],
        ],
        resize_keyboard=True,
    )


def product_inline_keyboard(product_id: int, product_url: str | None = None):
    buttons_row1 = [
        InlineKeyboardButton(
            text="💖 У вибране",
            callback_data=f"fav_add_{product_id}",
        ),
        InlineKeyboardButton(
            text="🧺 В кошик",
            callback_data=f"cart_add_{product_id}",
        ),
    ]

    inline_kb = InlineKeyboardMarkup(inline_keyboard=[buttons_row1])

    row2 = []
    if product_url:
        row2.append(
            InlineKeyboardButton(
                text="🌐 На сайт",
                url=product_url,
            )
        )

    row2.append(
        InlineKeyboardButton(
            text="📨 Написати адміну",
            url="https://t.me/kolo_sky_admin",
        )
    )

    inline_kb.inline_keyboard.append(row2)

    return inline_kb


def favorite_item_keyboard(product_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧺 В кошик",
                    callback_data=f"cart_add_{product_id}",
                ),
                InlineKeyboardButton(
                    text="❌ Прибрати",
                    callback_data=f"fav_remove_{product_id}",
                ),
            ]
        ]
    )
