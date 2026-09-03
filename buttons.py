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
        buttons.append([
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_vac_{vacancy_id}"),
            InlineKeyboardButton(text="❌ Закрыть", callback_data=f"close_vac_{vacancy_id}")
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Этап 6: Кнопки для Поиска вакансий и Откликов ---

def candidate_menu():
    """Обновленное меню кандидата с кнопкой поиска"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мой профиль")],
            [KeyboardButton(text="Заполнить/Изменить профиль")],
            [KeyboardButton(text="🔍 Поиск вакансий"), KeyboardButton(text="Мои отклики")]
        ],
        resize_keyboard=True
    )

def vacancy_search_inline(vacancy_id: int, has_applied: bool = False):
    """Инлайн-клавиатура при просмотре вакансии кандидатом"""
    buttons = []
    if not has_applied:
        buttons.append([
            InlineKeyboardButton(text="📩 Откликнуться", callback_data=f"apply_vac_{vacancy_id}")
        ])
    else:
        buttons.append([
            InlineKeyboardButton(text="✅ Вы уже откликнулись", callback_data="already_applied")
        ])
    
    # Кнопки пагинации (перелистывания)
    buttons.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data=f"prev_vac_{vacancy_id}"),
        InlineKeyboardButton(text="Вперед ▶️", callback_data=f"next_vac_{vacancy_id}")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def employer_application_action_inline(application_id: int):
    """Инлайн-клавиатура для работодателя при получении отклика"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_app_{application_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_app_{application_id}")
            ]
        ]
    )