from sql import connection
async def register_user(telegram_id: int, role: str):
    db = await connection()
    try:
        await db.execute(
            'INSERT INTO users (telegram_id, role) VALUES ($1, $2) ON CONFLICT (telegram_id) DO UPDATE SET role = $2',
            telegram_id, role
        )
    finally:
        await db.close()

async def get_user(telegram_id: int):
    db = await connection()
    try:
        return await db.fetchrow('SELECT * FROM users WHERE telegram_id = $1', telegram_id)
    finally:
        await db.close()

async def save_candidate_profile(telegram_id: int, data: dict):
    db = await connection()
    try:
        salary = int(data['desired_salary']) if str(data['desired_salary']).isdigit() else 0
        await db.execute("""
            INSERT INTO candidate_profiles 
            (user_id, name, city, phone_number, desired_position, desired_salary, experience_level, skills, education, languages, experience)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (user_id) DO UPDATE SET
                name = EXCLUDED.name,
                city = EXCLUDED.city,
                phone_number = EXCLUDED.phone_number,
                desired_position = EXCLUDED.desired_position,
                desired_salary = EXCLUDED.desired_salary,
                experience_level = EXCLUDED.experience_level,
                skills = EXCLUDED.skills,
                education = EXCLUDED.education,
                languages = EXCLUDED.languages,
                experience = EXCLUDED.experience;
        """, telegram_id, data['name'], data['city'], data['phone_number'], 
           data['desired_position'], salary, data['experience_level'], 
           data['skills'], data['education'], data['languages'], data['experience'])
    finally:
        await db.close()

async def get_candidate_profile(telegram_id: int):
    db = await connection()
    try:
        return await db.fetchrow('SELECT * FROM candidate_profiles WHERE user_id = $1', telegram_id)
    finally:
        await db.close()

async def save_employer_profile(telegram_id: int, data: dict):
    db = await connection()
    try:
        await db.execute("""
            INSERT INTO employer_profiles 
            (user_id, company_name, industry, city, description, contact_information)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (user_id) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                industry = EXCLUDED.industry,
                city = EXCLUDED.city,
                description = EXCLUDED.description,
                contact_information = EXCLUDED.contact_information;
        """, telegram_id, data['company'], data['industry'], data['city'], data['description'], data['contact_information'])
    finally:
        await db.close()

async def get_employer_profile(telegram_id: int):
    db = await connection()
    try:
        return await db.fetchrow('SELECT * FROM employer_profiles WHERE user_id = $1', telegram_id)
    finally:
        await db.close()

# Вакансии
async def save_vacancy(employer_id: int, company_name: str, data: dict, status: str = 'active'):
    db = await connection()
    try:
        s_min = int(data['salary_min']) if str(data['salary_min']).isdigit() else 0
        s_max = int(data['salary_max']) if str(data['salary_max']).isdigit() else 0
        
        await db.execute("""
            INSERT INTO vacancies 
            (employer_id, company_name, title, description, city, job_type, experience_level, required_skills, salary_min, salary_max, requirements, responsibilities, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
        """, employer_id, company_name, data['title'], data['description'], data['city'],
           data['job_type'], data['experience_level'], data['required_skills'],
           s_min, s_max, data['requirements'], data['responsibilities'], status)
    finally:
        await db.close()

async def get_employer_vacancies(employer_id: int):
    db = await connection()
    try:
        return await db.fetch('SELECT * FROM vacancies WHERE employer_id = $1 ORDER BY id DESC', employer_id)
    finally:
        await db.close()

async def close_vacancy(vacancy_id: int, employer_id: int):
    db = await connection()
    try:
        await db.execute("UPDATE vacancies SET status = 'closed' WHERE id = $1 AND employer_id = $2", vacancy_id, employer_id)
    finally:
        await db.close()