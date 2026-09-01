from aiogram.types import *

def start_buttons():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Я кандидат"), KeyboardButton(text="Я работодатель")],
        ],
        resize_keyboard=True
    )