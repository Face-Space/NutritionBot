import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
driver.implicitly_wait(20)

# driver.execute_script("window.scrollBy(0, 500);")
porridge = driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div[5]/div[2]/div[1]/a')
porridge.click()
porridge_table = (
    driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div/table/tbody').find_elements(
        By.TAG_NAME, "tr"))


for i in range(len(porridge_table)):
    # Повторно ищем элементы каждый раз, чтобы получить свежие элементы, т.к. после driver.back() и паузы элементы в
    # переменной porridge_table устаревают, и при следующей итерации обращение к element.text вызывает
    # StaleElementReferenceException
    porridge_table = (driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div/table/tbody').find_elements(By.TAG_NAME, "tr"))
    element = porridge_table[i]
    product_name = element.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div/table/tbody/tr[1]/td[1]/a').text
    calories = driver.find_elements(By.CLASS_NAME, 'uk-text-right')[0].text.replace("кКал", "").strip()


    element.click()
    description = driver.find_element(By.CLASS_NAME, "mzr-recipe-view-description-tc").text
    driver.back()
    data = {"name_dish": product_name, "calories": calories}
    print(data)

    time.sleep(random.randint(1, 3))


driver.quit()


