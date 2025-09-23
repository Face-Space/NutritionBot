import random
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

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


soup = BeautifulSoup(driver.page_source, "lxml")
driver.implicitly_wait(20)


porridge = driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div[5]/div[2]/div[1]/a')
porridge.click()
porridge_table = (
    driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div/table/tbody').find_elements(
        By.TAG_NAME, "tr"))


for i in porridge_table:

    tr_tag = i.find_element(By.TAG_NAME, "a")
    href = tr_tag.get_attribute("href")

    dish_name = tr_tag.text
    calories = i.find_elements(By.CLASS_NAME, "uk-text-right")[0].text.replace("кКал", "").strip()

    driver.execute_script("window.open(arguments[0], '_blank')", href)
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)

    description = driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div[2]/div/p').text
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    data = {"name_dish": dish_name, "description": description, "calories": float(calories)}
    print(data)

driver.quit()


