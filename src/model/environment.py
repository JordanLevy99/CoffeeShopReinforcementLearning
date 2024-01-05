import os
import pickle
from dataclasses import dataclass
from pathlib import Path

from selenium.common import TimeoutException

from src.game.play import Game
from src.game.types import NUM_DAYS
from src.model.models import CoffeeShopModel


class Environment:

    def step(self, **kwargs):
        """
        What we define as a single 'step' in the learning process, may need to be overriden by subclasses
        :return:
        """
        # self.collect_observations()
        # self.get_actions()
        # status = self.perform_actions()
        # return status
        raise NotImplementedError

    def collect_observations(self):
        raise NotImplementedError

    def get_actions(self):
        raise NotImplementedError

    def perform_actions(self):
        raise NotImplementedError

    def save_data(self):
        """
        A method to save environment action and observation data
        :return:
        """
        raise NotImplementedError


@dataclass(frozen=True)
class ActionNames:
    price = 'price'
    recipe = 'recipe'
    purchases = 'purchases'
    reward = 'reward'


class CoffeeShopGameEnvironment(Environment):

    def __init__(self, game: Game, model: CoffeeShopModel, run_name='default'):
        self.game = game
        self.model = model
        self.model.reward = 0
        self.reward = 0

        self.__action_data = self.__initialize_action_data()
        self.__price = None
        self.__recipe = None
        self.__purchases = None
        self.status = ''
        self.run_name = run_name

        self.__save_data_path = self.__get_save_data_path()
        os.makedirs(self.__save_data_path, exist_ok=True)

    def step(self, day):
        self.game.day = day
        self.collect_observations()
        self.get_actions()
        status = self.perform_actions()
        self.get_reward()
        return status

    def collect_observations(self):
        self.game.load_data()
        if self.game.data_loader.status == 'game over':
            self.game.status = 'game over'
        return self.game.game_data

    def get_actions(self):
        day = self.game.day
        print(f'Current Day: {day}')
        # TODO: simplify once working for RLModel, this should probably only be one function that works with the two models
        self.model.get_model_output(self.game.game_data[day])
        self.__price = self.model.get_price(day)
        self.__recipe = self.model.get_recipe(day)
        self.__purchases = self.model.get_purchases(day)
        print(f'Switching to Price: {self.__price}')
        print(f'Switching to Recipe: {self.__recipe}')
        print(f'Purchasing Items: {self.__purchases}')
        self.__store_actions(day)

    def perform_actions(self):
        day = self.game.day
        # TODO: get this to work and be general enough to work for both Default and RL implementations (and others)
        self.game.adjust_recipe(self.__recipe)
        self.game.buy_items(self.__purchases)
        self.game.set_price(self.__price)
        try:
            self.game.start_day(day)
        except TimeoutException:
            print('You are too broke to start a new day.')
            self.game.status = 'broke'
            self.status = 'broke'
            return 'not enough money'

    def get_reward(self):
        self.reward = self.model.get_reward(self.game)
        return self.reward
        # current_reward = (self.game.day + 1)
        # self.reward += current_reward
        # if self.game.day == 13:
        #     self.reward += self.game.game_data[self.game.day][DataNames.balance]
        # if self.status == 'broke':
        #     self.reward -= 5
        # return self.reward

    def save_data(self, epoch=0):
        epoch_run_name = self.run_name + f'_{epoch}_'
        self.__store_actions(self.game.day)  # we store actions again to store reward in case of an early exit
        self.__save_observation_data(epoch_run_name)
        self.__save_action_data(epoch_run_name)
        self.model.save_model(self.__save_data_path, epoch_run_name)
        print(f'Game data saved at {self.__save_data_path} on day {self.game.day}')

    def __save_observation_data(self, epoch_run_name):
        with open(self.__save_data_path / f'{epoch_run_name}_observations.pkl', 'wb') as f:
            pickle.dump(self.game.game_data, f)

    def __save_action_data(self, epoch_run_name):
        with open(self.__save_data_path / f'{epoch_run_name}_actions.pkl', 'wb') as f:
            pickle.dump(self.__action_data, f)

    def __get_save_data_path(self):
        model_name = type(self.model).__name__
        return Path(f'data/{model_name}/{self.run_name}')

    def __store_actions(self, day):
        self.__action_data[day][ActionNames.price] = self.__price
        self.__action_data[day][ActionNames.recipe] = self.__recipe
        self.__action_data[day][ActionNames.purchases] = self.__purchases
        self.__action_data[day][ActionNames.reward] = self.reward

    @staticmethod
    def __initialize_action_data():
        return {
            day: {
                ActionNames.price: None,
                ActionNames.recipe: None,
                ActionNames.purchases: None,
                'reward': None  # TODO: find landing spot for reward data
            } for day in range(NUM_DAYS)
        }

# class RLModel(CoffeeShopModel):
#     pass


# @dataclass
# class ActionSpace:
#     pass
