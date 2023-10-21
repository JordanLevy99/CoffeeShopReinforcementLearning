from dataclasses import dataclass
from typing import List, Tuple

from src.game.play import _DataLoader, Game
from src.game.types import NUM_DAYS


class Environment:

    def collect_observations(self):
        raise NotImplementedError

    def perform_actions(self):
        raise NotImplementedError


class CoffeeShopGameEnvironment(Environment):

    def __init__(self, data_loader: _DataLoader, game: Game):
        self.data_loader = data_loader
        self.game = game

    def collect_observations(self):
        self.data_loader.load_data(self.game.day)

    def perform_actions(self):
        # TODO: get this to work and be general enough to work for both Default and RL implementations (and others)
        # game.adjust_recipe(recipe)
        # game.buy_items(purchases)
        # game.set_price(price)
        pass


class CoffeeShopModel:

    def get_recipe(self):
        raise NotImplementedError

    def get_buy_items(self):
        raise NotImplementedError

    def get_price(self):
        raise NotImplementedError


class BaselineModel(CoffeeShopModel):
    # TODO: get this interface working, with the idea being we have a RLModel that will take its place

    default_recipes: List[List[Tuple[str, int]]] = [[('coffee', 2), ('milk', 1.3), ('sugar', 2.5)] if day == 0 else
                                                    [('coffee', 3), ('milk', 1.3), ('sugar', 2.8)] for day in
                                                    range(NUM_DAYS)]

    default_purchases: List[List[Tuple[str, int]]] = [
        [('cups', 1), ('coffee', 1), ('milk', 2), ('sugar', 2)] if day == 0 else
        [('cups', 1), ('coffee', 2), ('milk', 2), ('sugar', 2), ('sugar', 2),
         ('coffee', 2)]
        for day in range(NUM_DAYS)]

    default_price_bump: List[float] = [0 if day == 0 else 0.10 for day in range(NUM_DAYS)]


    def get_recipe(self):
        return

# @dataclass
# class ActionSpace:
#     pass