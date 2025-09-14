from typing import Dict


def calculate_nutrition(age, gender, weight, height, activity_level, target) -> Dict[str, int]:
    # Выбор формулы расчета норм
    # На практике используют проверенные формулы для базового обмена веществ (BMR) и общих норм калорий:
    # Формула Миффлина-Сан Жеора для BMR.

    s = 5 if gender == 'male' else -161
    bmr = 10 * weight + 6.25 * height - 5 * age + s

    activity_miltipliers = {
        'low': 1.2,
        'moderate': 1.55,
        'high': 1.9
    }
    calories = bmr * activity_miltipliers.get(activity_level, 1.2)

    if target == 'lose':
        calories -= 500  # Дефицит калорий для похудения
    elif target == 'gain':
        calories += 500  # Профицит калорий для набора массы

    # Пример распределения макронутриентов:
    protein = 2 * weight  # г белка на кг
    fat = 0.8 * weight  # г жиров на кг
    carbs = (calories - (protein * 4 + fat * 9)) / 4  # г углеводов

    return {
        'calories': round(calories),
        'protein_g': round(protein),
        'fat_g': round(fat),
        'carbs_g': round(carbs)
    }



