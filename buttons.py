from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def start_buttons():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Кандидат"), KeyboardButton(text="Работодатель")]
        ],
        resize_keyboard=True
    )

def candidate_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мой профиль")],
            [KeyboardButton(text="Заполнить/Изменить профиль")]
        ],
        resize_keyboard=True
    )

def employer_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Профиль компании")],
            [KeyboardButton(text="Заполнить/Изменить компанию")],
            [KeyboardButton(text="Создать вакансию"), KeyboardButton(text="Мои вакансии")]
        ],
        resize_keyboard=True
    )

def confirm_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подтвердить"), KeyboardButton(text="Заполнить заново")]
        ],
        resize_keyboard=True
    )

def vacancy_status_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Опубликовать (active)"), KeyboardButton(text="Сохранить как черновик (draft)")]
        ],
        resize_keyboard=True
    )

def vacancy_action_inline(vacancy_id: int, is_closed: bool = False):
    buttons = []
    if not is_closed:
        buttons.append([InlineKeyboardButton(text="❌ Закрыть вакансию", callback_data=f"close_vac_{vacancy_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)