import asyncio
import logging
import json
import os

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LabeledPrice, PreCheckoutQuery
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv, find_dotenv

from database.models import Breakfast, Snack, Dinner, EveningMeal
from database.orm_query import *
from keyboards.inline import *
from services.calculate_nutrition import calculate_nutrition, number_of_grams
from states.FSM import UserSurvey
from bot_setup import bot


logger = logging.getLogger(__name__)
user_private_router = Router()
payment_router = Router()
load_dotenv(find_dotenv())


@user_private_router.message(CommandStart())
async def start_bot(message: types.Message, session: AsyncSession):
    await message.answer("Привет 👋, я - NutritionBot 🤖, бот, для управления питанием с нестандартным подходом "
                         "к планированию рациона 🥙\n")
    await asyncio.sleep(1.5)
    await message.answer("Я помогу вам контролировать свой вес, подбирая план питания 🥕 без жестких ограничений\n")
    await asyncio.sleep(1.5)
    await message.answer("Выберите, чтобы вы хотели сделать:\n\n"
                         "/start - Запуск/Перезапуск бота ▶️\n"
                         "/set_params - Установка индивидуальных параметров 📝 (возраст, вес, цель и т.д.)\n"
                         "/plan_meals - Генерация плана питания 🍍\n"
                         "/tariffs - Тарифы")


# Перед оплатой Telegram вызывает этот обработчик
@user_private_router.pre_checkout_query()
async def pre_checkout_q(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# Успешная оплата — Telegram отправляет ContentType.SUCCESSFUL_PAYMENT
@user_private_router.message(F.successful_payment)
async def successful_payment(message: types.Message, session: AsyncSession):
    await orm_mark_user_paid(session, message.from_user.id)
    await message.answer("Спасибо за оплату! \nТеперь доступ открыт ✅. \nДля перезапуска нажмите /start")


# ---------------------------------/set_params/---------------------------------------------

@user_private_router.message(Command("set_params"))
async def set_params(message: types.Message, state: FSMContext, session: AsyncSession):

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

    await plan_meal(message, session, Breakfast, "breakfast", "Завтрак", first_sending=True)
    await plan_meal(message, session, Dinner, "dinner", "Обед")
    await plan_meal(message, session, Snack, "snack", "Перекус")
    await plan_meal(message, session, EveningMeal, "evening_meal", "Ужин")


async def plan_meal(message: types.Message, session: AsyncSession, model, food_intake: str,
                    message_meal_name: str, first_sending=False):

    data = await orm_get_user_info(session, int(message.from_user.id))
    result = calculate_nutrition(data)

    if first_sending:
        await message.answer(f"Вот ваш рацион питания на сегодня с учётом необходимых для вас калорий:\n\n")
        response = (
            f"Калории в сутки: {result['calories']} кКал.\n"
            f"Белки: {result['protein_g']} г.\n"
            f"Жиры: {result['fat_g']} г.\n"
            f"Углеводы: {result['carbs_g']} г."
        )
        await message.answer(response)

    meal_name = await orm_get_random_dish(session, model)
    meal_weight = number_of_grams(result, meal_name, food_intake)
    meal_calories = number_of_grams(result, meal_name, food_intake, return_weight=False)

    while True:
        if meal_weight > 600:  # т.к. больше полкило еды съесть довольно трудно, берём из БД что-то калорийнее
            meal_name = await orm_get_random_dish(session, model)

            meal_weight = number_of_grams(result, meal_name, food_intake)
            meal_calories = number_of_grams(result, meal_name, food_intake, return_weight=False)
        else:
            break

    await message.answer(f"{message_meal_name}:\n{meal_name[0].name_dish}.\n\n"
                         f"Необходимое кол-во грамм в одной порции: {round(meal_weight, 1)}\n\n"
                         f"Калории: {round(meal_calories, 1)} кКал.\n"
                         f"Белки: {round(meal_name[0].proteins * (meal_weight / 100), 1)} г.\n"
                         f"Жиры: {round(meal_name[0].fats * (meal_weight / 100), 1)} г.\n"
                         f"Углеводы: {round(meal_name[0].carbohydrates * (meal_weight / 100), 1)} г.\n",
                         reply_markup=look_cooking_kb(meal_name[0].id, food_intake).as_markup())

    meal_info = {
        "name_dish": meal_name[0].name_dish,
        "dish_id": meal_name[0].id,
        "proteins": meal_name[0].proteins,
        "fats": meal_name[0].fats,
        "carbohydrates": meal_name[0].carbohydrates
    }

    meal_info_json = json.dumps(meal_info)
    # перед сохранением преобразуем в JSON строку, т.к. SQLite не умеет автоматически сериализовать сложные объекты,
    # такие как словари, и требует примитивные типы: строки, числа и т.п

    data = {
        "message_meal_name": message_meal_name,
        "meal_info": meal_info_json,
        "meal_calories": meal_calories,
        "meal_weight": meal_weight,
        "food_intake": food_intake
    }

    await orm_save_temporary_info(session, data, message.from_user.id)


@user_private_router.callback_query(F.data.startswith("look_cooking:"))
async def look_cook(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    dish_id = int(callback.data.split(":")[1])
    model_type = str(callback.data.split(":")[2])

    model = {
        "breakfast": Breakfast,
        "snack": Snack,
        "dinner": Dinner,
        "evening_meal": EveningMeal
    }.get(model_type)

    meal = await orm_get_dish_by_id(session, model, dish_id)
    await bot.edit_message_text(text=f'Приготовление блюда "{meal[0].name_dish}":\n\n'
                                        f'{meal[0].description}',
                                chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                reply_markup=back_to_dish_info(model_type).as_markup())


@user_private_router.callback_query(F.data.startswith("back_to_dish_info"))
async def back_handler(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    food_intake = callback.data.split(":")[1]
    data = await orm_get_temporary_dish_info(session, callback.from_user.id, food_intake)
    meal_info = json.loads(data[0].meal_info)

    await bot.edit_message_text(text=f"{data[0].message_meal_name}:\n{meal_info["name_dish"]}.\n\n"
                         f"Необходимое кол-во грамм в одной порции: {round(data[0].meal_weight, 1)}\n\n"
                         f"Калории: {round(data[0].meal_calories, 1)} кКал.\n"
                         f"Белки: {round(meal_info["proteins"] * (data[0].meal_weight / 100), 1)} г.\n"
                         f"Жиры: {round(meal_info["fats"] * (data[0].meal_weight / 100), 1)} г.\n"
                         f"Углеводы: {round(meal_info["carbohydrates"] * (data[0].meal_weight / 100), 1)} г.\n",
                         chat_id=callback.message.chat.id,
                         message_id=callback.message.message_id,
                         reply_markup=look_cooking_kb(meal_info["dish_id"], data[0].food_intake).as_markup())


@user_private_router.message(~Command("admin"))
async def trash_remove(message: types.Message):
    await message.delete()



