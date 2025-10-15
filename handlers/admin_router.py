import logging


from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from filters import IsAdmin
from keyboards.inline import admin_kb
from parser.multithread_parser import scrape_and_store

logger = logging.getLogger(__name__)


admin_router = Router()
admin_router.message.filter(IsAdmin())


@admin_router.message(Command("admin"))
async def start_changes(message: types.Message, state: FSMContext):
    await message.answer("Если хотите заново спарсить еду для приёма пищи, нажмите кнопку ниже",
                         reply_markup=admin_kb.as_markup())
    await state.clear()


@admin_router.callback_query(F.data == "parse_breakfast")
async def parse_breakfast(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Идёт парсинг в БД, обычно это занимает около 10 минут, пожалуйста подождите")
    await scrape_and_store()
    await callback.message.answer("Парсинг успешно окончен, можете тестировать")


