import time
from enum import Enum, auto
from typing import Dict, List, Tuple
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from src.game.locators import InventoryDataLocators, ButtonLocators, RecipeDataLocators
from src.game.util import GameUtil


class DataNames(Enum):
    inventory = auto()
    recipe = auto()


class Game(GameUtil):

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.driver = driver
        self.game_screen = self.driver.find_element(value="screen-game")

        self.game_data: Dict[str, Dict[str, float]] = {}
        self.__initialize_game_data()
        self.__initialize_scale()


    def load_data(self):
        # TODO: expand to include weather info, other metadata (reputation, etc.)
        for name, locator in InventoryDataLocators.map.items():
            value = self.get_text(locator)
            self.game_data[DataNames.inventory.name][name] = float(value)
        print(f'Loaded in the following data: {self.game_data}...')

    def buy_items(self, purchases: List[Tuple[str, int]]):
        self.__expand_inventory()
        # TODO: make more customizable, this may end up being a class of its own TODO: idea: make it so you can feed
        #  in which option to buy (0, 1, 2) and which item to buy (cups, coffee, sugar, or milk)
        for name, amount in purchases:
            locator = ButtonLocators.buy_map[name][amount]
            self.__try_buying_item(amount, locator, name)

    def __try_buying_item(self, amount, locator, name):
        try:
            self.click_button(locator, name, 2)
        except TimeoutException:
            print(f'Not enough money to purchase option {amount} of {name}')
            if amount > 0:
                amount -= 1
                print(f'Trying again with option {amount}')
                self.__try_buying_item(amount, locator, name)

    def adjust_recipe(self, recipe: List[Tuple[str, float]]):
        self.__expand_recipe()
        # TODO: cleanup, add drag_button function to GameUtil, with scale and everything
        ## 0 to 213 pixel scale I think

        range_map = {'coffee': (1, 4), 'milk': (0, 2), 'sugar': (0, 4)}
        for name, amount in recipe:
            locator = ButtonLocators.recipe_map[name]
            min_max = range_map[name]
            self.adjust_slider(amount, locator, min_max)

    def set_price(self, price: float):
        price_min_max = (0.05, 10)
        self.adjust_slider(price, ButtonLocators.price, price_min_max)

    def start_day(self):
        self.click_button(ButtonLocators.start_day, 'start day')
        locator = InventoryDataLocators.time
        time_str = self.driver.find_element(locator[0], locator[1]).text
        while time_str != '07:00 PM':
            time.sleep(1)
            time_str = self.driver.find_element(locator[0], locator[1]).text
        self.click_button(ButtonLocators.continue_button, 'continue')
        try:
            self.click_button(ButtonLocators.return_to_game, 'return to game', 10)
        except TimeoutException:
            pass

    def __expand_inventory(self):
        # TODO: put in check if inventory class is 'expanded'
        locator = InventoryDataLocators.coffee
        expand_inventory_element = self.driver.find_element(locator[0], locator[1])
        self.actions.move_to_element(expand_inventory_element)
        self.actions.perform()
        print('Expanding inventory menu...')

    def __expand_recipe(self):
        # TODO: put in check if inventory class is 'expanded'
        locator = InventoryDataLocators.coffee
        expand_inventory_element = self.driver.find_element(locator[0], locator[1])
        self.actions.move_to_element(expand_inventory_element)
        locator = RecipeDataLocators.coffee
        expand_recipe_element = self.driver.find_element(locator[0], locator[1])
        self.actions.move_to_element(expand_recipe_element)
        self.actions.perform()
        print('Expanding recipe menu...')
        time.sleep(3)

    def __initialize_game_data(self):
        self.game_data[DataNames.inventory.name] = {}

    def __initialize_scale(self):
        game = self.driver.find_element(By.XPATH, '//*[@id="game"]')
        style = game.get_attribute('style')
        self.scale = float(style.split('(')[-1].strip(');'))
        print(f'Scale initialized as {self.scale}...')
