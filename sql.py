import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def connection():
    db = await asyncpg.connect(
        host='localhost',
        user='postgres',
        database='job_fainder_db',
        password=os.getenv('DB_PASSWORD'),
        port=5432
    )
    return db

async def create_tables():
    db = await connection()
    try:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT NOT NULL UNIQUE,
            role VARCHAR(20) not null,
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
            contact_information VARCHAR(50) NOT NULL
        );
        """)
        print('Tables created')
    except Exception as er:
        print(er)
    finally:
        await db.close()