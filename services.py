import aiohttp
import asyncio
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

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

async def fetch_and_store_hh_vacancies(query: str = "Python"):
    url = "https://api.hh.ru/vacancies"
    params = {"text": query, "per_page": 10}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params, headers=HEADERS) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for item in data.get("items", []):
                        salary_data = item.get("salary")
                        salary = "Не указана"
                        if salary_data:
                            s_from = salary_data.get("from")
                            s_to = salary_data.get("to")
                            currency = salary_data.get("currency", "руб.")
                            salary = f"от {s_from or ''} до {s_to or ''} {currency}".strip()

                        v_data = {
                            "external_id": f"hh_{item.get('id')}",
                            "source": "HeadHunter",
                            "title": item.get("name"),
                            "company": item.get("employer", {}).get("name", "Не указано"),
                            "salary": salary,
                            "description": item.get("snippet", {}).get("requirement", "") or "Описание отсутствует",
                            "url": item.get("alternate_url")
                        }
                        await save_external_vacancy(v_data)
        except Exception as e:
            print(f"Ошибка при сборе с HH: {e}")

async def sync_external_vacancies():
    print("🔄 Начинаем обновление внешних вакансий...")
    keywords = ["Python", "JavaScript", "Data Analyst", "Project Manager"]
    for kw in keywords:
        await fetch_and_store_hh_vacancies(query=kw)
    print("✅ Обновление внешних вакансий завершено!")

async def fetch_all_combined_vacancies():
    bot_vacancies = await get_all_active_vacancies()
    for v in bot_vacancies:
        v["source"] = "Внутренняя вакансия бота"
        v["is_external"] = False

    ext_vacancies = await get_external_vacancies()
    for v in ext_vacancies:
        v["is_external"] = True
    return bot_vacancies + ext_vacancies