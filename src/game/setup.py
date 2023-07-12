from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from src.game.locators import ButtonLocators
from src.game.util import GameUtil


# @dataclass(frozen=True)
# class SetupButtonLocators:
#     play_button_locator = (By.XPATH, "/html/body/div[2]/section[1]/ul/li[1]/button")
#     skip_tutorial_button_locator = (By.XPATH, "/html/body/div[2]/section[5]/div/p/button[1]")
#     next_button_locator = (By.XPATH, "/html/body/div[2]/section[5]/div/p/button[3]")


class GameSetup(GameUtil):

    def __init__(self):
        self.driver = webdriver.Firefox()
        super().__init__(self.driver)

    def setup(self):
        self.__load_game()
        self.__click_buttons()

    def __load_game(self):
        self.driver.install_addon('ublock_origin-1.50.0.xpi', temporary=True)
        self.driver.get("https://www.coolmathgames.com/0-coffee-shop")
        self.__switch_to_game_frame()

    def __switch_to_game_frame(self):
        game_locator = (By.ID, "html5game")
        self.wait.until(EC.frame_to_be_available_and_switch_to_it(game_locator))

    def __click_buttons(self):
        self.click_button(ButtonLocators.play, "play")
        self.click_button(ButtonLocators.skip_tutorial, "skip tutorial")
        self.click_button(ButtonLocators.next, "next")
