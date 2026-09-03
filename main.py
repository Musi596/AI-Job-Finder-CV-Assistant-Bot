import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from dotenv import load_dotenv

from buttons import (
    cancel_keyboard,
    candidate_action_inline,
    candidate_menu,
    confirm_keyboard,
    employer_menu,
    employer_vacancies_inline,
    start_buttons,
    vacancy_action_inline,
)
from sql import (
    create_application,
    create_tables,
    get_all_active_vacancies,
    get_application_by_id,
    get_applications_for_vacancy,
    get_candidate_applications,
    get_candidate_profile,
    get_employer_profile,
    get_employer_vacancies_with_app_count,
    get_saved_vacancies,
    is_already_applied,
    is_vacancy_saved,
    register_user,
    save_candidate_profile,
    save_employer_profile,
    save_vacancy,
    unsave_vacancy,
    update_application_status,
)

load_dotenv()
dp = Dispatcher()
bot = Bot(token=os.getenv("BOT_TOKEN"))

class CandidateFSM(StatesGroup):
    name = State()
    city = State()
    phone_number = State()
    desired_position = State()
    experience_level = State()
    skills = State()
    desired_salary = State()
    education = State()
    languages = State()
    experience = State()
    confirm = State()

class EmployerFSM(StatesGroup):
    company = State()
    industry = State()
    city = State()
    description = State()
    contact_information = State()
    confirm = State()

STATUS_TRANSLATIONS = {
    "submitted": "⏳ Отправлен",
    "reviewing": "👀 На рассмотрении",
    "interview": "🤝 Собеседование",
    "accepted": "✅ Принят",
    "rejected": "❌ Отклонен"
}

@dp.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять.", reply_markup=candidate_menu())
        return
    await state.clear()
    await message.answer("❌ Заполнение прервано. Возврат в главное меню.", reply_markup=candidate_menu())

@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Выберите роль:', reply_markup=start_buttons())

@dp.message(F.text == 'Кандидат')
async def select_candidate_role(message: Message, state: FSMContext):
    await register_user(message.from_user.id, 'Кандидат')
    profile = await get_candidate_profile(message.from_user.id)
    if profile:
        await message.answer("Вы вошли как Кандидат.", reply_markup=candidate_menu())
    else:
        await message.answer("Начнем заполнение анкеты кандидата!\n1/10. Введите ФИО:", reply_markup=cancel_keyboard())
        await state.set_state(CandidateFSM.name)

@dp.message(F.text == 'Работодатель')
async def select_employer_role(message: Message, state: FSMContext):
    await register_user(message.from_user.id, 'Работодатель')
    profile = await get_employer_profile(message.from_user.id)
    if profile:
        await message.answer("Вы вошли как Работодатель.", reply_markup=employer_menu())
    else:
        await message.answer("Начнем регистрацию компании!\n1/5. Введите название компании:", reply_markup=cancel_keyboard())
        await state.set_state(EmployerFSM.company)

@dp.message(F.text == "Заполнить/Изменить профиль")
async def start_candidate_fsm(message: Message, state: FSMContext):
    await message.answer('1/10. Введите полное имя (ФИО):', reply_markup=cancel_keyboard())
    await state.set_state(CandidateFSM.name)

@dp.message(CandidateFSM.name)
async def process_cand_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CandidateFSM.city)
    await message.answer('2/10. Укажите ваш город:', reply_markup=cancel_keyboard())

@dp.message(CandidateFSM.city)
async def process_cand_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(CandidateFSM.phone_number)
    await message.answer('3/10. Введите номер телефона или контактные данные:', reply_markup=cancel_keyboard())

@dp.message(CandidateFSM.phone_number)
async def process_cand_phone(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await state.set_state(CandidateFSM.desired_position)
    await message.answer('4/10. Укажите желаемую должность:', reply_markup=cancel_keyboard())

@dp.message(CandidateFSM.desired_position)
async def process_cand_position(message: Message, state: FSMContext):
    await state.update_data(desired_position=message.text)
    await state.set_state(CandidateFSM.experience_level)
    await message.answer('5/10. Укажите ваш уровень опыта (Junior / Middle / Senior):', reply_markup=cancel_keyboard())

@dp.message(CandidateFSM.experience_level)
async def process_cand_exp_level(message: Message, state: FSMContext):
    await state.update_data(experience_level=message.text)
    await state.set_state(CandidateFSM.skills)
    await message.answer('6/10. Перечислите ваши ключевые навыки:', reply_markup=cancel_keyboard())

@dp.message(CandidateFSM.skills)
async def process_cand_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(CandidateFSM.desired_salary)
    await message.answer('7/10. Укажите ожидаемую зарплату (цифрами):', reply_markup=cancel_keyboard())

@dp.message(CandidateFSM.desired_salary)
async def process_cand_salary(message: Message, state: FSMContext):
    await state.update_data(desired_salary=message.text)
    await state.set_state(CandidateFSM.education)
    await message.answer('8/10. Укажите ваше образование:', reply_markup=cancel_keyboard())

@dp.message(CandidateFSM.education)
async def process_cand_education(message: Message, state: FSMContext):
    await state.update_data(education=message.text)
    await state.set_state(CandidateFSM.languages)
    await message.answer('9/10. Укажите владение языками:', reply_markup=cancel_keyboard())

@dp.message(CandidateFSM.languages)
async def process_cand_languages(message: Message, state: FSMContext):
    await state.update_data(languages=message.text)
    await state.set_state(CandidateFSM.experience)
    await message.answer('10/10. Опишите ваш подробный опыт работы:', reply_markup=cancel_keyboard())

@dp.message(CandidateFSM.experience)
async def process_cand_experience(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    data = await state.get_data()
    
    result = (
        "*Проверьте данные профиля кандидата:*\n\n"
        f"1. *ФИО:* {data.get('name')}\n"
        f"2. *Город:* {data.get('city')}\n"
        f"3. *Контакты:* {data.get('phone_number')}\n"
        f"4. *Должность:* {data.get('desired_position')}\n"
        f"5. *Уровень:* {data.get('experience_level')}\n"
        f"6. *Навыки:* {data.get('skills')}\n"
        f"7. *Ожидаемая зарплата:* {data.get('desired_salary')}\n"
        f"8. *Образование:* {data.get('education')}\n"
        f"9. *Языки:* {data.get('languages')}\n"
        f"10. *Опыт работы:* {data.get('experience')}"
    )
    await state.set_state(CandidateFSM.confirm)
    await message.answer(result, parse_mode="Markdown", reply_markup=confirm_keyboard())

@dp.message(CandidateFSM.confirm, F.text == "Подтвердить")
async def confirm_candidate_profile(message: Message, state: FSMContext):
    data = await state.get_data()
    await save_candidate_profile(message.from_user.id, data)
    await state.clear()
    await message.answer("Профиль кандидата успешно сохранен в БД!", reply_markup=candidate_menu())

@dp.message(F.text == "Мой профиль")
async def show_candidate_profile(message: Message):
    profile = await get_candidate_profile(message.from_user.id)
    if not profile:
        await message.answer("Ваш профиль не найден. Пожалуйста, заполните его.")
        return
    
    result = (
        "*Ваш профиль кандидата:*\n\n"
        f"1. *ФИО:* {profile['name']}\n"
        f"2. *Город:* {profile['city']}\n"
        f"3. *Контакты:* {profile['phone_number']}\n"
        f"4. *Желаемая должность:* {profile['desired_position']}\n"
        f"5. *Уровень:* {profile['experience_level']}\n"
        f"6. *Навыки:* {profile['skills']}\n"
        f"7. *Зарплата:* {profile['desired_salary']}\n"
        f"8. *Образование:* {profile['education']}\n"
        f"9. *Языки:* {profile['languages']}\n"
        f"10. *Опыт работы:* {profile['experience']}"
    )
    await message.answer(result, parse_mode="Markdown")

@dp.message(F.text == "Поиск вакансий")
async def search_vacancies_handler(message: Message):
    vacancies = await get_all_active_vacancies()
    if not vacancies:
        await message.answer("На данный момент активных вакансий нет.", reply_markup=candidate_menu())
        return

    for vac in vacancies:
        is_saved = await is_vacancy_saved(message.from_user.id, vac['id'])
        card = (
            f"📌 *{vac['title']}*\n"
            f"🏢 Компания: {vac['company_name']}\n"
            f"📍 Город: {vac['city']}\n"
            f"💼 Тип: {vac['job_type']} ({vac['experience_level']})\n"
            f"💰 ЗП: {vac['salary_min']} - {vac['salary_max']}\n\n"
            f"🛠 *Навыки:* {vac['required_skills']}\n"
            f"📋 *Требования:* {vac['requirements']}"
        )
        await message.answer(
            card,
            parse_mode="Markdown",
            reply_markup=vacancy_action_inline(vac['id'], is_saved=is_saved, is_closed=False)
        )

@dp.callback_query(F.data.startswith("vac_save_"))
async def handle_save_vacancy(callback: CallbackQuery):
    vacancy_id = int(callback.data.split("_")[2])
    candidate_id = callback.from_user.id

    await save_vacancy(candidate_id, vacancy_id)
    await callback.answer("⭐️ Вакансия сохранена!", show_alert=True)
    await callback.message.edit_reply_markup(
        reply_markup=vacancy_action_inline(vacancy_id, is_saved=True, is_closed=False)
    )

@dp.callback_query(F.data.startswith("vac_unsave_"))
async def handle_unsave_vacancy(callback: CallbackQuery):
    vacancy_id = int(callback.data.split("_")[2])
    candidate_id = callback.from_user.id

    await unsave_vacancy(candidate_id, vacancy_id)
    await callback.answer("❌ Вакансия удалена из сохранённых.", show_alert=True)
    await callback.message.edit_reply_markup(
        reply_markup=vacancy_action_inline(vacancy_id, is_saved=False, is_closed=False)
    )

@dp.message(F.text == "Сохранённые вакансии")
async def show_saved_vacancies_handler(message: Message):
    saved_vacs = await get_saved_vacancies(message.from_user.id)
    if not saved_vacs:
        await message.answer("У вас нет сохранённых вакансий.", reply_markup=candidate_menu())
        return

    await message.answer("⭐️ *Ваши сохранённые вакансии:*", parse_mode="Markdown")
    for vac in saved_vacs:
        card = (
            f"📌 *{vac['title']}*\n"
            f"🏢 Компания: {vac['company_name']}\n"
            f"📍 Город: {vac['city']}\n"
            f"💼 Тип: {vac['job_type']} ({vac['experience_level']})\n"
            f"💰 ЗП: {vac['salary_min']} - {vac['salary_max']}\n\n"
            f"🛠 *Навыки:* {vac['required_skills']}\n"
            f"📋 *Требования:* {vac['requirements']}"
        )
        await message.answer(
            card,
            parse_mode="Markdown",
            reply_markup=vacancy_action_inline(vac['id'], is_saved=True, is_closed=(vac['status'] == 'closed'))
        )

@dp.callback_query(F.data.startswith("vac_apply_"))
async def apply_to_vacancy(callback: CallbackQuery):
    vacancy_id = int(callback.data.split("_")[2])
    candidate_id = callback.from_user.id

    if await is_already_applied(vacancy_id, candidate_id):
        await callback.answer("⚠️ Вы уже откликались на эту вакансию!", show_alert=True)
        return

    success = await create_application(vacancy_id, candidate_id)
    if success:
        await callback.answer("✅ Отклик успешно отправлен!", show_alert=True)
    else:
        await callback.answer("❌ Ошибка при отправке отклика.", show_alert=True)

@dp.message(F.text == "Мои отклики")
async def show_candidate_applications(message: Message):
    apps = await get_candidate_applications(message.from_user.id)
    if not apps:
        await message.answer("У вас пока нет активных откликов.", reply_markup=candidate_menu())
        return

    text = "📋 *Ваши отклики на вакансии:*\n\n"
    for app in apps:
        status_human = STATUS_TRANSLATIONS.get(app['status'], app['status'])
        date_str = app['created_at'].strftime("%d.%m.%Y %H:%M")
        text += (
            f"🏢 *{app['company_name']}* — {app['vacancy_title']}\n"
            f"📊 Статус: `{status_human}`\n"
            f"📅 Дата: {date_str}\n"
            f"-----------------------------------\n"
        )
    await message.answer(text, parse_mode="Markdown", reply_markup=candidate_menu())

@dp.message(F.text == "Заполнить/Изменить компанию")
async def start_employer_fsm(message: Message, state: FSMContext):
    await message.answer('1/5. Название компании:', reply_markup=cancel_keyboard())
    await state.set_state(EmployerFSM.company)

@dp.message(EmployerFSM.company)
async def process_emp_company(message: Message, state: FSMContext):
    await state.update_data(company=message.text)
    await state.set_state(EmployerFSM.industry)
    await message.answer('2/5. Отрасль компании:', reply_markup=cancel_keyboard())

@dp.message(EmployerFSM.industry)
async def process_emp_industry(message: Message, state: FSMContext):
    await state.update_data(industry=message.text)
    await state.set_state(EmployerFSM.city)
    await message.answer('3/5. Город:', reply_markup=cancel_keyboard())

@dp.message(EmployerFSM.city)
async def process_emp_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(EmployerFSM.description)
    await message.answer('4/5. Описание компании:', reply_markup=cancel_keyboard())

@dp.message(EmployerFSM.description)
async def process_emp_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(EmployerFSM.contact_information)
    await message.answer('5/5. Контактная информация:', reply_markup=cancel_keyboard())

@dp.message(EmployerFSM.contact_information)
async def process_emp_contact(message: Message, state: FSMContext):
    await state.update_data(contact_information=message.text)
    data = await state.get_data()
    
    result = (
        "*Проверьте данные профиля компании:*\n\n"
        f"1. *Компания:* {data.get('company')}\n"
        f"2. *Отрасль:* {data.get('industry')}\n"
        f"3. *Город:* {data.get('city')}\n"
        f"4. *Описание:* {data.get('description')}\n"
        f"5. *Контакты:* {data.get('contact_information')}"
    )
    await state.set_state(EmployerFSM.confirm)
    await message.answer(result, parse_mode="Markdown", reply_markup=confirm_keyboard())

@dp.message(EmployerFSM.confirm, F.text == "Подтвердить")
async def confirm_employer_profile(message: Message, state: FSMContext):
    data = await state.get_data()
    await save_employer_profile(message.from_user.id, data)
    await state.clear()
    await message.answer("Профиль компании сохранен в БД!", reply_markup=employer_menu())

@dp.message(F.text == "Мои вакансии")
async def show_employer_vacancies_apps(message: Message):
    vacancies = await get_employer_vacancies_with_app_count(message.from_user.id)
    if not vacancies:
        await message.answer("У вас пока нет созданных вакансий.", reply_markup=employer_menu())
        return

    await message.answer(
        "📋 *Ваши вакансии:* Нажмите на вакансию, чтобы просмотреть отклики.",
        parse_mode="Markdown",
        reply_markup=employer_vacancies_inline(vacancies)
    )

@dp.callback_query(F.data.startswith("emp_vac_apps_"))
async def list_vacancy_applications(callback: CallbackQuery):
    vacancy_id = int(callback.data.split("_")[3])
    apps = await get_applications_for_vacancy(vacancy_id)

    if not apps:
        await callback.answer("На эту вакансию пока нет откликов.", show_alert=True)
        return

    await callback.answer()
    await callback.message.answer(f"📥 *Откликов на вакансию: {len(apps)}*")

    for app in apps:
        matching_percent = "85%"
        status_human = STATUS_TRANSLATIONS.get(app['app_status'], app['app_status'])

        card = (
            f"👤 *Имя:* {app['name']}\n"
            f"🎯 *Процент соответствия:* `{matching_percent}`\n"
            f"💼 *Уровень опыта:* {app['experience_level']}\n"
            f"📊 *Статус:* {status_human}"
        )

        await callback.message.answer(
            card,
            parse_mode="Markdown",
            reply_markup=candidate_action_inline(app['app_id'], app['app_status'])
        )

@dp.callback_query(F.data.startswith("app_profile_"))
async def view_candidate_profile(callback: CallbackQuery):
    app_id = int(callback.data.split("_")[2])
    app = await get_application_by_id(app_id)

    if not app:
        await callback.answer("Отклик не найден.", show_alert=True)
        return

    if app['app_status'] in ['interview', 'accepted']:
        contact_info = app['phone_number']
    else:
        contact_info = "🔒 *Скрыто до приглашения на собеседование*"

    profile_text = (
        f"👤 *Профиль кандидата: {app['name']}*\n\n"
        f"📍 *Город:* {app['city']}\n"
        f"💼 *Уровень:* {app['experience_level']}\n"
        f"🎯 *Желаемая должность:* {app['desired_position']}\n"
        f"💰 *Ожидаемая ЗП:* {app['desired_salary']}\n"
        f"🎓 *Образование:* {app['education']}\n"
        f"🌐 *Языки:* {app['languages']}\n"
        f"📞 *Контакты:* {contact_info}"
    )

    await callback.answer()
    await callback.message.answer(profile_text, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("app_resume_"))
async def view_candidate_resume(callback: CallbackQuery):
    app_id = int(callback.data.split("_")[2])
    app = await get_application_by_id(app_id)

    if not app:
        await callback.answer("Отклик не найден.", show_alert=True)
        return

    resume_text = (
        f"📄 *Резюме и Опыт работы ({app['name']}):*\n\n"
        f"🛠 *Ключевые навыки:* {app['skills']}\n\n"
        f"📋 *Подробный опыт:* {app['experience']}"
    )

    await callback.answer()
    await callback.message.answer(resume_text, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("app_status_"))
async def change_application_status(callback: CallbackQuery):
    parts = callback.data.split("_")
    new_status = parts[2]
    app_id = int(parts[3])

    app = await get_application_by_id(app_id)
    if not app:
        await callback.answer("Отклик не найден.", show_alert=True)
        return

    success = await update_application_status(app_id, new_status)
    if success:
        if new_status == 'interview':
            await callback.answer("✅ Кандидат приглашен! Контакты открыты.", show_alert=True)
            try:
                await bot.send_message(
                    chat_id=app['candidate_id'],
                    text="🎉 Вас пригласили на собеседование!"
                )
            except Exception:
                pass
        elif new_status == 'rejected':
            await callback.answer("❌ Отклик отклонен.", show_alert=True)
            try:
                await bot.send_message(
                    chat_id=app['candidate_id'],
                    text="К сожалению, ваш отклик был отклонен."
                )
            except Exception:
                pass

        status_human = STATUS_TRANSLATIONS.get(new_status, new_status)
        await callback.message.edit_text(
            f"👤 *Имя:* {app['name']}\n"
            f"🎯 *Процент соответствия:* `85%`\n"
            f"💼 *Уровень опыта:* {app['experience_level']}\n"
            f"📊 *Статус:* {status_human}",
            parse_mode="Markdown",
            reply_markup=candidate_action_inline(app_id, new_status)
        )

async def main():
    await create_tables()
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as er:
        print(f"Ошибка запуска: {er}")