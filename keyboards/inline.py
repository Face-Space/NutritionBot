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


admin_kb = InlineKeyboardBuilder()
admin_kb.add(InlineKeyboardButton(text="Спарсить завтрак", callback_data="parse_breakfast"))
admin_kb.adjust(1)


look_cooking = InlineKeyboardBuilder()
look_cooking.add(InlineKeyboardButton(text="Как готовить?", callback_data="look_cooking"))
look_cooking.adjust(1)

