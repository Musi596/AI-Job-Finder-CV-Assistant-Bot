from sql import connection

async def register(telegram_id,role):
    db = await connection()
    try:
        await db.execute('insert into users(telegram_id, role) values($1,$2) ON CONFLICT DO NOTHING',telegram_id, role)
    except Exception as er:
        print(er)
    finally:
        await db.close()
