import logging
import asyncio


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

class ParsingManager:
    active_parsing_users:set[int]



@admin_router.message(Command("admin"))
async def start_changes(message: types.Message, state: FSMContext):
    await message.answer("Если хотите заново спарсить еду для приёма пищи, нажмите кнопку ниже",
                         reply_markup=admin_kb.as_markup())
    await state.clear()


@admin_router.callback_query(F.data == "parse_breakfast")
async def parse_breakfast(callback: CallbackQuery):
    async with asyncio.Lock():
        if callback.from_user.id in ParsingManager.active_parsing_users:
            await callback.message.answer("Парсинг уже запущен, пожалуйста подождите!", show_alert=True)
            logger.warning(f"Пользователь {callback.from_user.first_name} уже запустил парсинг")
            return

        ParsingManager.active_parsing_users.add(callback.from_user.id)

    await callback.answer()
    await callback.message.answer("Идёт парсинг в БД, обычно это занимает около 10 минут, пожалуйста подождите")

    try:
        await scrape_and_store()
    finally:
        async with asyncio.Lock():
            ParsingManager.active_parsing_users.remove(callback.from_user.id)


    await callback.message.answer("Парсинг успешно окончен, можете тестировать")


