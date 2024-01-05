import re
import time
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Tuple, Union
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from src.game.locators import InventoryDataLocators, ButtonLocators, RecipeDataLocators, MetadataLocators
from src.game.types import NUM_DAYS
from src.game.util import GameUtil


@dataclass(frozen=True)
class DataNames:
    inventory = 'inventory'
    recipe = 'recipe'
    price = 'price'
    weather = 'weather'
    reputation = 'reputation'
    balance = 'balance'

    columns = ['inventory', 'recipe', 'price', 'weather', 'reputation', 'balance']


class Game(GameUtil):

    def __init__(self, driver: WebDriver):
        super().__init__(driver)
        self.driver = driver
        self.game_screen = self.driver.find_element(value="screen-game")

        self.game_data: Dict[str, Dict[int, Dict[str, Union[float, str, int]]]] = {}
        self.data_loader = _DataLoader(self.driver)

        # self.__initialize_game_data()
        self.day = 0
        self.status = None
        self.__initialize_scale()

    def load_data(self):
        self.__expand_recipe()
        self.game_data = self.data_loader.load_data(self.day)
        # TODO: expand to include weather info, other metadata (reputation, etc.)
        print(f'Loaded in the following data: {self.game_data}...')

    def buy_items(self, purchases: List[Tuple[str, int]]):
        self.__expand_inventory()
        # TODO: make more customizable, this may end up being a class of its own TODO: idea: make it so you can feed
        #  in which option to buy (0, 1, 2) and which item to buy (cups, coffee, sugar, or milk)
        for item, option in purchases:
            locator = ButtonLocators.buy_map[item][option]
            self.__try_buying_item(option, locator, item)

    def __try_buying_item(self, option, locator, name):
        try:
            self.click_button(locator, name, 2)
        except TimeoutException:
            print(f'Not enough money to purchase option {option} of {name}')
            if option > 0:
                option -= 1
                print(f'Trying again with option {option}')
                new_locator = ButtonLocators.buy_map[name][option]
                self.__try_buying_item(option, new_locator, name)

    def adjust_recipe(self, recipe: List[Tuple[str, float]]):
        self.__expand_recipe()
        # TODO: cleanup, add drag_button function to GameUtil, with scale and everything
        ## 0 to 213 pixel scale I think

        range_map = {'coffee': (1, 4), 'milk': (0, 2), 'sugar': (0, 4)}
        for name, amount in recipe:
            locator = ButtonLocators.recipe_map[name]
            min_max = range_map[name]
            self.adjust_slider(amount, locator, min_max, self.scale)

    def set_price(self, price: float):
        price_min_max = (0.05, 10)
        # TODO: make code cleaner here, extract find element to a function???
        elem = self.driver.find_element(By.CSS_SELECTOR, 'p[data-state="price"]')
        additional_scale = float(elem.get_attribute('data-scale'))
        scale = self.scale * additional_scale
        self.adjust_slider(price, ButtonLocators.price, price_min_max, scale)

    def start_day(self, day):
        self.day = day
        self.click_button(ButtonLocators.start_day, 'start day')
        time_locator = InventoryDataLocators.time
        time_str = self.get_text(time_locator)
        while time_str != '07:00 PM':
            time.sleep(1)
            time_str = self.get_text(time_locator)
            self.__try_to_skip_to_end_of_day()

        self.click_button(ButtonLocators.continue_button, 'continue')
        self.__handle_ad_screen()

    def __handle_ad_screen(self):
        try:
            self.click_button(ButtonLocators.return_to_game, 'return to game', 5)
        except TimeoutException:
            pass

    def __try_to_skip_to_end_of_day(self):
        try:
            self.click_button(ButtonLocators.skip_day, 'skip day', 1)
        except TimeoutException:
            pass

    def __expand_inventory(self):
        # TODO: put in check if inventory class is 'expanded'
        inventory_locator = InventoryDataLocators.coffee
        self.status = self.move_to_element(self.actions, inventory_locator, 'inventory', timeout=3)
        # expand_inventory_element = self.driver.find_element(locator[0], locator[1])
        # self.actions.move_to_element(expand_inventory_element)
        self.actions.perform()
        # print('Expanding inventory menu...')

    def __expand_recipe(self):
        # TODO: put in check if inventory class is 'expanded'
        self.__expand_inventory()
        # inventory_locator = InventoryDataLocators.coffee
        # self.move_to_element(self.actions, locator, timeout=3)
        # expand_inventory_element = self.driver.find_element(locator[0], locator[1])
        # self.actions.move_to_element(expand_inventory_element)
        recipe_locator = RecipeDataLocators.coffee
        self.status = self.move_to_element(self.actions, recipe_locator, 'recipe', timeout=3)
        # expand_recipe_element = self.driver.find_element(locator[0], locator[1])
        # self.actions.move_to_element(expand_recipe_element)
        # self.actions.perform()
        # print('Expanding recipe menu...')
        time.sleep(2)

    def __initialize_game_data(self):
        self.game_data[DataNames.inventory.name] = {}

    def __initialize_scale(self):
        game = self.driver.find_element(By.XPATH, '//*[@id="game"]')
        style = game.get_attribute('style')
        self.scale = float(style.split('(')[-1].strip(');'))
        print(f'Scale initialized as {self.scale}...')


class _DataLoader(GameUtil):
    """
    Loads all relevant metadata (inventory, weather, reputation, cash)
    """

    REPUTATION_RE = re.compile(r'\d*(\.{0,1})\d+px')

    def __init__(self, driver: WebDriver, day=1):
        self.driver = driver
        self.status = ''
        super().__init__(driver)
        self.__initialize_game_data()

    def load_data(self, day):

        self.__load_inventory_data(day)
        self.__load_recipe_data(day)
        self.__load_weather_data(day)
        self.__load_reputation_data(day)
        self.load_balance_data(day)
        self.__load_price_data(day)
        # self.__load_day()
        return self.game_data

    def __initialize_game_data(self):
        self.game_data = {
            day: {
                name: {}
                for name in DataNames.columns
            }
            for day in range(NUM_DAYS)
        }

    # TODO: refactor the below three functions (and any other load functions) into a unified class structure
    def __load_inventory_data(self, day):
        for name, locator in InventoryDataLocators.map.items():
            value = self.get_text(locator)
            self.game_data[day][DataNames.inventory][name] = float(value)

    def __load_recipe_data(self, day):
        for name, locator in ButtonLocators.recipe_map.items():
            value = self.get_text(locator)
            self.game_data[day][DataNames.recipe][name] = float(value)

    def __load_weather_data(self, day):
        for name, locator in MetadataLocators.weather_map.items():
            value = self.get_text(locator)
            try:
                self.game_data[day][DataNames.weather][name] = int(value.strip('°'))
            except ValueError:
                self.game_data[day][DataNames.weather][name] = value

    def __load_reputation_data(self, day):
        reputation_map = {
            'good': 1,
            'bad': -1
        }

        reputation_finder = MetadataLocators.reputation
        reputation_element = self.driver.find_element(by=reputation_finder[0], value=reputation_finder[1])

        reputation_multiplier = reputation_map[reputation_element.get_attribute('class')]
        absolute_reputation = float(re.search(self.REPUTATION_RE, reputation_element.get_attribute('style')).group(0)
                                    .strip('px'))
        reputation = absolute_reputation * reputation_multiplier
        self.game_data[day][DataNames.reputation] = reputation

    def load_balance_data(self, day, errors=0):
        balance = self.get_text(MetadataLocators.balance)
        if not balance:
            self.status = 'game over'
            return

        self.game_data[day][DataNames.balance] = float(balance)

    def __load_price_data(self, day):
        price = self.get_text(ButtonLocators.price)
        self.game_data[day][DataNames.price] = float(price.strip('$'))

