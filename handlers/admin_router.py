import logging


from aiogram import Router, types, F
from aiogram.filters import Filter, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from filters import IsAdmin
from keyboards.inline import admin_kb
from parser.dishes_parser import DishesParser

logger = logging.getLogger(__name__)


admin_router = Router()
admin_router.message.filter(IsAdmin())


@admin_router.message(Command("admin"))
async def start_changes(message: types.Message, state: FSMContext):
    await message.answer("Что хотите сделать? Каждая из кнопок парсит в базу данных инфу с сайта:\n"
                         "https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie\n"
                         "",
                         reply_markup=admin_kb.as_markup())
    await state.clear()


@admin_router.callback_query(F.data == "parse_breakfast")
async def parse_breakfast(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Идёт парсинг завтрака в БД, пожалуйста подождите")

    url = "https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"
    dishes_parser = DishesParser(str(callback.message.from_user.id))
    dishes_parser.initialize()
    dishes_parser.parse_dishes(url)

    await callback.message.answer("Парсинг завтрака в БД успешно окончен, можете тестировать")


