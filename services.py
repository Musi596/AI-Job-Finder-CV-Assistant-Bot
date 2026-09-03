from sql import (
    create_application,
    get_all_active_vacancies,
    get_candidate_applications,
    get_candidate_profile,
    get_employer_profile,
    get_latest_cv_file,
    get_saved_vacancies,
    is_already_applied,
    is_vacancy_saved,
    register_user,
    save_candidate_profile,
    save_cv_file,
    save_employer_profile,
    save_vacancy,
    unsave_vacancy,
)


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