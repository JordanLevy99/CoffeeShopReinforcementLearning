import time
from abc import abstractmethod
from typing import Tuple

from selenium.common import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.webdriver import WebDriver


class GameUtil:

    def __init__(self, driver: WebDriver, timeout=15):
        self.driver = driver
        self.actions = webdriver.ActionChains(self.driver)
        self.wait = self.__set_wait(timeout)
        self.__timeout = timeout

        self.pixel_range = (0, 213)
        self.pixel_min, self.pixel_max = self.pixel_range

    def click_button(self, locator: Tuple[str, str], name: str = None, timeout=None):
        if timeout:
            self.wait = self.__set_wait(timeout)
        else:
            self.wait = self.__set_wait(self.__timeout)
        button = self.wait.until(EC.element_to_be_clickable(locator))
        errors = 0
        self.__try_click_button(button, errors)
        if name:
            print(f"Clicked {name} button...")

    def get_text(self, locator: Tuple[str, str]):
        element = self.driver.find_element(locator[0], locator[1])
        return element.text

    def adjust_slider(self, value, locator, min_max):
        min_val, max_val = min_max
        button = self.driver.find_element(locator[0], locator[1])
        current_x_value = float(button.get_attribute('style').split()[-1][:-3])
        x_converted_value = lambda x: ((x - min_val) / (max_val - min_val)) * (self.pixel_max - self.pixel_min)
        x_value = x_converted_value(value)
        offset = (x_value - current_x_value) * self.scale
        self.actions.drag_and_drop_by_offset(button, xoffset=offset, yoffset=0)
        self.actions.perform()

    def __set_wait(self, timeout):
        return WebDriverWait(self.driver, timeout)

    def __try_click_button(self, button, errors):
        try:
            button.click()
        except ElementClickInterceptedException as e:
            errors += 1
            if errors > 3:
                raise ElementClickInterceptedException
            time.sleep(1)
            print(f'Trying to click again (errors={errors})...')
            self.__try_click_button(button, errors)
