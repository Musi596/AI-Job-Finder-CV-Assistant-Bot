import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv

from sql import create_tables
from services import (
    register_user, save_candidate_profile, get_candidate_profile,
    save_employer_profile, get_employer_profile, save_vacancy,
    get_employer_vacancies, close_vacancy
)
from buttons import (
    start_buttons, candidate_menu, employer_menu,
    confirm_keyboard, vacancy_status_keyboard, vacancy_action_inline
)

load_dotenv()
dp = Dispatcher()

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

class VacancyFSM(StatesGroup):
    title = State()
    description = State()
    city = State()
    job_type = State()
    experience_level = State()
    required_skills = State()
    salary_min = State()
    salary_max = State()
    requirements = State()
    responsibilities = State()
    status = State()
    confirm = State()

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
        await message.answer("Начнем заполнение анкеты кандидата!\nВведите ФИО:", reply_markup=None)
        await state.set_state(CandidateFSM.name)

@dp.message(F.text == 'Работодатель')
async def select_employer_role(message: Message, state: FSMContext):
    await register_user(message.from_user.id, 'Работодатель')
    profile = await get_employer_profile(message.from_user.id)
    if profile:
        await message.answer("Вы вошли как Работодатель.", reply_markup=employer_menu())
    else:
        await message.answer("Начнем регистрацию компании!\nВведите название компании:", reply_markup=None)
        await state.set_state(EmployerFSM.company)

@dp.message(F.text == "Заполнить/Изменить профиль")
async def start_candidate_fsm(message: Message, state: FSMContext):
    await message.answer('1/10. Введите полное имя (ФИО):')
    await state.set_state(CandidateFSM.name)

@dp.message(CandidateFSM.name)
async def process_cand_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CandidateFSM.city)
    await message.answer('2/10. Укажите ваш город:')

@dp.message(CandidateFSM.city)
async def process_cand_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(CandidateFSM.phone_number)
    await message.answer('3/10. Введите номер телефона или контактные данные:')

@dp.message(CandidateFSM.phone_number)
async def process_cand_phone(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await state.set_state(CandidateFSM.desired_position)
    await message.answer('4/10. Укажите желаемую должность:')

@dp.message(CandidateFSM.desired_position)
async def process_cand_position(message: Message, state: FSMContext):
    await state.update_data(desired_position=message.text)
    await state.set_state(CandidateFSM.experience_level)
    await message.answer('5/10. Укажите ваш уровень опыта (Junior / Middle / Senior):')

@dp.message(CandidateFSM.experience_level)
async def process_cand_exp_level(message: Message, state: FSMContext):
    await state.update_data(experience_level=message.text)
    await state.set_state(CandidateFSM.skills)
    await message.answer('6/10. Перечислите ваши ключевые навыки:')

@dp.message(CandidateFSM.skills)
async def process_cand_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(CandidateFSM.desired_salary)
    await message.answer('7/10. Укажите ожидаемую зарплату (цифрами):')

@dp.message(CandidateFSM.desired_salary)
async def process_cand_salary(message: Message, state: FSMContext):
    await state.update_data(desired_salary=message.text)
    await state.set_state(CandidateFSM.education)
    await message.answer('8/10. Укажите ваше образование:')

@dp.message(CandidateFSM.education)
async def process_cand_education(message: Message, state: FSMContext):
    await state.update_data(education=message.text)
    await state.set_state(CandidateFSM.languages)
    await message.answer('9/10. Укажите владение языками:')

@dp.message(CandidateFSM.languages)
async def process_cand_languages(message: Message, state: FSMContext):
    await state.update_data(languages=message.text)
    await state.set_state(CandidateFSM.experience)
    await message.answer('10/10. Опишите ваш подробный опыт работы:')

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
    await message.answer(" Профиль кандидата успешно сохранен в БД!", reply_markup=candidate_menu())

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

@dp.message(F.text == "Заполнить/Изменить компанию")
async def start_employer_fsm(message: Message, state: FSMContext):
    await message.answer('1/5. Название компании:')
    await state.set_state(EmployerFSM.company)

@dp.message(EmployerFSM.company)
async def process_emp_company(message: Message, state: FSMContext):
    await state.update_data(company=message.text)
    await state.set_state(EmployerFSM.industry)
    await message.answer('2/5. Отрасль компании:')

@dp.message(EmployerFSM.industry)
async def process_emp_industry(message: Message, state: FSMContext):
    await state.update_data(industry=message.text)
    await state.set_state(EmployerFSM.city)
    await message.answer('3/5. Город:')

@dp.message(EmployerFSM.city)
async def process_emp_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(EmployerFSM.description)
    await message.answer('4/5. Описание компании:')

@dp.message(EmployerFSM.description)
async def process_emp_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(EmployerFSM.contact_information)
    await message.answer('5/5. Контактная информация:')

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
    await message.answer(" Профиль компании сохранен в БД!", reply_markup=employer_menu())

@dp.message(F.text == "Профиль компании")
async def show_employer_profile(message: Message):
    profile = await get_employer_profile(message.from_user.id)
    if not profile:
        await message.answer("Профиль компании не найден. Пожалуйста, заполните его.")
        return
    
    result = (
        "*Профиль компании:*\n\n"
        f"1. *Компания:* {profile['company_name']}\n"
        f"2. *Отрасль:* {profile['industry']}\n"
        f"3. *Город:* {profile['city']}\n"
        f"4. *Описание:* {profile['description']}\n"
        f"5. *Контакты:* {profile['contact_information']}"
    )
    await message.answer(result, parse_mode="Markdown")

@dp.message(F.text == "Создать вакансию")
async def start_vacancy_fsm(message: Message, state: FSMContext):
    employer = await get_employer_profile(message.from_user.id)
    if not employer:
        await message.answer("Сначала заполните профиль компании!")
        return

    await message.answer("1/11. Введите название вакансии:")
    await state.set_state(VacancyFSM.title)

@dp.message(VacancyFSM.title)
async def process_vac_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(VacancyFSM.description)
    await message.answer("2/11. Введите подробное описание вакансии:")

@dp.message(VacancyFSM.description)
async def process_vac_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(VacancyFSM.city)
    await message.answer("3/11. Укажите город:")

@dp.message(VacancyFSM.city)
async def process_vac_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(VacancyFSM.job_type)
    await message.answer("4/11. Тип занятости (Полная, Частичная, Удаленка):")

@dp.message(VacancyFSM.job_type)
async def process_vac_job_type(message: Message, state: FSMContext):
    await state.update_data(job_type=message.text)
    await state.set_state(VacancyFSM.experience_level)
    await message.answer("5/11. Требуемый уровень опыта (Junior / Middle / Senior):")

@dp.message(VacancyFSM.experience_level)
async def process_vac_exp(message: Message, state: FSMContext):
    await state.update_data(experience_level=message.text)
    await state.set_state(VacancyFSM.required_skills)
    await message.answer("6/11. Требуемые навыки (через запятую):")

@dp.message(VacancyFSM.required_skills)
async def process_vac_skills(message: Message, state: FSMContext):
    await state.update_data(required_skills=message.text)
    await state.set_state(VacancyFSM.salary_min)
    await message.answer("7/11. Минимальная зарплата (число):")

@dp.message(VacancyFSM.salary_min)
async def process_vac_sal_min(message: Message, state: FSMContext):
    await state.update_data(salary_min=message.text)
    await state.set_state(VacancyFSM.salary_max)
    await message.answer("8/11. Максимальная зарплата (число):")

@dp.message(VacancyFSM.salary_max)
async def process_vac_sal_max(message: Message, state: FSMContext):
    await state.update_data(salary_max=message.text)
    await state.set_state(VacancyFSM.requirements)
    await message.answer("9/11. Требования к кандидату:")

@dp.message(VacancyFSM.requirements)
async def process_vac_reqs(message: Message, state: FSMContext):
    await state.update_data(requirements=message.text)
    await state.set_state(VacancyFSM.responsibilities)
    await message.answer("10/11. Обязанности кандидата:")

@dp.message(VacancyFSM.responsibilities)
async def process_vac_resp(message: Message, state: FSMContext):
    await state.update_data(responsibilities=message.text)
    await state.set_state(VacancyFSM.status)
    await message.answer("11/11. Выберите статус для вакансии:", reply_markup=vacancy_status_keyboard())

@dp.message(VacancyFSM.status)
async def process_vac_status(message: Message, state: FSMContext):
    status_text = message.text
    status = 'draft' if 'draft' in status_text.lower() else 'active'
    await state.update_data(status=status)
    
    data = await state.get_data()
    result = (
        "*Подтверждение создания вакансии:*\n\n"
        f"1. *Название:* {data.get('title')}\n"
        f"2. *Описание:* {data.get('description')}\n"
        f"3. *Город:* {data.get('city')}\n"
        f"4. *Тип занятости:* {data.get('job_type')}\n"
        f"5. *Уровень:* {data.get('experience_level')}\n"
        f"6. *Навыки:* {data.get('required_skills')}\n"
        f"7. *Мин. ЗП:* {data.get('salary_min')}\n"
        f"8. *Макс. ЗП:* {data.get('salary_max')}\n"
        f"9. *Требования:* {data.get('requirements')}\n"
        f"10. *Обязанности:* {data.get('responsibilities')}\n"
        f"11. *Статус:* {data.get('status')}"
    )
    await state.set_state(VacancyFSM.confirm)
    await message.answer(result, parse_mode="Markdown", reply_markup=confirm_keyboard())

@dp.message(VacancyFSM.confirm, F.text == "Подтвердить")
async def confirm_vacancy(message: Message, state: FSMContext):
    data = await state.get_data()
    employer = await get_employer_profile(message.from_user.id)
    
    await save_vacancy(
        employer_id=message.from_user.id,
        company_name=employer['company_name'],
        data=data,
        status=data['status']
    )
    await state.clear()
    await message.answer(" Вакансия успешно сохранена!", reply_markup=employer_menu())

@dp.message(F.text == "Мои вакансии")
async def list_employer_vacancies(message: Message):
    vacancies = await get_employer_vacancies(message.from_user.id)
    if not vacancies:
        await message.answer("У вас пока нет созданных вакансий.")
        return

    for vac in vacancies:
        is_closed = vac['status'] == 'closed'
        text = (
            f"📌 *{vac['title']}* ({vac['status'].upper()})\n"
            f"🏢 Компания: {vac['company_name']}\n"
            f"📍 Город: {vac['city']}\n"
            f"💼 Тип: {vac['job_type']} ({vac['experience_level']})\n"
            f"💰 ЗП: {vac['salary_min']} - {vac['salary_max']}\n\n"
            f"📄 *Описание:* {vac['description']}\n"
            f"🛠 *Навыки:* {vac['required_skills']}\n"
            f"📋 *Требования:* {vac['requirements']}\n"
            f"📝 *Обязанности:* {vac['responsibilities']}"
        )
        await message.answer(
            text, 
            parse_mode="Markdown", 
            reply_markup=vacancy_action_inline(vac['id'], is_closed=is_closed)
        )

@dp.callback_query(F.data.startswith("close_vac_"))
async def process_close_vacancy(callback: CallbackQuery):
    vac_id = int(callback.data.split("_")[2])
    await close_vacancy(vac_id, callback.from_user.id)
    await callback.answer("Вакансия закрыта!")
    await callback.message.edit_text(callback.message.text + "\n\n❌ *ВAКАНСИЯ ЗАКРЫТА*", parse_mode="Markdown")

@dp.message(F.text == "Заполнить заново")
async def reset_fsm(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Заполнение отменено. Выберите нужный пункт меню.", reply_markup=start_buttons())

async def main():
    await create_tables()
    logging.basicConfig(level=logging.INFO)
    logging.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as er:
        print(f"Ошибка запуска: {er}")