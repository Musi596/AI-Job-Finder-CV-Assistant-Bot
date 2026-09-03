import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def connection():
    return await asyncpg.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'postgres'),
        database=os.getenv('DB_NAME', 'job_fainder_db'),
        password=os.getenv('DB_PASSWORD'),
        port=int(os.getenv('DB_PORT', 5432))
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
            cover_letter TEXT,
            status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(vacancy_id, candidate_id) -- Защита от повторных откликов на одну и ту же вакансию
        );
        """)
        print('Таблицы успешно созданы')
    except Exception as er:
        print(f"Ошибка при создании таблиц: {er}")
    finally:
        await db.close()