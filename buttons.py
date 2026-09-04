from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

def start_buttons():
    kb = [
        [KeyboardButton(text="Кандидат"), KeyboardButton(text="Работодатель")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def candidate_menu():
    kb = [
        [KeyboardButton(text="Поиск вакансий")], [KeyboardButton(text="Мои отклики")],
        [KeyboardButton(text="Сохранённые вакансии")],
        [KeyboardButton(text="Заполнить/Изменить профиль")], [KeyboardButton(text="Мой профиль")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def employer_menu():
    kb = [
        [KeyboardButton(text="Мои вакансии"), KeyboardButton(text="Создать вакансию")],
        [KeyboardButton(text="Заполнить/Изменить компанию"), KeyboardButton(text="Мой профиль компании")]
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

def vacancy_action_inline(vacancy_id: int, is_saved: bool = False, is_closed: bool = False):
    keyboard = []
    first_row = []

    if not is_closed:
        first_row.append(InlineKeyboardButton(text="📩 Откликнуться", callback_data=f"vac_apply_{vacancy_id}"))

    if is_saved:
        first_row.append(InlineKeyboardButton(text="❌ Удалить из сохранённых", callback_data=f"vac_unsave_{vacancy_id}"))
    else:
        first_row.append(InlineKeyboardButton(text="⭐️ Сохранить", callback_data=f"vac_save_{vacancy_id}"))

    if first_row:
        keyboard.append(first_row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def employer_vacancies_inline(vacancies):
    keyboard = []
    for vac in vacancies:
        btn_text = f"📌 {vac['title']} (Откликов: {vac['applications_count']})"
        keyboard.append([InlineKeyboardButton(text=btn_text, callback_data=f"emp_vac_apps_{vac['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def candidate_action_inline(app_id: int, current_status: str):
    keyboard = [
        [
            InlineKeyboardButton(text="👤 Посмотреть профиль", callback_data=f"app_profile_{app_id}"),
            InlineKeyboardButton(text="📄 Анализ AI", callback_data=f"app_resume_{app_id}")
        ],
        [
            InlineKeyboardButton(text="🤝 Пригласить", callback_data=f"app_status_interview_{app_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"app_status_rejected_{app_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)