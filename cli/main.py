import time
from typing import List, Tuple

from selenium.webdriver.support import expected_conditions as EC

from src.game.play import Game
from src.game.setup import GameSetup
from src.game.locators import InventoryDataLocators
from src.game.types import NUM_DAYS

default_recipes: List[List[Tuple[str, int]]] = [[('coffee', 2), ('milk', 1.3), ('sugar', 2.5)] if day == 0 else
                                                [('coffee', 3), ('milk', 1.3), ('sugar', 2.8)] for day in range(NUM_DAYS)]

default_purchases: List[List[Tuple[str, int]]] = [
    [('cups', 1), ('coffee', 1), ('milk', 2), ('sugar', 2)] if day == 0 else
    [('cups', 1), ('coffee', 2), ('milk', 2), ('sugar', 2), ('sugar', 2),
     ('coffee', 2)]
    for day in range(NUM_DAYS)]

default_price_bump: List[float] = [0 if day == 0 else 0.10 for day in range(NUM_DAYS)]


def setup_game():
    start_time = time.time()

    game_setup = GameSetup()
    game_setup.setup()

    print(f"Took {(time.time() - start_time)} seconds to setup game, now reading info and creating Game object")

    game = Game(game_setup.driver)
    game.load_data()
    price = 2.25
    # TODO: get day to range from 1 to 14 (to make data more interpretable)
    for day in range(NUM_DAYS):
        purchases = default_purchases[day]
        recipe = default_recipes[day]
        price += default_price_bump[day]

        game.adjust_recipe(recipe)
        game.buy_items(purchases)
        game.set_price(price)
        game.load_data()  # TODO: expand data that is loaded in each data, store between days
        game.start_day(day)
    pass
