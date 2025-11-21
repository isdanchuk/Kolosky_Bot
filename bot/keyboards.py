from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Каталог"), KeyboardButton(text="💖 Вибране")],
            [KeyboardButton(text="ℹ️ Про нас"), KeyboardButton(text="📞 Контакти")]
        ],
        resize_keyboard=True
    )


def catalog_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧵 Худі"), KeyboardButton(text="👚 Футболки")],
            [KeyboardButton(text="🎽 Корсети"), KeyboardButton(text="🎀 Заколки")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )


def favorite_button(product_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="💖 Додати у вибране",
                callback_data=f"fav_{product_id}"
            )]
        ]
    )
