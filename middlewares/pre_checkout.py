from typing import Callable, Awaitable, Any, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, LabeledPrice, PreCheckoutQuery
import os

from sqlalchemy.ext.asyncio import async_sessionmaker

from bot_setup import bot
from database.orm_query import orm_get_paid_users, orm_delete_temporary_dish
from keyboards.inline import tariffs_kb


class CheckIsPaidMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any],
    ):

        if event.successful_payment:
            # если оплата прошла успешно, тогда обходим этот мидлварь и идём дальше
            return await handler(event, data)

        user_id = event.from_user.id

        async with self.session_pool() as session:
            # очищаем временное хранилище для конкретного юзера в БД перед запуском
            await orm_delete_temporary_dish(session, user_id)
            payment = await orm_get_paid_users(session, user_id)

            if not payment:
                await event.answer("💰 Чтобы начать пользоваться ботом, выберите тариф:", reply_markup=tariffs_kb.as_markup())

                # await bot.send_invoice(
                #     event.chat.id,
                #     title="Подписка на месяц",
                #     description="Доступ к боту",
                #     provider_token=os.getenv("PAYMENT_TOKEN"),
                #     currency="rub",
                #     prices=[LabeledPrice(label="Доступ к боту на 1 месяц", amount=500 * 100)],
                #     start_parameter="month_subscription",
                #     payload="user_subscription"
                # )


            else:
                # Если оплата есть, продолжаем обработку
                return await handler(event, data)
