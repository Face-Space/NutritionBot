from aiogram.fsm.state import StatesGroup, State


class UserSurvey(StatesGroup):
    age = State()
    gender = State()
    weight = State()
    height = State()
    activity_level = State()
    target = State()
    number_of_meals = State()
    food_prohibitions = State()
