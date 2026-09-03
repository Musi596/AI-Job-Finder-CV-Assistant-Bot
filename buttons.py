from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

def start_buttons():
    kb = [
        [KeyboardButton(text="Кандидат"), KeyboardButton(text="Работодатель")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def candidate_menu():
    kb = [
        [KeyboardButton(text="Поиск вакансий"), KeyboardButton(text="Мои отклики")],
        [KeyboardButton(text="Заполнить/Изменить профиль"), KeyboardButton(text="Мой профиль")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def employer_menu():
    kb = [
        [KeyboardButton(text="Мои вакансии"), KeyboardButton(text="Создать вакансию")],
        [KeyboardButton(text="Заполнить/Изменить компанию"), KeyboardButton(text="Профиль компании")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def cancel_keyboard():
    kb = [[KeyboardButton(text="❌ Отмена")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def confirm_keyboard():
    kb = [
        [KeyboardButton(text="Подтвердить")],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def vacancy_action_inline(vacancy_id: int, is_closed: bool = False):
    buttons = []
    if not is_closed:
        buttons.append([InlineKeyboardButton(text="📩 Откликнуться", callback_data=f"vac_apply_{vacancy_id}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)