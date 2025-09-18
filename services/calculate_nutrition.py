from typing import Dict


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





