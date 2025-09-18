import logging
import time
from typing import Optional

from selenium import webdriver
from selenium.common import WebDriverException, TimeoutException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium_stealth import stealth

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
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")

        if self.headless:
            chrome_options.add_argument("--headless")

        chrome_options.add_argument("--window-size=1920,1080")

        try:
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

            driver.implicitly_wait(20)
            driver.set_page_load_timeout(60)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            self.driver = driver
            self.wait = WebDriverWait(driver, 20)
            logger.info("Chrome драйвер создан успешно")
            return driver

        except WebDriverException as e:
            logger.error(f"Ошибка создания Chrome драйвера: {e}")


    def navigate_to_url(self, url: str):
        if not self.driver:
            logger.error("Драйвер не инициализирован")
            return False

        try:
            logger.debug(f"Переход по URL: {url}")
            self.driver.get(url)
            self._wait_for_antibot_bypass()

            return True

        except TimeoutException:
            logger.error(f"Таймаут при загрузке: {url}")
            return False

        except WebDriverException as e:
            logger.error(f"Ошибка WebDriver: {e}")
            return False


    def _wait_for_antibot_bypass(self, max_wait_time: int = 240):  # ⬅️ 120 → 240
        start_time = time.time()
        reload_attempts = 0
        max_reload_attempts = 3

        while time.time() - start_time < max_wait_time:
            try:
                if self._is_blocked():
                    if reload_attempts < max_reload_attempts:
                        logger.info(
                            f"Обнаружена блокировка, перезагрузка страницы"
                            f"(попытка {reload_attempts + 1}/{max_reload_attempts})"
                        )
                        self.driver.refresh()
                        reload_attempts += 1
                        time.sleep(15)
                        continue
                    else:
                        logger.warning("Превышено количество попыток, возвращаем новый драйвер")
                        raise Exception("Access blocked after retries")
                else:
                    logger.info("Антибот защита пройдена")
                    return

            except Exception as e:
                if "Access blocked" in str(e):
                    raise
                time.sleep(15)
                continue

        logger.warning(f"Антибот защита не пройдена за {max_wait_time} секунд")
        raise Exception("AntibotTimeout")


    def _is_blocked(self) -> bool:
        if not self.driver:
            return True

        try:
            blocked_indicators = [
                "cloudflare", "checking your browser", "enable javascript",
                "access denied", "blocked", "ddos-guard", "проверка браузера",
                "доступ ограничен", "access restricted"
            ]

            page_source = self.driver.page_source.lower()

            for indicator in blocked_indicators:
                if indicator in page_source:
                    return True
            return False

        except Exception:
            return True


    def close(self):
        if self.driver:
            try:
                self.driver.quit()
                logger.debug("Драйвер закрыт успешно")

            except Exception as e:
                logger.error(f"Ошибка закрытия драйвера: {e}")

            finally:
                self.driver = None
                self.wait = None





