from aiogram.types import *

def start_buttons():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Кандидат"), KeyboardButton(text="Работодатель")],
        ],
        resize_keyboard=True
    )