import asyncio
import logging

from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_add_user_info, orm_get_user_info, orm_delete_user_info, orm_get_breakfast
from keyboards.inline import gender_kb, activity_level_kb, target_kb, num_meals_kb
from services.calculate_nutrition import calculate_nutrition, number_of_grams
from states.FSM import UserSurvey

logger = logging.getLogger(__name__)
user_private_router = Router()


@user_private_router.message(CommandStart())
async def start_bot(message: types.Message, state: FSMContext):
    await message.answer("Привет 👋, я - NutritionBot 🤖, бот, для управления питанием с нестандартным подходом "
                         "к планированию рациона ")
    await asyncio.sleep(2)
    await message.answer("Я помогу вам контролировать свой вес, подбирая план питания без жестких ограничений")
    await asyncio.sleep(2)
    await message.answer("Выберите, чтобы вы хотели сделать:\n"
                         "/start - Запуск/Перезапуск бота\n"
                         "/set_params - Установка индивидуальных параметров (возраст, вес, цель и т.д.)\n"
                         "/add_product - Добавление продуктов в базу пользователя\n"
                         "/plan_meals - Генерация плана питания\n"
                         "/payment - Тарифы")


# ---------------------------------/set_params/---------------------------------------------

@user_private_router.message(Command("set_params"))
async def set_params(message: types.Message, state: FSMContext):
    await message.answer("Отлично, давайте перейдём к делу")
    await asyncio.sleep(2)
    await message.answer("Сейчас я задам несколько вопросов, чтобы составить план конкретно под вас")
    await asyncio.sleep(2)
    await message.answer("Для начала укажите свой возраст цифрами и без букв:")
    await state.set_state(UserSurvey.age)


@user_private_router.message(UserSurvey.age)
async def ask_age(message: types.Message, state: FSMContext):
    try:
        int(message.text)

        if len(message.text) >= 3 or len(message.text) < 2:
            await message.answer("Введите пожалуйста свой настоящий возраст:")
            return

    except ValueError:
        await message.answer("Введите сколько вам полных лет без букв и символов:")
        return

    await message.answer("Хорошо, теперь выберите пожалуйста свой пол: ", reply_markup=gender_kb.as_markup())
    await state.update_data(age=message.text)
    await state.set_state(UserSurvey.gender)


@user_private_router.callback_query(UserSurvey.gender)
async def ask_gender(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Отлично, укажите свой рост цифрами в сантиметрах, без букв и символов:")
    await state.update_data(gender=callback.data)
    await state.set_state(UserSurvey.height)


@user_private_router.message(UserSurvey.height)
async def ask_height(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)

        if height > 250 or height < 70:
            await message.answer("Введите пожалуйста настоящий рост:")
            return

    except ValueError:
        await message.answer("Введите свой рост только цифрами и без лишних символов:")
        return

    await message.answer("Теперь введите свой вес:")
    await state.update_data(height=message.text)
    await state.set_state(UserSurvey.weight)


@user_private_router.message(UserSurvey.weight)
async def ask_weight(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)

        if weight > 300 or weight < 30:
            await message.answer("Введите пожалуйста настоящий вес.")
            return

    except ValueError:
        await message.answer("Введите свой вес только цифрами и без лишних символов.")
        return

    await message.answer("По вашим ощущениям, какой ваш уровень физической активности:",
                         reply_markup=activity_level_kb.as_markup())
    await state.update_data(weight=message.text)
    await state.set_state(UserSurvey.activity_level)


@user_private_router.callback_query(UserSurvey.activity_level)
async def activity_level(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Выберите цель для вашей диеты:", reply_markup=target_kb.as_markup())
    await state.update_data(activity_level=callback.data)
    await state.set_state(UserSurvey.target)


@user_private_router.callback_query(UserSurvey.target)
async def num_meals(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Напишите какие у вас есть противопоказания или заболевания "
                                  "(аллергия, диабет, проблемы ЖКТ и т.д.)")
    await state.update_data(num_meals=callback.data)
    await state.set_state(UserSurvey.food_prohibitions)


@user_private_router.message(UserSurvey.food_prohibitions)
async def food_prohibitions(message: types.Message, state: FSMContext, session: AsyncSession):
    user_id = int(message.from_user.id)
    await state.update_data(food_prohibitions=message.text)
    data = await state.get_data()

    if await orm_get_user_info(session, user_id):
        await orm_delete_user_info(session, user_id)

    await orm_add_user_info(session, data, user_id)
    await message.answer("Поздравляю, вы прошли опрос, все результаты записаны!")
    await asyncio.sleep(2)
    await message.answer("Теперь вы можете сгенерировать свой план питания, нажав /plan_meals")
    await state.clear()

#-------------------------------------/plan_meals/-------------------------------------------

@user_private_router.message(Command("plan_meals"))
async def plan_meals(message: types.Message, session: AsyncSession):
    data = await orm_get_user_info(session, int(message.from_user.id))

    result = calculate_nutrition(data)
    response = (
        f"Ваш план питания:\n"
        f"Калории в сутки: {result['calories']} ккал\n"
        f"Белки: {result['protein_g']} г\n"
        f"Жиры: {result['fat_g']} г\n"
        f"Углеводы: {result['carbs_g']} г"
    )

    await message.answer(response)

    breakfast = await orm_get_breakfast(session)
    snack = await orm_get_snack(session)
    dinner = await orm_get_dinner(session)
    evening_meal = await orm_get_evening_meal(session)


    meals = {
        "breakfast": breakfast,
        "snack": snack,
        "dinner": dinner,
        "evening_meal": evening_meal
    }

    weight = number_of_grams(result, meals["breakfast"])

    await message.answer(f"Вот ваш рацион питания на сегодня с учётом необходимых для вас калорий:\n"
                         f"Завтрак:\n{breakfast[0].name_dish}\n"
                         f"Калории:{breakfast[0].calories}\n"
                         f"Белки:\n"
                         f"Жиры:\n"
                         f"Углеводы:\n")


@user_private_router.message(~Command("admin"))
async def trash_remove(message: types.Message):
    await message.delete()












