from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
# описывает входящее Telegram-событие (например, сообщение, callback query и т.п.)
from sqlalchemy.ext.asyncio import async_sessionmaker


class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    # Определяется метод __call__, позволяющий объекту класса вызываться как функция
    async def __call__(self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ):
        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)


    # Middleware захватывает событие, создает асинхронную сессию базы данных, кладет ее в data,
    # и потом вызывает дальше обработчик сессии, передавая ему возможность работать с базой через data['session'].
    # После завершения обработчика сессия автоматически закрывается.
    # Такой подход позволяет удобно получать сессию базы данных для каждого события Telegram, не создавая ее каждый
    # раз вручную в обработчиках и гарантируя корректное закрытие сессии.


