import logging
import sys
from pathlib import Path
from aiogram import Dispatcher, Bot, types
import asyncio
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))
# Эта строчка гарантирует, что директория, где расположен текущий файл, будет первой
# в списке путей поиска модулей Python


from utils.logger import setup_logging
from common.bot_cmds_list import private
from filters.chat_types import admins_list
from handlers.user_private import user_private_router


bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher()

dp.include_router(user_private_router)


async def _on_startup():
    await bot.send_message(admins_list[0], "Бот работает для всех")
    print("бот заработал")


async def _on_shutdown():
    await bot.send_message(admins_list[0], "Бот лёг")
    print("бот лёг")


async def main():
    try:
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Запуск телеграм бота")

        dp.startup.register(_on_startup)
        dp.shutdown.register(_on_shutdown)
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

    except Exception as e:
        print(f"Ошибка запуска бота: {e}")


if __name__ == "__main__":
    asyncio.run(main())
