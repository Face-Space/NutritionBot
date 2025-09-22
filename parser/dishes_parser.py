import logging
from dataclasses import dataclass
from typing import List, Dict

from selenium.webdriver.common.by import By

from utils.selenium_manager import SeleniumManager

logger = logging.getLogger(__name__)

@dataclass
class DishesInfo:
    dish_name: str = ""
    calories: int = ""
    proteins: int = ""
    fats: int = ""
    carbs: int = ""
    error: str = ""


class DishesParser:
    def __init__(self, user_id: str = None):
        self.user_id = user_id
        self.selenium_manager = SeleniumManager()
        self.results = List[DishesInfo]


    def initialize(self):
        try:
            self.driver = self.selenium_manager.create_driver()
            logger.info(f"Парсер блюд инициализирован")
        except Exception as e:
            logger.info(f"Ошибка инициализации парсера: {e}")
            raise


    def parse_dishes(self, url: str):
        try:
            self.selenium_manager.navigate_to_url(url)
            self._get_breakfast()

            return self._get_breakfast()
        except Exception as e:
            print(f"Ошибка {e}")


    def _get_breakfast(self):
        porridge =self.driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div[5]/div[2]/div[1]/a')
        porridge.click()
        name = self.driver.find_element(By.XPATH, '//*[@id="mzr-grid-content"]/div/div[2]/div/div/table/tbody/tr[1]/td[1]/a').text
        print(name, "!!!!!!!!!!!!!!!!!!!!!!!!!!")

        return name

    def close(self):
        if self.selenium_manager:
            self.selenium_manager.close()







