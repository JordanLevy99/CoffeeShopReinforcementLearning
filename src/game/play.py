from enum import Enum, auto
from typing import Dict, List
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver

from src.game.locators import InventoryDataLocators, ButtonLocators
from src.game.util import GameUtil


class DataNames(Enum):
    inventory = auto()
    recipe = auto()


class Game(GameUtil):

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.driver = driver
        self.actions = webdriver.ActionChains(self.driver)


        self.game_screen = self.driver.find_element(value="screen-game")

        self.game_data: Dict[str, Dict[str, float]] = {}
        self.__initialize_game_data()

    def load_data(self):
        for name, locator in InventoryDataLocators.map.items():
            value = self.get_text(locator)
            self.game_data[DataNames.inventory.name][name] = float(value)
        print(f'Loaded in the following data: {self.game_data}...')

    def buy_items(self):
        self.__expand_inventory()
        # TODO: make more customizable, this may end up being a class of its own TODO: idea: make it so you can feed
        #  in which option to buy (0, 1, 2) and which item to buy (cups, coffee, sugar, or milk)
        for name, locator_map in ButtonLocators.buy_map.items():
            locator = locator_map[0]  # TODO: parameterize 0 to be either 0, 1, or 2 (a choice of how much to buy)
            self.click_button(locator, name)

    def __expand_inventory(self):
        # TODO: put in check if inventory class is 'expanded'
        locator = InventoryDataLocators.coffee
        expand_inventory_element = self.driver.find_element(locator[0], locator[1])
        self.actions.move_to_element(expand_inventory_element)
        self.actions.perform()

    def __initialize_game_data(self):
        self.game_data[DataNames.inventory.name] = {}
