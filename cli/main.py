import os
import pickle
import time
from pathlib import Path
from typing import List, Tuple

from selenium.webdriver.support import expected_conditions as EC

from src.game.play import Game
from src.game.setup import GameSetup
from src.game.locators import InventoryDataLocators
from src.game.types import NUM_DAYS
from src.model.environment import CoffeeShopGameEnvironment, Environment
from src.model.models import BaselineModel, RLModel


# default_recipes: List[List[Tuple[str, int]]] = [[('coffee', 2), ('milk', 1.3), ('sugar', 2.5)] if day == 0 else
#                                                 [('coffee', 3), ('milk', 1.3), ('sugar', 2.8)] for day in range(NUM_DAYS)]
#
# default_purchases: List[List[Tuple[str, int]]] = [
#     [('cups', 1), ('coffee', 1), ('milk', 2), ('sugar', 2)] if day == 0 else
#     [('cups', 1), ('coffee', 2), ('milk', 2), ('sugar', 2), ('sugar', 2),
#      ('coffee', 2)]
#     for day in range(NUM_DAYS)]
#
# default_price_bump: List[float] = [0 if day == 0 else 0.10 for day in range(NUM_DAYS)]


def run(args):
    start_time = time.time()
    model = _initialize_model(args)  # Initialize model before starting main loop so the model persists between epochs
    for epoch in range(args.epoch):
        game = _setup_game(args, epoch, start_time)
        if not args.learn:  # in 'data collection' mode (no learning/retention over epochs by the model)
            model = _initialize_model(args)
        environment = CoffeeShopGameEnvironment(game, model, args.run_name)
        # TODO: get day to range from 1 to 14 (to make data more interpretable) - maybe
        try:
            for day in range(NUM_DAYS):
                environment.step(day)
                environment.save_data(epoch)
                if environment.game.status:
                    print('Epoch is over')
                    break
        except Exception as e:
            print(f'Error occurred somewhere, here is the message:\n\t{e}')
            print(f'Saving data now...')
            environment.get_reward()
            environment.save_data(args.run_name)
        finally:
            game.driver.quit()


def _setup_game(args, epoch, start_time):
    print(f'\n\nStarting Epoch {epoch + 1} out of {args.epoch}...')
    game_setup = GameSetup()
    game_setup.setup()
    print(f"Took {(time.time() - start_time)} seconds to setup game, now reading info and creating Game object")
    game = Game(game_setup.driver)
    game.load_data()
    return game


def _get_epoch_run_name(args, epoch):
    epoch_run_name = args.run_name
    if args.epoch > 1:
        epoch_run_name += f'_{epoch}_'
    return epoch_run_name


def _initialize_model(args):
    if args.baseline:
        model = BaselineModel()
    else:
        # model = BaselineModel()
        model = RLModel()  # TODO: replace above line with this line
    return model

# def _save_data(environment:     CoffeeShopGameEnvironment, run_name='default'):
#     print(os.getcwd())
#     model_name = type(environment.model).__name__
#     data_path = Path(f'data/{model_name}')
#     os.makedirs(data_path, exist_ok=True)
#     with open(data_path / f'{run_name}_observations.pkl', 'wb') as f:
#         pickle.dump(environment.game.game_data, f)
#
#     environment.save_data(run_name)
