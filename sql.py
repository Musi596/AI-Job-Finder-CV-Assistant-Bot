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
        create table if not exists users(
            id serial primary key,
            telegram_id bigint not null unique,
            role varchar(20),
            created_at timestamp default now()
        );
        create table if not exists candidate_profiles(
            name varchar(100) not null,
            city varchar(50) not null,
            phone_number varchar(50) not null,
            desired_position varchar(100) not null,
            desired_salary bigint,
            experience_level varchar(50),
            skills text,
            education text not null,
            languages text,
            experience varchar(100)
        );
        """)
        print('Tables created')
    except Exception as er:
        print(er)
    finally:
        await db.close()