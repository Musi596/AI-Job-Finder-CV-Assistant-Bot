import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
from services import * 
from buttons import *

load_dotenv()
dp = Dispatcher()
bot = Bot(os.getenv('BOT_TOKEN'))
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer('Выберите роль:',reply_markup=start_buttons())

@dp.message(F.text == 'Кандидат')
async def handler(message: Message):
    await register(message.from_user.id,message.text)
    await message.answer('Успешно')

@dp.message(F.text == 'Работодатель')
async def handler(message: Message):
    await register(message.from_user.id,message.text)
    await message.answer('Успешно')


async def main():
    logging.info("Бот запускается...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен")