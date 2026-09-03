import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv

from buttons import *
from sql import create_tables
import services

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=MemoryStorage())

# --- FSM Классы ---

class CandidateProfileFSM(StatesGroup):
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

class EmployerProfileFSM(StatesGroup):
    company = State()
    industry = State()
    city = State()
    description = State()
    contact_information = State()

class VacancyFSM(StatesGroup):
    title = State()
    city = State()
    job_type = State()
    experience_level = State()
    salary_min = State()
    salary_max = State()
    required_skills = State()
    requirements = State()
    confirm = State()

class CVUploadFSM(StatesGroup):
    wait_file = State()

# --- Системные и общие хэндлеры ---

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Добро пожаловать! Выберите вашу роль:", reply_markup=start_buttons())

@dp.message(F.text == "❌ Отмена")
async def process_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=start_buttons())

# --- Роли ---

@dp.message(F.text == "Кандидат")
async def select_candidate(message: Message):
    await services.register_candidate(message.from_user.id)
    await message.answer("Вы вошли как Кандидат.", reply_markup=candidate_menu())

@dp.message(F.text == "Работодатель")
async def select_employer(message: Message):
    await services.register_employer(message.from_user.id)
    await message.answer("Вы вошли как Работодатель.", reply_markup=employer_menu())

# --- Профиль Кандидата ---

@dp.message(F.text == "Мой профиль")
async def show_candidate_profile(message: Message):
    profile = await services.fetch_candidate(message.from_user.id)
    if not profile:
        await message.answer("Профиль не заполнен. Нажмите 'Заполнить/Изменить профиль'.")
        return
    
    text = (
        f"👤 *Имя:* {profile['name']}\n"
        f"📍 *Город:* {profile['city']}\n"
        f"📞 *Телефон:* {profile['phone_number']}\n"
        f"💼 *Желаемая должность:* {profile['desired_position']}\n"
        f"📊 *Уровень:* {profile['experience_level']}\n"
        f"💰 *Ожидаемая ЗП:* {profile['desired_salary']} USD\n"
        f"🛠 *Навыки:* {profile['skills']}\n"
        f"🎓 *Образование:* {profile['education']}\n"
        f"🌐 *Языки:* {profile['languages']}\n"
        f"📝 *Опыт:* {profile['experience']}"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=candidate_menu())

@dp.message(F.text == "Заполнить/Изменить профиль")
async def start_cand_profile(message: Message, state: FSMContext):
    await state.set_state(CandidateProfileFSM.name)
    await message.answer("Введите ваше полное имя:", reply_markup=cancel_keyboard())

@dp.message(CandidateProfileFSM.name)
async def process_cand_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CandidateProfileFSM.city)
    await message.answer("Укажите ваш город:")

@dp.message(CandidateProfileFSM.city)
async def process_cand_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(CandidateProfileFSM.phone_number)
    await message.answer("Укажите контактный номер телефона:")

@dp.message(CandidateProfileFSM.phone_number)
async def process_cand_phone(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await state.set_state(CandidateProfileFSM.desired_position)
    await message.answer("Желаемая должность (например: Python Backend Developer):")

@dp.message(CandidateProfileFSM.desired_position)
async def process_cand_pos(message: Message, state: FSMContext):
    await state.update_data(desired_position=message.text)
    await state.set_state(CandidateProfileFSM.experience_level)
    await message.answer("Ваш уровень (Junior, Middle, Senior):")

@dp.message(CandidateProfileFSM.experience_level)
async def process_cand_exp_lvl(message: Message, state: FSMContext):
    await state.update_data(experience_level=message.text)
    await state.set_state(CandidateProfileFSM.skills)
    await message.answer("Ваши ключевые навыки (через запятую):")

@dp.message(CandidateProfileFSM.skills)
async def process_cand_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(CandidateProfileFSM.desired_salary)
    await message.answer("Ожидаемая зарплата (только число):")

@dp.message(CandidateProfileFSM.desired_salary)
async def process_cand_salary(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите корректное число.")
        return
    await state.update_data(desired_salary=message.text)
    await state.set_state(CandidateProfileFSM.education)
    await message.answer("Образование:")

@dp.message(CandidateProfileFSM.education)
async def process_cand_edu(message: Message, state: FSMContext):
    await state.update_data(education=message.text)
    await state.set_state(CandidateProfileFSM.languages)
    await message.answer("Владение языками:")

@dp.message(CandidateProfileFSM.languages)
async def process_cand_lang(message: Message, state: FSMContext):
    await state.update_data(languages=message.text)
    await state.set_state(CandidateProfileFSM.experience)
    await message.answer("Кратко опишите ваш коммерческий/проектный опыт:")

@dp.message(CandidateProfileFSM.experience)
async def process_cand_exp(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    data = await state.get_data()
    await services.store_candidate_profile(message.from_user.id, data)
    await state.clear()
    await message.answer("Профиль успешно сохранен!", reply_markup=candidate_menu())

# --- Загрузка Резюме (.txt) ---

@dp.message(F.text == "📄 Загрузить резюме (TXT)")
async def start_cv_upload(message: Message, state: FSMContext):
    await state.set_state(CVUploadFSM.wait_file)
    await message.answer("Отправьте ваш файл резюме в формате **.txt**:", reply_markup=cancel_keyboard())

@dp.message(CVUploadFSM.wait_file, F.document)
async def process_cv_file(message: Message, state: FSMContext):
    doc = message.document
    if not doc.file_name.endswith('.txt'):
        await message.answer("Ошибка! Пожалуйста, отправьте файл в формате .txt")
        return

    os.makedirs("cv_uploads", exist_ok=True)
    file_path = f"cv_uploads/{message.from_user.id}_{doc.file_name}"
    
    file_info = await bot.get_file(doc.file_id)
    await bot.download_file(file_info.file_path, destination=file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception:
        with open(file_path, "r", encoding="cp1251", errors="ignore") as f:
            text = f.read()

    await services.store_cv_file(message.from_user.id, file_path, doc.file_name, text)
    await state.clear()
    await message.answer("📄 Текст резюме успешно прочитан и сохранен!", reply_markup=candidate_menu())

# --- Поиск и Отклики ---

@dp.message(F.text == "Поиск вакансий")
async def search_vacancies(message: Message):
    vacancies = await services.fetch_active_vacancies()
    if not vacancies:
        await message.answer("Активных вакансий пока нет.")
        return

    for v in vacancies:
        is_saved = await services.check_is_saved(message.from_user.id, v['id'])
        msg = (
            f"🏢 *{v['company_name']}*\n"
            f"📌 *Вакансия:* {v['title']}\n"
            f"📍 *Город:* {v['city']} ({v['job_type']})\n"
            f"📊 *Уровень:* {v['experience_level']}\n"
            f"💰 *ЗП:* {v['salary_min']} - {v['salary_max']}\n"
            f"🛠 *Навыки:* {v['required_skills']}\n\n"
            f"📋 *Требования:* {v['requirements']}"
        )
        await message.answer(msg, parse_mode="Markdown", reply_markup=vacancy_action_inline(v['id'], is_saved))

@dp.callback_query(F.data.startswith("vac_apply_"))
async def callback_apply(call: CallbackQuery):
    vac_id = int(call.data.split("_")[2])
    success = await services.apply_for_vacancy(vac_id, call.from_user.id)
    if success:
        await call.answer("Отклик успешно отправлен!", show_alert=True)
    else:
        await call.answer("Вы уже откликались на эту вакансию.", show_alert=True)

@dp.callback_query(F.data.startswith("vac_save_"))
async def callback_save(call: CallbackQuery):
    vac_id = int(call.data.split("_")[2])
    await services.add_saved_vacancy(call.from_user.id, vac_id)
    await call.answer("Добавлено в сохранённые!")

@dp.callback_query(F.data.startswith("vac_unsave_"))
async def callback_unsave(call: CallbackQuery):
    vac_id = int(call.data.split("_")[2])
    await services.remove_saved_vacancy(call.from_user.id, vac_id)
    await call.answer("Удалено из сохранённых!")

@dp.message(F.text == "Сохранённые вакансии")
async def show_saved_vacancies(message: Message):
    vacancies = await services.fetch_saved_vacancies(message.from_user.id)
    if not vacancies:
        await message.answer("У вас нет сохранённых вакансий.")
        return

    for v in vacancies:
        msg = (
            f"⭐️ *{v['company_name']}* — {v['title']}\n"
            f"📍 {v['city']} | 💰 {v['salary_min']}-{v['salary_max']}\n"
            f"📋 {v['requirements']}"
        )
        await message.answer(msg, parse_mode="Markdown", reply_markup=vacancy_action_inline(v['id'], is_saved=True))

@dp.message(F.text == "Мои отклики")
async def show_my_applications(message: Message):
    apps = await services.fetch_candidate_applications(message.from_user.id)
    if not apps:
        await message.answer("Вы еще никуда не откликались.")
        return

    res = "📋 *Ваши отклики:*\n\n"
    for a in apps:
        res += f"📌 *{a['vacancy_title']}* в {a['company_name']}\nСтатус: `{a['status']}`\n\n"
    await message.answer(res, parse_mode="Markdown")

# --- Работодатель ---

@dp.message(F.text == "Мой профиль компании")
async def show_employer_profile(message: Message):
    profile = await services.fetch_employer(message.from_user.id)
    if not profile:
        await message.answer("Профиль компании не найден. Пожалуйста, заполните его.")
        return

    result = (
        f"🏢 *Компания:* {profile['company_name']}\n"
        f"🏭 *Отрасль:* {profile['industry']}\n"
        f"📍 *Город:* {profile['city']}\n"
        f"📝 *Описание:* {profile['description']}\n"
        f"📞 *Контакты:* {profile['contact_information']}"
    )
    await message.answer(result, parse_mode="Markdown", reply_markup=employer_menu())

@dp.message(F.text == "Заполнить/Изменить компанию")
async def start_emp_profile(message: Message, state: FSMContext):
    await state.set_state(EmployerProfileFSM.company)
    await message.answer("Введите название компании:", reply_markup=cancel_keyboard())

@dp.message(EmployerProfileFSM.company)
async def process_emp_company(message: Message, state: FSMContext):
    await state.update_data(company=message.text)
    await state.set_state(EmployerProfileFSM.industry)
    await message.answer("Сфера деятельности / Отрасль:")

@dp.message(EmployerProfileFSM.industry)
async def process_emp_ind(message: Message, state: FSMContext):
    await state.update_data(industry=message.text)
    await state.set_state(EmployerProfileFSM.city)
    await message.answer("Город:")

@dp.message(EmployerProfileFSM.city)
async def process_emp_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(EmployerProfileFSM.description)
    await message.answer("Описание компании:")

@dp.message(EmployerProfileFSM.description)
async def process_emp_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(EmployerProfileFSM.contact_information)
    await message.answer("Контактные данные (email/телефон):")

@dp.message(EmployerProfileFSM.contact_information)
async def process_emp_contacts(message: Message, state: FSMContext):
    await state.update_data(contact_information=message.text)
    data = await state.get_data()
    await services.store_employer_profile(message.from_user.id, data)
    await state.clear()
    await message.answer("Профиль компании сохранен!", reply_markup=employer_menu())

# --- FSM Создания Вакансии ---

@dp.message(F.text == "Создать вакансию")
async def start_vacancy_fsm(message: Message, state: FSMContext):
    await state.set_state(VacancyFSM.title)
    await message.answer("1/8. Введите название вакансии (например: Python Backend Developer):", reply_markup=cancel_keyboard())

@dp.message(VacancyFSM.title)
async def process_vac_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(VacancyFSM.city)
    await message.answer("2/8. Город работы (или 'Удаленно'):", reply_markup=cancel_keyboard())

@dp.message(VacancyFSM.city)
async def process_vac_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(VacancyFSM.job_type)
    await message.answer("3/8. Тип занятости (Full-time / Part-time / Remote):", reply_markup=cancel_keyboard())

@dp.message(VacancyFSM.job_type)
async def process_vac_job_type(message: Message, state: FSMContext):
    await state.update_data(job_type=message.text)
    await state.set_state(VacancyFSM.experience_level)
    await message.answer("4/8. Требуемый уровень (Junior / Middle / Senior):", reply_markup=cancel_keyboard())

@dp.message(VacancyFSM.experience_level)
async def process_vac_exp_level(message: Message, state: FSMContext):
    await state.update_data(experience_level=message.text)
    await state.set_state(VacancyFSM.salary_min)
    await message.answer("5/8. Минимальная зарплата (число):", reply_markup=cancel_keyboard())

@dp.message(VacancyFSM.salary_min)
async def process_vac_salary_min(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число!")
        return
    await state.update_data(salary_min=message.text)
    await state.set_state(VacancyFSM.salary_max)
    await message.answer("6/8. Максимальная зарплата (число):", reply_markup=cancel_keyboard())

@dp.message(VacancyFSM.salary_max)
async def process_vac_salary_max(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите число!")
        return
    await state.update_data(salary_max=message.text)
    await state.set_state(VacancyFSM.required_skills)
    await message.answer("7/8. Ключевые навыки (через запятую):", reply_markup=cancel_keyboard())

@dp.message(VacancyFSM.required_skills)
async def process_vac_skills(message: Message, state: FSMContext):
    await state.update_data(required_skills=message.text)
    await state.set_state(VacancyFSM.requirements)
    await message.answer("8/8. Подробные требования к кандидату:", reply_markup=cancel_keyboard())

@dp.message(VacancyFSM.requirements)
async def process_vac_requirements(message: Message, state: FSMContext):
    await state.update_data(requirements=message.text)
    data = await state.get_data()

    result = (
        "*Проверьте данные вакансии:*\n\n"
        f"📌 *Название:* {data.get('title')}\n"
        f"📍 *Город:* {data.get('city')}\n"
        f"💼 *Тип:* {data.get('job_type')}\n"
        f"📊 *Уровень:* {data.get('experience_level')}\n"
        f"💰 *ЗП:* {data.get('salary_min')} - {data.get('salary_max')}\n"
        f"🛠 *Навыки:* {data.get('required_skills')}\n"
        f"📋 *Требования:* {data.get('requirements')}"
    )
    await state.set_state(VacancyFSM.confirm)
    await message.answer(result, parse_mode="Markdown", reply_markup=confirm_keyboard())

@dp.message(VacancyFSM.confirm, F.text == "Подтвердить")
async def confirm_vacancy_creation(message: Message, state: FSMContext):
    data = await state.get_data()
    await services.store_vacancy(message.from_user.id, data)
    await state.clear()
    await message.answer("🎉 Вакансия успешно опубликована!", reply_markup=employer_menu())

# --- Управление откликами работодателем ---

@dp.message(F.text == "Мои вакансии")
async def show_employer_vacancies(message: Message):
    vacs = await services.fetch_employer_vacancies(message.from_user.id)
    if not vacs:
        await message.answer("У вас пока нет созданных вакансий.")
        return

    await message.answer("Выберите вакансию для просмотра откликов:", reply_markup=employer_vacancies_inline(vacs))

@dp.callback_query(F.data.startswith("emp_vac_apps_"))
async def list_apps_for_vac(call: CallbackQuery):
    vac_id = int(call.data.split("_")[3])
    apps = await services.fetch_vacancy_applications(vac_id)
    if not apps:
        await call.answer("На эту вакансию пока нет откликов.", show_alert=True)
        return

    await call.message.answer(f"📥 *Отклики на вакансию:*", parse_mode="Markdown")
    for a in apps:
        msg = (
            f"👤 *Кандидат:* {a['name']}\n"
            f"🎯 *Должность:* {a['desired_position']}\n"
            f"📊 *Уровень:* {a['experience_level']}\n"
            f"📌 *Статус отклика:* `{a['app_status']}`"
        )
        await call.message.answer(msg, parse_mode="Markdown", reply_markup=candidate_action_inline(a['app_id'], a['app_status']))

@dp.callback_query(F.data.startswith("app_profile_"))
async def view_app_profile(call: CallbackQuery):
    app_id = int(call.data.split("_")[2])
    app_data = await services.fetch_application(app_id)
    if not app_data:
        await call.answer("Отклик не найден.")
        return

    msg = (
        f"👤 *Кандидат:* {app_data['name']}\n"
        f"📞 *Телефон:* {app_data['phone_number']}\n"
        f"📍 *Город:* {app_data['city']}\n"
        f"💼 *Желаемая позиция:* {app_data['desired_position']}\n"
        f"💰 *Ожидаемая ЗП:* {app_data['desired_salary']}\n"
        f"🎓 *Образование:* {app_data['education']}\n"
        f"🛠 *Навыки:* {app_data['skills']}\n"
        f"🌐 *Языки:* {app_data['languages']}\n"
        f"📝 *Опыт:* {app_data['experience']}"
    )
    await call.message.answer(msg, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("app_resume_"))
async def analyze_app_resume(call: CallbackQuery):
    app_id = int(call.data.split("_")[2])
    app_data = await services.fetch_application(app_id)
    
    cv_file = await services.fetch_latest_cv(app_data['candidate_id'])
    if not cv_file:
        await call.answer("Кандидат не прикрепил файл резюме (.txt).", show_alert=True)
        return

    await call.answer("AI анализирует резюме...")
    ai_result = await services.analyze_resume_with_ai(cv_file['extracted_text'], app_data['vacancy_requirements'])
    await call.message.answer(f"🤖 *Анализ соответствия от Groq AI:*\n\n{ai_result}", parse_mode="Markdown")

@dp.callback_query(F.data.startswith("app_status_"))
async def change_status(call: CallbackQuery):
    parts = call.data.split("_")
    new_status = parts[2]
    app_id = int(parts[3])

    await services.change_application_status(app_id, new_status)
    status_text = "Приглашен" if new_status == "interview" else "Отклонен"
    await call.answer(f"Статус изменен: {status_text}")
    await call.message.edit_text(f"{call.message.text}\n\n✅ *Обновленный статус:* `{new_status}`", parse_mode="Markdown")

# --- Запуск приложения ---

async def main():
    await create_tables()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())