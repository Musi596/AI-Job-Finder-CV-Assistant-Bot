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


async def fetch_active_vacancies():
    return await get_all_active_vacancies()


async def apply_for_vacancy(vacancy_id: int, candidate_id: int) -> bool:
    if await is_already_applied(vacancy_id, candidate_id):
        return False
    return await create_application(vacancy_id, candidate_id)


async def fetch_candidate_applications(candidate_id: int):
    return await get_candidate_applications(candidate_id)