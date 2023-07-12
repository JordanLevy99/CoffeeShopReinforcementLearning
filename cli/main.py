import time

from selenium.webdriver.support import expected_conditions as EC

from src.game.play import Game
from src.game.setup import GameSetup
from src.game.locators import InventoryDataLocators


def setup_game():
    start_time = time.time()

    game_setup = GameSetup()
    game_setup.setup()

    print(f"Took {time.time() - start_time} seconds to setup game, now reading info and creating Game object")

    game = Game(game_setup.driver)
    game.load_data()
    game.buy_items()
    game.load_data()
    pass
