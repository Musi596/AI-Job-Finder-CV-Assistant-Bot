import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from dotenv import load_dotenv
from services import * 
from buttons import *

load_dotenv()
dp = Dispatcher()


class candidate(StatesGroup):
    name = State()
    city = State()
    phone_number = State()
    desired_position = State()
    desired_salary = State()
    expirience_level = State()
    skills = State()
    education = State()
    languages = State()
    expirience = State()


bot = Bot(os.getenv('BOT_TOKEN'))
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer('Выберите роль:',reply_markup=start_buttons())

@dp.message(F.text == 'Кандидат')
async def handler(message: Message, state: FSMContext):
    await register(message.from_user.id,message.text)
    await state.set_state(candidate.name)
    await message.answer('Введите ФИО:')

@dp.message(candidate.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(candidate.city)
    await message.answer('Укажите ваш город:')

@dp.message(candidate.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(candidate.phone_number)
    await message.answer('Введите номер телефона:')

@dp.message(candidate.phone_number)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone_number=message.text)
    await state.set_state(candidate.desired_position)
    await message.answer('Укажите желаемую должность:')

@dp.message(candidate.desired_position)
async def process_position(message: Message, state: FSMContext):
    await state.update_data(desired_position=message.text)
    await state.set_state(candidate.desired_salary)
    await message.answer('Укажите желаемую зарплату:')

@dp.message(candidate.desired_salary)
async def process_salary(message: Message, state: FSMContext):
    await state.update_data(desired_salary=message.text)
    await state.set_state(candidate.expirience_level)
    await message.answer('Укажите ваш уровень опыта:')

@dp.message(candidate.expirience_level)
async def process_exp_level(message: Message, state: FSMContext):
    await state.update_data(expirience_level=message.text)
    await state.set_state(candidate.skills)
    await message.answer('Перечислите ваши ключевые навыки:')

@dp.message(candidate.skills)
async def process_skills(message: Message, state: FSMContext):
    await state.update_data(skills=message.text)
    await state.set_state(candidate.education)
    await message.answer('Укажите ваше образование:')

@dp.message(candidate.education)
async def process_education(message: Message, state: FSMContext):
    await state.update_data(education=message.text)
    await state.set_state(candidate.languages)
    await message.answer('Владение иностранными языками:')

@dp.message(candidate.languages)
async def process_languages(message: Message, state: FSMContext):
    await state.update_data(languages=message.text)
    await state.set_state(candidate.expirience)
    await message.answer('Опишите ваш опыт работы:')

@dp.message(candidate.expirience)
async def process_experience(message: Message, state: FSMContext):
    await state.update_data(expirience=message.text)
    data = await state.get_data()
    result = (
        "**Анкета кандидата успешно заполнена!**\n\n"
        f"**ФИО:* {data['name']}\n"
        f"**Город:* {data['city']}\n"
        f"**Телефон:* {data['phone_number']}\n"
        f"**Должность:* {data['desired_position']}\n"
        f"**Зарплата:* {data['desired_salary']}\n"
        f"**Уровень:* {data['expirience_level']}\n"
        f"**Навыки:* {data['skills']}\n"
        f"**Образование:* {data['education']}\n"
        f"**Языки:* {data['languages']}\n"
        f"**Опыт работы:* {data['expirience']}"
    )
    
    await message.answer(result, parse_mode="Markdown")
    await state.clear()  



async def main():
    logging.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as er:
        print(er)