import asyncio
import logging

from aiogram import Router, types
from aiogram.filters import CommandStart, or_f, Command
from aiogram.fsm.context import FSMContext

from states.FSM import UserSurvey

logger = logging.getLogger()
user_private_router = Router()


@user_private_router.message(CommandStart())
async def start_bot(message: types.Message, state: FSMContext):
    await message.answer("Привет 👋, я - NutritionBot 🤖, бот, для управления питанием с нестандартным подходом "
                         "к планированию рациона ")
    await asyncio.sleep(2)
    await message.answer("Я помогу вам контролировать свой вес, подбирая план питания без жестких ограничений")
    await asyncio.sleep(2)
    await message.answer("Сейчас я задам несколько вопросов, чтобы составить план конкретно под вас")
    await asyncio.sleep(2)
    await message.answer("Для начала укажите свой возраст цифрами и без букв:")
    await state.set_state(UserSurvey.age)


@user_private_router.message(or_f(UserSurvey.age, Command("set_params")))
async def ask_age(message: types.Message, state: FSMContext):
    try:
        int(message.text)

        if len(message.text) >= 3 or len(message.text) < 2:
            await message.answer("Введите пожалуйста свой настоящий возраст")
            return

    except ValueError:
        await message.answer("Введите сколько вам полных лет без букв, символов")
        return

    await message.answer("Хорошо, теперь введите пожалуйста свой пол: ")
    await state.set_state(UserSurvey.gender)















