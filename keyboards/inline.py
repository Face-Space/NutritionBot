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


def look_cooking_kb(dish_id: int, model_type: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Как готовить?", callback_data=f"look_cooking:{dish_id}:{model_type}"))
    kb.adjust(1)
    return kb


back_to_dish_info = InlineKeyboardBuilder()
back_to_dish_info.add(InlineKeyboardButton(text="Назад", callback_data="back_to_dish_info"))
back_to_dish_info.adjust(1)
