import time

from selenium.webdriver.support import expected_conditions as EC

from src.game.play import Game
from src.game.setup import GameSetup
from src.game.locators import InventoryDataLocators


def setup_game():
    start_time = time.time()

    game_setup = GameSetup()
    game_setup.setup()

    print(f"Took {(time.time() - start_time)} seconds to setup game, now reading info and creating Game object")

    game = Game(game_setup.driver)
    game.load_data()
    price = 2
    for day in range(14):
        if day == 0:
            purchases = [('cups', 1), ('coffee', 1), ('milk', 2), ('sugar', 2)]
            recipe = [('coffee', 2), ('milk', 1.3), ('sugar', 2.5)]
            game.adjust_recipe(recipe)
            price = 2.50
        else:
            purchases = [('cups', 1), ('coffee', 2), ('milk', 2), ('sugar', 2), ('sugar', 2), ('coffee', 2)]
            recipe = [('coffee', 3), ('milk', 1.3), ('sugar', 2.8)]
            game.adjust_recipe(recipe)
            price += 0.10
        game.buy_items(purchases)
        game.set_price(price)
        game.load_data()  # TODO: expand data that is loaded in each data, store between days
        game.start_day()
    pass
