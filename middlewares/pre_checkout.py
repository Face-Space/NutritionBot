from datetime import date, datetime
from typing import Callable, Awaitable, Any, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag, extract_flags
from aiogram.types import TelegramObject, Message

from sqlalchemy.ext.asyncio import async_sessionmaker

from database.orm_query import orm_get_paid_users, orm_delete_temporary_dish
from keyboards.inline import tariffs_kb


class CheckIsPaidMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]
    ) -> Any:

        if event.successful_payment:
            # если оплата прошла успешно, тогда обходим этот мидлварь и идём дальше
            return await handler(event, data)

        user_id = event.from_user.id

        async with self.session_pool() as session:
            payment = await orm_get_paid_users(session, user_id)

            if not payment:
                await event.answer("💰 Чтобы начать пользоваться ботом, выберите тариф:", reply_markup=tariffs_kb.as_markup())

            else:
                end_subscription_str = payment[0].end_subscription
                end_subscription = datetime.strptime(end_subscription_str, "%Y-%m-%d").date()
                # перевод из типа str в тип date

                days_left = (end_subscription - date.today()).days
                # days это атрибут объекта timedelta (разница между двумя датами или временем) в Python, который
                # возвращает количество полных дней в этой разнице как целое число

                if days_left < 0:
                    await event.answer("Ваша подписка истекла, пожалуйста, пополните счёт для дальнейшего пользования:",
                                       reply_markup=tariffs_kb.as_markup())

                else:
                    # Если оплата есть, продолжаем обработку
                    return await handler(event, data)


class SubscriptionEndWarning(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool


    async def __call__(self,
                 handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                 event: TelegramObject,
                 data: Dict[str, Any]
    ) -> Any:

        # Проверяем, что событие - сообщение
        if not isinstance(event, Message):
            return await handler(event, data)

        # Получаем флаг о том, что это команда
        command_flag = get_flag(data, "command") # <- command_flag не работает, хз почему
        if command_flag or (event.text and event.text.startswith("/")):
            user_id = event.from_user.id
            async with self.session_pool() as session:
                payment = await orm_get_paid_users(session, user_id)

                end_subscription_str = payment[0].end_subscription
                end_subscription = datetime.strptime(end_subscription_str, "%Y-%m-%d").date()
                # перевод из типа str в тип date

                days_left = (end_subscription - date.today()).days
                # days это атрибут объекта timedelta (разница между двумя датами или временем) в Python, который
                # возвращает количество полных дней в этой разнице как целое число

                if 0 <= days_left <= 7:

                    if days_left == 0:
                        await event.answer(
                            f"У вас уже завтра закончится подписка , пополните счёт для дальнейшего "
                            f"пользования нажав \n/payment")

                        return await handler(event, data)

                    if days_left == 1:
                        days_word = "день"

                    elif days_left in [2, 3, 4]:
                        days_word = "дня"

                    else:
                        days_word = "дней"

                    await event.answer(
                        f"У вас закончится подписка через {days_left} {days_word}, пополните счёт для дальнейшего "
                        f"пользования, нажав \n/payment")

                    return await handler(event, data)

        return await handler(event, data)
