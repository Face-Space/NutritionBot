import logging
from typing import Optional

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger(__name__)

class SeleniumManager:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None

    def create_driver(self) -> webdriver.Chrome:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
