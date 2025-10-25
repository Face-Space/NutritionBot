from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
# описывает входящее Telegram-событие (например, сообщение, callback query и т.п.)
from sqlalchemy.ext.asyncio import async_sessionmaker


class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        self.session_pool = session_pool

    # Определяется метод __call__, позволяющий объекту класса вызываться как функция
    # Хотя в коде явно этот объект не вызывается через скобки, сам фреймворк Aiogram при получении события вызывает этот метод

    async def __call__(self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        # Это аргумент — функция‑обработчик (handler), которую middleware вызовет после своей работы
        # Callable — тип Python для функций.
        # Внутри квадратных скобок — список аргументов, которые handler ожидает

        # Первый аргумент: TelegramObject — это объект события Telegram (например, сообщение, команда, callback-кнопка,
        # любой update)

        # Второй аргумент: Dict[str, Any] — это словарь дополнительных данных (context data, сюда middleware кладут
        # всякую полезную информацию, которую потом могут использовать остальные слои — фильтры, хендлеры

        event: TelegramObject,
        # Это сам объект события, пришедший из Telegram — не обязательно сообщение, это может быть любой тип апдейта (callback, inline‑query, edited message и т.д.).
        # Используется для доступа к содержимому update: сообщение, id пользователя, тип события.
        # В хендлер передаётся так, чтобы фильтры и бизнес‑логика работали со всеми типами событий.

        data: Dict[str, Any]
        # Это словарь данных, сопровождающий событие по всей цепочке обработки в aiogram.
        # В middleware в этот словарь можно складывать любые объекты (например, сессию SQLAlchemy, текущего пользователя,
        # конфиги, флаги).
        # Все значения из этого словаря aiogram умеет разбирать и подставлять их в параметры ваших хендлеров по имени.
        # Например, если в data есть 'session': ..., то ваш хендлер с параметром session сможет получить этот объект
        # автоматически

    ):
        async with self.session_pool() as session:
            data['session'] = session
            return await handler(event, data)


    # Middleware захватывает событие, создает асинхронную сессию базы данных, кладет ее в data,
    # и потом вызывает дальше обработчик сессии, передавая ему возможность работать с базой через data['session'].
    # После завершения обработчика сессия автоматически закрывается.
    # Такой подход позволяет удобно получать сессию базы данных для каждого события Telegram, не создавая ее каждый
    # раз вручную в обработчиках и гарантируя корректное закрытие сессии.


