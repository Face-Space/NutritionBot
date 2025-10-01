import asyncio
import logging
import random
import time
import concurrent.futures
from functools import partial
from typing import Optional

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import engine
from database.models import Breakfast, Snack, Dinner, EveningMeal


logger = logging.getLogger()

def create_driver() -> webdriver.Chrome:
    user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/140.0.0.0 Safari/537.36")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"--user-agent={user_agent}")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")


    driver = webdriver.Chrome(options=chrome_options)

    stealth(
                    driver,
                    languages=["ru-RU", "ru"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True
                )
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


all_data = []


def parse_description(href, driver) -> Optional[str]:
    try:
        driver.get(href)
        time.sleep(random.uniform(1, 2))
        description = driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div[2]/div/p').text
        print("Описание блюда спарсено!")
        return description

    except Exception as e:
        logger.info(f"Ошибка парсинга {href}: {e}")
        print(f"Ошибка парсинга {href}: {e}")
        driver.quit()
        return None


def parse_dishes(driver):
    table = (
        driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div/table/tbody').find_elements(
            By.TAG_NAME, "tr"))


    for i in table:
        tr_tag = i.find_element(By.TAG_NAME, "a")
        href = tr_tag.get_attribute("href")

        dish_name = tr_tag.text
        if "Торт" in dish_name:
            continue

        remove_table = str.maketrans({",": ".", "г": ""})
        calories = i.find_elements(By.CLASS_NAME, "uk-text-right")[0].text.translate(remove_table).replace("кКал",
                                                                                                           "").strip()
        proteins = i.find_elements(By.CLASS_NAME, "uk-text-right")[1].text.translate(remove_table).replace("кКал",
                                                                                                           "").strip()
        fats = i.find_elements(By.CLASS_NAME, "uk-text-right")[2].text.translate(remove_table).replace("кКал",
                                                                                                       "").strip()
        carbohydrates = i.find_elements(By.CLASS_NAME, "uk-text-right")[3].text.translate(remove_table).replace("кКал",
                                                                                                                "").strip()

        # driver.execute_script("window.open(arguments[0], '_blank')", href)
        # driver.switch_to.window(driver.window_handles[-1])
        # time.sleep(random.randint(1, 3))


        data = {
            "name_dish": dish_name,
            "href": href,
            "calories": float(calories),
            "proteins": float(proteins),
            "fats": float(fats),
            "carbohydrates": float(carbohydrates)
        }

        print("Словарь добавлен")
        all_data.append(data)

    # driver.close()
    # driver.switch_to.window(driver.window_handles[0])

    # driver.quit()

    print("Запуск параллельного парсинга")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        hrefs = [dish["href"] for dish in all_data]

        # partial - инструмент для создания новой функции на базе существующей, при этом некоторые аргументы исходной
        # функции фиксируются заранее.
        print("1111")
        partial_func = partial(parse_description, driver=driver)
        print("2222")
        descriptions = list(executor.map(partial_func, hrefs))
        print("3333")
        # применяет функцию последовательно ко всем элементам итерируемого объекта, но при этом
        # распределяет работу между потоками, выполняя её параллельно
    print("Описание спарсено")

    final_data = []
    for dish_info, desc in zip(all_data, descriptions):
        if desc is None:
            desc = ""

        del dish_info["href"]
        dish_info["description"] = desc
        final_data.append(dish_info)

    print(final_data)
    return final_data


def main_actions(category_dish, time_eat, driver):
    category_dish.click()
    data = parse_dishes(driver)
    asyncio.run(_bulk_insert(data, time_eat))
    all_data.clear()


async def _bulk_insert(data_list, time_eat):
    async with AsyncSession(engine) as session:
        objects = [time_eat(**item) for item in data_list]
        session.add_all(objects)
        await session.commit()


def parse_nutrition():
    driver = create_driver()

    # Парсинг завтрака
    driver.get("https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie")
    porridge = driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div[5]/div[2]/div[1]/a')
    time_eat_class = Breakfast
    main_actions(porridge, time_eat_class, driver)
    print("Завтрак спарсен!!!!!!!!!")

    # Парсинг десертов для завтрака
    driver.get("https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie")
    desserts = driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div[5]/div[1]/div[5]/a')
    time_eat_class = Snack
    main_actions(desserts, time_eat_class, driver)

    # Парсинг обеда
    driver.get("https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie")
    dinner = driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div[5]/div[2]/div[3]/a')
    time_eat_class = Dinner
    main_actions(dinner, time_eat_class, driver)

    # Парсинг ужина
    driver.get("https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie")
    evening_meal = driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div[5]/div[1]/div[2]/a')
    time_eat_class = EveningMeal
    main_actions(evening_meal, time_eat_class, driver)

    driver.quit()


if __name__ == "__main__":
    parse_nutrition()


