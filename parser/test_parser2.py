import csv
import json
import os

from bs4 import BeautifulSoup
import requests


headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
    Chrome/134.0.0.0 Safari/537.36"
}

url = "https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"

req = requests.get(url, headers=headers)
src = req.text

with open("index.html", "w", encoding="utf-8") as file:
    file.write(src)

# сохраняем страницу в файл, чтобы продолжить работать с ней если вдруг получим бан

with open("index.html", encoding="utf-8") as file:
    src = file.read()


soup = BeautifulSoup("lxml", src)
all_products_hrefs = soup.find_all(class_="mzr-tc-group-item-href")
necessary_categories = ["Каши", "Вторые блюда", "Первые блюда", "Закуски", "Десерты"]


all_categories_dict = {}
for item in all_products_hrefs:
    if item.text in necessary_categories:
        item_text = item.text
        item_href = "https://health-diet.ru" + item.get('href')

        all_categories_dict[item_text] = item_href


# with open("all_categories_dict.json", "w", encoding="utf-8") as file:
#     json.dump(all_categories_dict, file, indent=4,ensure_ascii=False)


# цикл, на каждой итерации которого мы будем заходить на страницу категории, собирать с неё данные о всех
# товарах и их хим.составе и записывать всё это в файл

count = 0

for category_name, category_href in all_categories_dict.items():

    req = requests.get(url=category_href, headers=headers)
    src = req.text
    # os.makedirs("E:/MyPetProjects/NutritionBot/parser/html_pages", exist_ok=True)

    # сохранение страницы под именем категории
    with open(f"data/{count}_{category_name}.html", "w", encoding="utf-8") as file:
        file.write(src)

    # откроем и сохраним код страницы в переменную
    with open(f"data/{count}_{category_name}.html", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    # проверка страницы на наличие таблицы с продуктами
    alert_block = soup.find(class_="uk-alert-danger")
    if alert_block is not None:
        continue

    # собираем заголовки таблицы
    table_head = soup.find("mzr-tc-group-table").find("tr").find_all("th")
    product = table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbohydrates = table_head[4].text

    # запись данных в таблицу
    with open(f"data/{count}_{category_name}.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow((product, calories, proteins, fats, carbohydrates))

    # собираем данные продуктов
    products_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")

    product_info = []

    # из каждого tr тэга собираем td тэги в которых и содержится нужная нам инфа
    for i in products_data:
        products_tds = i.find_all("td")

        title = products_tds[0].find("a").text




