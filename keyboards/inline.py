from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder



gender_kb = InlineKeyboardBuilder()
gender_kb.add(InlineKeyboardButton(text="Мужской", callback_data="male"),
              InlineKeyboardButton(text="Женский", callback_data="female"),
              InlineKeyboardButton(text="Отмена", callback_data="cancel"))


activity_level_kb = InlineKeyboardBuilder()
activity_level_kb.add(InlineKeyboardButton(text="Низкий", callback_data="low"),
                      InlineKeyboardButton(text="Средний", callback_data="moderate"),
                      InlineKeyboardButton(text="Высокий", callback_data="high"),
                      InlineKeyboardButton(text="Отмена", callback_data="cancel"))
activity_level_kb.adjust(1)


target_kb = InlineKeyboardBuilder()
target_kb.add(InlineKeyboardButton(text="Снижение веса", callback_data="lose"),
              InlineKeyboardButton(text="Поддержание веса", callback_data="maintenance"),
              InlineKeyboardButton(text="Набор массы", callback_data="gain"),
              InlineKeyboardButton(text="Отмена", callback_data="cancel"))
target_kb.adjust(1)


admin_kb = InlineKeyboardBuilder()
admin_kb.add(InlineKeyboardButton(text="Спарсить всё", callback_data="parse_breakfast"))
admin_kb.adjust(1)


def look_cooking_kb(dish_id: int, model_type: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Как готовить?", callback_data=f"look_cooking:{dish_id}:{model_type}"))
    kb.adjust(1)
    return kb


def back_to_dish_info(food_intake: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Назад", callback_data=f"back_to_dish_info:{food_intake}"))
    kb.adjust(1)
    return kb


tariffs_kb = InlineKeyboardBuilder()
tariffs_kb.add(InlineKeyboardButton(text="1 месяц - 500р.", callback_data="tariff_1 месяц_500"),
               InlineKeyboardButton(text="6 месяцев - 2500р.", callback_data="tariff_пол года_2500"),
               InlineKeyboardButton(text="1 год - 5000р.", callback_data="tariff_1 год_5000"))
tariffs_kb.adjust(1)


cancel_kb = InlineKeyboardBuilder()
cancel_kb.add(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
cancel_kb.adjust(1)