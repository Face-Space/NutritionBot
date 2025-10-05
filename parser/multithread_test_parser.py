import asyncio
import concurrent.futures
import logging
import os
import time
from pathlib import Path

from bs4 import BeautifulSoup
import requests

from database.engine import engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from database.models import EveningMeal, Breakfast, Snack, Dinner


logger = logging.getLogger(__name__)
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/134.0.0.0 Safari/537.36"
}
current_path = Path(__file__).parent / "data"


def save_page(content: str, filename: str):
    with open(filename, "w",encoding="utf=8") as file:
        file.write(content)


def load_page(filename: str) -> str:
    with open(filename, encoding="utf-8") as file:
        return file.read()


meals = [EveningMeal, Breakfast, Snack, Dinner]  # порядок записи данных в таблицы,
                                                 # относительно их расположения на странице


async def _bulk_insert(data_list, time_eat):
    async with AsyncSession(engine) as session:
        # Удаляем все строки из таблицы модели time_eat
        await session.execute(delete(time_eat))
        await session.commit()

        # Добавляем новые объекты
        objects = [time_eat(**k) for k in data_list]
        session.add_all(objects)
        await session.commit()


def fetch_product_data(products_tds):
    dish_name = products_tds[0].find("a").text

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

    try:
        print(f'Инфа с "{dish_name}" успешно собрана')
        return {
            "name_dish": dish_name,
            "calories": float(calories),
            "proteins": float(proteins),
            "fats": float(fats),
            "carbohydrates": float(carbohydrates),
            "description": description
        }

    except ValueError as e:
        logger.info(f"Ошибка, информация о продукте не собрана: {e}")
        return None


def get_categories(src):
    soup = BeautifulSoup(src, "lxml")
    all_products_hrefs = soup.find_all(class_="mzr-tc-group-item-href")
    necessary_categories = ["Каши", "Вторые блюда", "Первые блюда", "Закуски"]

    categories = {
        item.text: "https://health-diet.ru" + item.get('href')
        for item in all_products_hrefs if item.text in necessary_categories
    }

    return categories


async def scrape_and_store():
    start_time = time.time()
    url = "https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"

    req = requests.get(url, headers=headers)
    req.raise_for_status()
    content = req.text
    filename = f"{current_path}/index.html"

    # сохраняем страницу в файл, чтобы продолжить работать с ней если вдруг получим бан
    save_page(content, filename)
    categories_src = load_page(filename)

    categories = get_categories(categories_src)
    logger.info(f"Найдено категорий для обработки: {len(categories)}")
    count = 0

    # iteration_count = int(len(all_categories_dict))
    # print(f"Всего итераций: {iteration_count}")


    for category_name, category_href in categories.items():
        req = requests.get(url=category_href, headers=headers)
        req.raise_for_status()
        # позволяет избежать "тихого" игнорирования ошибок и упрощает обработку неудавшихся запросов
        category_html = req.text
        page_filename = f"{current_path}/{count}_{category_name}.html"

        save_page(category_html, page_filename)
        dish_src = load_page(page_filename)

        soup = BeautifulSoup(dish_src, "lxml")

        # проверка страницы на наличие таблицы с продуктами
        alert_block = soup.find(class_="uk-alert-danger")
        if alert_block is not None:
            continue

        # собираем данные продуктов
        products_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            products_info = list(filter(None, executor.map(fetch_product_data, [p.find_all("td") for p in products_data])))
            # Если в качестве функции передать None, filter оставит только истинные значения
            # из последовательности (отфильтрует ложные).


        time_to_eat = meals[count]
        asyncio.run(_bulk_insert(products_info, time_to_eat))
        # print("Категория успешно записана в БД")

        count += 1
        iteration_count = iteration_count - 1
        # print(f"# Итерация {count}. {category_name} записан...")
        logger.info(f"# Итерация {count}. {category_name} записан...")
        # print(f"Осталось итераций: {iteration_count}")

        if iteration_count == 0:
            end_time = time.time()
            duration = end_time - start_time
            print(f"Работа завершена за {duration:.2f} секунд")
            break


if __name__ == "__main__":
    asyncio.run(scrape_and_store())


