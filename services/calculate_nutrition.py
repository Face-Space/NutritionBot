from datetime import timedelta
from typing import Dict
import logging


logger = logging.getLogger(__name__)

def calculate_nutrition(data: list) -> Dict[str, int]:
    user_info = data[0]

    # age, gender, weight, height, activity_level, target, food_proh
    # Выбор формулы расчета норм
    # На практике используют проверенные формулы для базового обмена веществ (BMR) и общих норм калорий:
    # Формула Миффлина-Сан Жеора для BMR.

    s = 5 if user_info.gender == 'male' else -161
    bmr = 10 * user_info.weight + 6.25 * user_info.height - 5 * user_info.age + s

    activity_miltipliers = {
        'low': 1.2,
        'moderate': 1.55,
        'high': 1.9
    }
    calories = bmr * activity_miltipliers.get(user_info.activity_level, 1.2)

    if user_info.target == 'lose':
        calories -= 500  # Дефицит калорий для похудения
    elif user_info.target == 'gain':
        calories += 500  # Профицит калорий для набора массы

    # Пример распределения макронутриентов:
    protein = 2 * user_info.weight  # г белка на кг
    fat = 0.8 * user_info.weight  # г жиров на кг
    carbs = (calories - (protein * 4 + fat * 9)) / 4  # г углеводов

    return {
        'calories': round(calories),
        'protein_g': round(protein),
        'fat_g': round(fat),
        'carbs_g': round(carbs)
    }


def number_of_grams(data: dict, meals, food_intake, return_weight = True):
    necessary_calories = None

    if food_intake == "breakfast":
        necessary_calories = data['calories'] * 25 / 100
        # здесь считаем, что для завтрака нужно 25% от суточного потребления калорий,
        # в остальных похожий расчёт

    elif food_intake == "snack":
        necessary_calories = data['calories'] * 10 / 100

    elif food_intake == "dinner":
        necessary_calories = data['calories'] * 35 / 100

    elif food_intake == "evening_meal":
        necessary_calories = data['calories'] * 30 / 100

    try:
        weight = necessary_calories / meals[0].calories * 100
        # считаем количество грамм за один приём пищи
        if return_weight:
            return weight

        return necessary_calories

    except ZeroDivisionError as e:
        logger.error("Ошибка, в БД калорийность продукта 0 калорий!")


def parse_interval(payload: str) -> timedelta:
    mapping = {
        "1 месяц": timedelta(days=30),
        "6 месяцев": timedelta(days=183),
        "1 год": timedelta(days=365)
    }

    return mapping.get(payload, timedelta(days=0))

