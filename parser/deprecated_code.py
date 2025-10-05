import asyncio
import concurrent.futures
import os
from pathlib import Path

from bs4 import BeautifulSoup
import requests

from database.engine import engine
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import EveningMeal, Breakfast, Snack, Dinner


async def bulk_insert(data_list, time_eat):
    async with AsyncSession(engine) as session:
        objects = [time_eat(**k) for k in data_list]
        session.add_all(objects)
        await session.commit()


headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/134.0.0.0 Safari/537.36"
}

current_path = Path(__file__).parent
# os.makedirs(data_path, exist_ok=True)
url = "https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"

req = requests.get(url, headers=headers)
src = req.text

with open(f"{current_path}/index.html", "w", encoding="utf-8") as file:
    file.write(src)

# сохраняем страницу в файл, чтобы продолжить работать с ней если вдруг получим бан

with open(f"{current_path}/index.html", encoding="utf-8") as file:
    src = file.read()


soup = BeautifulSoup(src, "lxml")
all_products_hrefs = soup.find_all(class_="mzr-tc-group-item-href")
necessary_categories = ["Каши", "Вторые блюда", "Первые блюда", "Закуски", "Десерты"]
meals = [EveningMeal, Breakfast, Snack, Breakfast,  Dinner]  # порядок записи данных в таблицы,
                                                             # относительно их расположения на странице
time_to_eat = None


all_categories_dict = {}
for item in all_products_hrefs:
    if item.text in necessary_categories:
        item_text = item.text
        all_categories_dict[item_text] = "https://health-diet.ru" + item.get('href')


# with open("all_categories_dict.json", "w", encoding="utf-8") as file:
#     json.dump(all_categories_dict, file, indent=4,ensure_ascii=False)


# цикл, на каждой итерации которого мы будем заходить на страницу категории, собирать с неё данные о всех
# товарах и их хим.составе и записывать всё это в файл

iteration_count = int(len(all_categories_dict)) - 1
count = 0
print(f"Всего итераций: {iteration_count}")


for category_name, category_href in all_categories_dict.items():

    req = requests.get(url=category_href, headers=headers)
    src = req.text

    # сохранение страницы под именем категории
    with open(f"{current_path}/{count}_{category_name}.html", "w", encoding="utf-8") as file:
        file.write(src)

    # откроем и сохраним код страницы в переменную
    with open(f"{current_path}/{count}_{category_name}.html", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    # проверка страницы на наличие таблицы с продуктами
    alert_block = soup.find(class_="uk-alert-danger")
    if alert_block is not None:
        continue

    # собираем данные продуктов
    products_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")
    products_info = []
    num = 0

    # из каждого tr тэга собираем td тэги в которых и содержится нужная нам инфа
    for i in products_data:
        products_tds = i.find_all("td")  # здесь хранится список из td

        dish_name = products_tds[0].find("a").text
        if "Торт" in dish_name:  # торты не полезные, поэтому скипаем их нах
            continue

        # with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        href = "https://health-diet.ru" + products_tds[0].find("a").get("href")
        desc_req = requests.get(url=href, headers=headers)
        desc_src = desc_req.text
        desc_soup = BeautifulSoup(desc_src, "lxml")

        remove_table = str.maketrans({",": ".", "г": ""})
        calories = products_tds[1].text.translate(remove_table).replace("кКал", "").strip()
        proteins = products_tds[2].text.translate(remove_table).replace("кКал", "").strip()
        fats = products_tds[3].text.translate(remove_table).replace("кКал", "").strip()
        carbohydrates = products_tds[4].text.translate(remove_table).replace("кКал", "").strip()
        description = desc_soup.find(class_="mzr-recipe-view-description-tc").text.strip()
        # description = "description"

        data = {
            "name_dish": dish_name,
            "calories": float(calories),
            "proteins": float(proteins),
            "fats": float(fats),
            "carbohydrates": float(carbohydrates),
            "description": description
        }

        products_info.append(data)
        num += 1
        print(f"Название категории # {num} спарсено")

    time_to_eat = meals[count]
    asyncio.run(bulk_insert(products_info, time_to_eat))
    print("Категория успешно записана в БД")
    products_info.clear()

    count += 1
    print(f"# Итерация {count}. {category_name} записан...")
    iteration_count = iteration_count - 1
    if iteration_count == 0:
        print("Работа завершена")
        break

    print(f"Осталось итераций: {iteration_count}")


