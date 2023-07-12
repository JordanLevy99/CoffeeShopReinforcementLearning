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

    for day in range(15):
        if day == 0:
            purchases = [('cups', 1), ('coffee', 1), ('milk', 2), ('sugar', 2)]
            recipe = [('coffee', 2), ('milk', 1.3), ('sugar', 2.5)]
            game.adjust_recipe(recipe)
        else:
            purchases = [('cups', 1), ('coffee', 2), ('milk', 2), ('sugar', 2), ('sugar', 2)]
            recipe = [('coffee', 3), ('milk', 1.3), ('sugar', 2.8)]
            game.adjust_recipe(recipe)
        game.buy_items(purchases)
        # TODO: add adjust price

        # TODO: add skip ad (return to game button)
        game.load_data()
        game.start_day()
    pass
