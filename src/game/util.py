import time
from abc import abstractmethod
from typing import Tuple

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.webdriver import WebDriver


class GameUtil:

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 15)

    def click_button(self, locator: Tuple[str, str], name: str = None):
        button = self.wait.until(EC.element_to_be_clickable(locator))
        time.sleep(1)
        button.click()
        if name:
            print(f"Clicked {name} button...")

    def get_text(self, locator: Tuple[str, str]):
        element = self.driver.find_element(locator[0], locator[1])
        return element.text
