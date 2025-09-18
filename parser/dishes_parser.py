import logging
from dataclasses import dataclass
from typing import List, Dict

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


    # def initialize(self):
    #     try:
    #         self.driver = self.selenium_manager.create_driver()
    #         logger.info(f"Парсер блюд инициализирован")
    #     except Exception as e:
    #         logger.info(f"Ошибка инициализации парсера: {e}")
    #         raise


    def parse_dishes(self, dishes_links: Dict[str, str]) -> List[DishesInfo]:
        self.dishes_links = dishes_links





