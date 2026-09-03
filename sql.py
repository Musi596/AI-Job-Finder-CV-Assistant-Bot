import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def connection():
    return await asyncpg.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

async def create_tables():
    db = await connection()
    try:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL UNIQUE,
            role VARCHAR(20) NOT NULL,
            is_blocked BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS candidate_profiles (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL UNIQUE REFERENCES users(telegram_id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            city VARCHAR(50) NOT NULL,
            phone_number VARCHAR(50) NOT NULL,
            desired_position VARCHAR(100) NOT NULL,
            desired_salary BIGINT,
            experience_level VARCHAR(50),
            skills TEXT,
            education TEXT NOT NULL,
            languages TEXT,
            experience TEXT
        );

        CREATE TABLE IF NOT EXISTS employer_profiles (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL UNIQUE REFERENCES users(telegram_id) ON DELETE CASCADE,
            company_name VARCHAR(100) NOT NULL,
            industry VARCHAR(200) NOT NULL,
            city VARCHAR(50) NOT NULL,
            description TEXT NOT NULL,
            contact_information VARCHAR(100) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS vacancies (
            id SERIAL PRIMARY KEY,
            employer_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
            company_name VARCHAR(100) NOT NULL,
            title VARCHAR(500) NOT NULL,
            description TEXT NOT NULL,
            city VARCHAR(50) NOT NULL,
            job_type VARCHAR(100) NOT NULL,
            experience_level VARCHAR(50) NOT NULL,
            required_skills TEXT NOT NULL,
            salary_min BIGINT NOT NULL,
            salary_max BIGINT NOT NULL,
            requirements TEXT NOT NULL,
            responsibilities TEXT NOT NULL,
            status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('draft', 'active', 'closed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS applications (
            id SERIAL PRIMARY KEY,
            vacancy_id INT NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
            candidate_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'submitted' CHECK (status IN ('submitted', 'reviewing', 'interview', 'accepted', 'rejected')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(vacancy_id, candidate_id)
        );

        CREATE TABLE IF NOT EXISTS saved_vacancies (
            id SERIAL PRIMARY KEY,
            candidate_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
            vacancy_id INT NOT NULL REFERENCES vacancies(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(candidate_id, vacancy_id)
        );

        CREATE TABLE IF NOT EXISTS cv_files (
            id SERIAL PRIMARY KEY,
            candidate_id BIGINT NOT NULL REFERENCES users(telegram_id) ON DELETE CASCADE,
            file_path VARCHAR(255) NOT NULL,
            original_file_name VARCHAR(255) NOT NULL,
            extracted_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print('Таблицы успешно созданы')
    except Exception as er:
        print(f"Ошибка при создании таблиц: {er}")
    finally:
        await db.close()

async def register_user(telegram_id: int, role: str):
    db = await connection()
    try:
        await db.execute("""
            INSERT INTO users (telegram_id, role)
            VALUES ($1, $2)
            ON CONFLICT (telegram_id) DO UPDATE SET role = EXCLUDED.role;
        """, telegram_id, role)
    finally:
        await db.close()

async def get_candidate_profile(telegram_id: int):
    db = await connection()
    try:
        return await db.fetchrow("SELECT * FROM candidate_profiles WHERE user_id = $1;", telegram_id)
    finally:
        await db.close()

async def save_candidate_profile(telegram_id: int, data: dict):
    db = await connection()
    try:
        await db.execute("""
            INSERT INTO candidate_profiles (
                user_id, name, city, phone_number, desired_position,
                experience_level, skills, desired_salary, education, languages, experience
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (user_id) DO UPDATE SET
                name = EXCLUDED.name,
                city = EXCLUDED.city,
                phone_number = EXCLUDED.phone_number,
                desired_position = EXCLUDED.desired_position,
                experience_level = EXCLUDED.experience_level,
                skills = EXCLUDED.skills,
                desired_salary = EXCLUDED.desired_salary,
                education = EXCLUDED.education,
                languages = EXCLUDED.languages,
                experience = EXCLUDED.experience;
        """, telegram_id, data.get('name'), data.get('city'), data.get('phone_number'),
        data.get('desired_position'), data.get('experience_level'), data.get('skills'),
        int(data.get('desired_salary', 0)), data.get('education'), data.get('languages'), data.get('experience'))
    finally:
        await db.close()

async def get_employer_profile(telegram_id: int):
    db = await connection()
    try:
        return await db.fetchrow("SELECT * FROM employer_profiles WHERE user_id = $1;", telegram_id)
    finally:
        await db.close()

async def save_employer_profile(telegram_id: int, data: dict):
    db = await connection()
    try:
        await db.execute("""
            INSERT INTO employer_profiles (
                user_id, company_name, industry, city, description, contact_information
            ) VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user_id) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                industry = EXCLUDED.industry,
                city = EXCLUDED.city,
                description = EXCLUDED.description,
                contact_information = EXCLUDED.contact_information;
        """, telegram_id, data.get('company'), data.get('industry'), data.get('city'),
        data.get('description'), data.get('contact_information'))
    finally:
        await db.close()

async def get_all_active_vacancies():
    db = await connection()
    try:
        return await db.fetch("SELECT * FROM vacancies WHERE status = 'active' ORDER BY created_at DESC;")
    finally:
        await db.close()

async def is_already_applied(vacancy_id: int, candidate_id: int) -> bool:
    db = await connection()
    try:
        row = await db.fetchrow(
            "SELECT 1 FROM applications WHERE vacancy_id = $1 AND candidate_id = $2;",
            vacancy_id, candidate_id
        )
        return row is not None
    finally:
        await db.close()

async def create_application(vacancy_id: int, candidate_id: int) -> bool:
    db = await connection()
    try:
        await db.execute(
            "INSERT INTO applications (vacancy_id, candidate_id) VALUES ($1, $2);",
            vacancy_id, candidate_id
        )
        return True
    except Exception:
        return False
    finally:
        await db.close()

async def get_candidate_applications(candidate_id: int):
    db = await connection()
    try:
        return await db.fetch("""
            SELECT a.status, a.created_at, v.title AS vacancy_title, v.company_name
            FROM applications a
            JOIN vacancies v ON a.vacancy_id = v.id
            WHERE a.candidate_id = $1
            ORDER BY a.created_at DESC;
        """, candidate_id)
    finally:
        await db.close()

async def get_employer_vacancies_with_app_count(employer_id: int):
    db = await connection()
    try:
        return await db.fetch("""
            SELECT v.*, COUNT(a.id) AS applications_count
            FROM vacancies v
            LEFT JOIN applications a ON v.id = a.vacancy_id
            WHERE v.employer_id = $1
            GROUP BY v.id
            ORDER BY v.created_at DESC;
        """, employer_id)
    finally:
        await db.close()

async def get_applications_for_vacancy(vacancy_id: int):
    db = await connection()
    try:
        return await db.fetch("""
            SELECT 
                a.id AS app_id,
                a.status AS app_status,
                a.candidate_id,
                cp.name,
                cp.experience_level,
                cp.skills,
                cp.desired_position,
                cp.city,
                cp.desired_salary,
                cp.education,
                cp.languages,
                cp.experience,
                cp.phone_number
            FROM applications a
            JOIN candidate_profiles cp ON a.candidate_id = cp.user_id
            WHERE a.vacancy_id = $1
            ORDER BY a.created_at DESC;
        """, vacancy_id)
    finally:
        await db.close()

async def get_application_by_id(app_id: int):
    db = await connection()
    try:
        return await db.fetchrow("""
            SELECT 
                a.id AS app_id,
                a.status AS app_status,
                a.candidate_id,
                a.vacancy_id,
                cp.name,
                cp.experience_level,
                cp.skills,
                cp.desired_position,
                cp.city,
                cp.desired_salary,
                cp.education,
                cp.languages,
                cp.experience,
                cp.phone_number
            FROM applications a
            JOIN candidate_profiles cp ON a.candidate_id = cp.user_id
            WHERE a.id = $1;
        """, app_id)
    finally:
        await db.close()

async def update_application_status(app_id: int, new_status: str):
    db = await connection()
    try:
        await db.execute("""
            UPDATE applications
            SET status = $1
            WHERE id = $2;
        """, new_status, app_id)
        return True
    except Exception:
        return False
    finally:
        await db.close()

# --- Сохранённые вакансии (Этап 9) ---

async def save_vacancy(candidate_id: int, vacancy_id: int) -> bool:
    db = await connection()
    try:
        await db.execute("""
            INSERT INTO saved_vacancies (candidate_id, vacancy_id)
            VALUES ($1, $2)
            ON CONFLICT (candidate_id, vacancy_id) DO NOTHING;
        """, candidate_id, vacancy_id)
        return True
    except Exception:
        return False
    finally:
        await db.close()

async def unsave_vacancy(candidate_id: int, vacancy_id: int) -> bool:
    db = await connection()
    try:
        await db.execute("""
            DELETE FROM saved_vacancies
            WHERE candidate_id = $1 AND vacancy_id = $2;
        """, candidate_id, vacancy_id)
        return True
    except Exception:
        return False
    finally:
        await db.close()

async def is_vacancy_saved(candidate_id: int, vacancy_id: int) -> bool:
    db = await connection()
    try:
        row = await db.fetchrow(
            "SELECT 1 FROM saved_vacancies WHERE candidate_id = $1 AND vacancy_id = $2;",
            candidate_id, vacancy_id
        )
        return row is not None
    finally:
        await db.close()

async def get_saved_vacancies(candidate_id: int):
    db = await connection()
    try:
        return await db.fetch("""
            SELECT v.*
            FROM saved_vacancies sv
            JOIN vacancies v ON sv.vacancy_id = v.id
            WHERE sv.candidate_id = $1
            ORDER BY sv.created_at DESC;
        """, candidate_id)
    finally:
        await db.close()

# --- Загрузка и сохраненный текст CV (Этап 10) ---

async def save_cv_file(candidate_id: int, file_path: str, original_file_name: str, extracted_text: str):
    db = await connection()
    try:
        return await db.fetchval("""
            INSERT INTO cv_files (candidate_id, file_path, original_file_name, extracted_text)
            VALUES ($1, $2, $3, $4)
            RETURNING id;
        """, candidate_id, file_path, original_file_name, extracted_text)
    finally:
        await db.close()

async def get_latest_cv_file(candidate_id: int):
    db = await connection()
    try:
        return await db.fetchrow("""
            SELECT * FROM cv_files
            WHERE candidate_id = $1
            ORDER BY created_at DESC LIMIT 1;
        """, candidate_id)
    finally:
        await db.close()