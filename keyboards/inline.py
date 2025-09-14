from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder



gender_kb = InlineKeyboardBuilder()
gender_kb.add(InlineKeyboardButton(text="Мужской", callback_data="male"),
              InlineKeyboardButton(text="Женский", callback_data="female"))


activity_level_kb = InlineKeyboardBuilder()
activity_level_kb.add(InlineKeyboardButton(text="Низкий", callback_data="low"),
                      InlineKeyboardButton(text="Средний", callback_data="moderate"),
                      InlineKeyboardButton(text="Высокий", callback_data="high"))


target_kb = InlineKeyboardBuilder()
target_kb.add(InlineKeyboardButton(text="Снижение веса", callback_data="lose"),
              InlineKeyboardButton(text="Поддержание веса", callback_data="maintenance"),
              InlineKeyboardButton(text="Набор массы", callback_data="gain"))


num_meals_kb = InlineKeyboardBuilder()
num_meals_kb.add(InlineKeyboardButton(text="2", callback_data="2"),
                 InlineKeyboardButton(text="3", callback_data="3"),
                 InlineKeyboardButton(text="4", callback_data="4"),
                 InlineKeyboardButton(text="5", callback_data="5"))

