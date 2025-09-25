import asyncio
import random
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import engine
from database.models import Breakfast
from database.orm_query import orm_add_breakfast

chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)


chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-plugins")


driver.get("https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie")
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
driver.implicitly_wait(20)
all_data = []


def parse_dishes():
    table = (
        driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div/table/tbody').find_elements(
            By.TAG_NAME, "tr"))


    for i in table:
        tr_tag = i.find_element(By.TAG_NAME, "a")
        href = tr_tag.get_attribute("href")

        dish_name = tr_tag.text
        remove_table = str.maketrans({",": ".", "г": ""})

        calories = i.find_elements(By.CLASS_NAME, "uk-text-right")[0].text.translate(remove_table).replace("кКал",
                                                                                                           "").strip()
        proteins = i.find_elements(By.CLASS_NAME, "uk-text-right")[1].text.translate(remove_table).replace("кКал",
                                                                                                           "").strip()
        fats = i.find_elements(By.CLASS_NAME, "uk-text-right")[2].text.translate(remove_table).replace("кКал",
                                                                                                       "").strip()
        carbohydrates = i.find_elements(By.CLASS_NAME, "uk-text-right")[3].text.translate(remove_table).replace("кКал",
                                                                                                                "").strip()

        driver.execute_script("window.open(arguments[0], '_blank')", href)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)

        description = driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div[2]/div/p').text
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        data = {"name_dish": dish_name, "description": description, "calories": float(calories),
                "proteins": float(proteins),
                "fats": float(fats), "carbohydrates": float(carbohydrates)}
        print(data)
        all_data.append(data)

def main_actions(category_dish):
    category_dish.click()
    parse_dishes()
    asyncio.run(_bulk_insert(all_data))
    driver.back()
    all_data.clear()


async def _bulk_insert(data_list):
    async with AsyncSession(engine) as session:
        objects = [Breakfast(**item) for item in data_list]
        # await orm_add_breakfast(session, objects)
        session.add_all(objects)
        await session.commit()

#-------------------------------------------Парсинг завтрака----------------------------------------------------

porridge = driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div[5]/div[2]/div[1]/a')
main_actions(porridge)

#-------------------------------------------Парсинг десертов для завтрака----------------------------------------------------
desserts = driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div[5]/div[1]/div[5]/a')
main_actions(desserts)


#-------------------------------------------Парсинг обэда----------------------------------------------------
dinner = driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div[5]/div[2]/div[3]/a')
main_actions(dinner)


#-------------------------------------------Парсинг ужин----------------------------------------------------
supper = driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div[5]/div[1]/div[2]/a')
main_actions(supper)




driver.quit()


