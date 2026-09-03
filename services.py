from ai_service import ask_ai
from sql import *

async def register_candidate(telegram_id: int):
    await register_user(telegram_id, "Кандидат")

async def register_employer(telegram_id: int):
    await register_user(telegram_id, "Работодатель")

async def fetch_candidate(telegram_id: int):
    return await get_candidate_profile(telegram_id)

async def fetch_employer(telegram_id: int):
    return await get_employer_profile(telegram_id)

async def store_candidate_profile(telegram_id: int, data: dict):
    await save_candidate_profile(telegram_id, data)

async def store_employer_profile(telegram_id: int, data: dict):
    await save_employer_profile(telegram_id, data)

async def store_vacancy(employer_id: int, data: dict):
    await create_vacancy(employer_id, data)

async def fetch_active_vacancies():
    return await get_all_active_vacancies()

async def apply_for_vacancy(vacancy_id: int, candidate_id: int) -> bool:
    if await is_already_applied(vacancy_id, candidate_id):
        return False
    return await create_application(vacancy_id, candidate_id)

async def fetch_candidate_applications(candidate_id: int):
    return await get_candidate_applications(candidate_id)

async def add_saved_vacancy(candidate_id: int, vacancy_id: int) -> bool:
    return await save_vacancy(candidate_id, vacancy_id)

async def remove_saved_vacancy(candidate_id: int, vacancy_id: int) -> bool:
    return await unsave_vacancy(candidate_id, vacancy_id)

async def fetch_saved_vacancies(candidate_id: int):
    return await get_saved_vacancies(candidate_id)

async def check_is_saved(candidate_id: int, vacancy_id: int) -> bool:
    return await is_vacancy_saved(candidate_id, vacancy_id)

async def store_cv_file(candidate_id: int, file_path: str, original_file_name: str, extracted_text: str):
    return await save_cv_file(candidate_id, file_path, original_file_name, extracted_text)

async def fetch_latest_cv(candidate_id: int):
    return await get_latest_cv_file(candidate_id)

async def fetch_employer_vacancies(employer_id: int):
    return await get_employer_vacancies_with_app_count(employer_id)

async def fetch_vacancy_applications(vacancy_id: int):
    return await get_applications_for_vacancy(vacancy_id)

async def fetch_application(app_id: int):
    return await get_application_by_id(app_id)

async def change_application_status(app_id: int, new_status: str):
    return await update_application_status(app_id, new_status)

async def analyze_resume_with_ai(cv_text: str, vacancy_requirements: str) -> str:
    prompt = (
        f"Проанализируй соответствие текста резюме кандидата требованиям вакансии.\n\n"
        f"--- ТЕКСТ РЕЗЮМЕ ---\n{cv_text}\n\n"
        f"--- ТРЕБОВАНИЯ ВАКАНСИИ ---\n{vacancy_requirements}\n\n"
        f"Дай структуру ответа:\n"
        f"1. Процент соответствия (0-100%)\n"
        f"2. Сильные стороны\n"
        f"3. Чего не хватает кандидату"
    )
    return await ask_ai(prompt)