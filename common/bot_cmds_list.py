from aiogram.types import BotCommand

private = [
    BotCommand(command="start", description="Запуск/Перезапуск бота"),
    BotCommand(command="set_params", description="Установка индивидуальных параметров (возраст, вес, цель и т.д.)"),
    BotCommand(command="add_product", description="Добавление продуктов в базу пользователя"),
    BotCommand(command="plan_meals", description="Генерация плана питания")
]