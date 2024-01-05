import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd
import torch
from torch import nn

from src.game.play import DataNames, Game
from src.game.types import NUM_DAYS


class CoffeeShopModel:
    # TODO: implement load model (involving torch load state dict from path)
    def __init__(self):
        self.reward = 0

    def get_model_output(self, observation_data):
        raise NotImplementedError

    def load_observations(self, observation_data):
        raise NotImplementedError

    def get_recipe(self, day: int):
        raise NotImplementedError

    def get_purchases(self, day: int):
        raise NotImplementedError

    def get_price(self, day: int):
        raise NotImplementedError

    def get_reward(self, game: Game):
        print(f'Current Day is {game.day} (starting to collect reward)')
        current_reward = game.day
        self.reward += current_reward
        self.reward += self.__get_balance_reward(game)
        if game.status == 'broke':
            self.reward -= 5
        print(f'Day {game.day} total reward: {self.reward}')
        return self.reward

    def __get_balance_reward(self, game):
        if game.day != (NUM_DAYS - 1):
            game.data_loader.load_balance_data(game.day + 1)
            start_of_day_balance = game.game_data[game.day][DataNames.balance]
            if game.data_loader.status == 'game over':
                print('You lost')
                return 0 - start_of_day_balance
            end_of_day_balance = game.game_data[game.day + 1][DataNames.balance]
            print(f'\tStart of day balance: {start_of_day_balance}')
            print(f'\tEnd of day balance: {end_of_day_balance}')
            balance_reward = end_of_day_balance - start_of_day_balance
        else:
            balance_reward = game.game_data[game.day][DataNames.balance]
        return balance_reward

    def save_model(self, data_path: Path, epoch_run_name: str):
        raise NotImplementedError


class BaselineModel(CoffeeShopModel):
    # TODO: get this interface working, with the idea being we have a RLModel that will take its place

    INITIAL_PRICE = 3.30

    default_recipes: List[List[Tuple[str, int]]] = [[('coffee', 2), ('milk', 1.3), ('sugar', 2.5)] if day == 0 else
                                                    [('coffee', 3), ('milk', 1.3), ('sugar', 2.8)] for day in
                                                    range(NUM_DAYS)]

    default_purchases: List[List[Tuple[str, int]]] = [
        [('cups', 1), ('coffee', 1), ('milk', 2), ('sugar', 2)] if day == 0 else
        [('cups', 1), ('coffee', 2), ('milk', 2), ('sugar', 2), ('sugar', 2),
         ('coffee', 2)]
        for day in range(NUM_DAYS)]

    def __init__(self):
        super().__init__()
        self.default_prices: List[float] = [self.INITIAL_PRICE + 0.10 * day for day in range(NUM_DAYS)]

    def get_model_output(self, observation_data):
        # Observation data does not affect the baseline model
        pass

    def load_observations(self, observation_data):
        # Observation data does not affect the baseline model
        pass

    def get_recipe(self, day: int):
        return self.default_recipes[day]

    def get_purchases(self, day: int):
        return self.default_purchases[day]

    def get_price(self, day: int):
        return self.default_prices[day]

    def save_model(self, data_path: Path, epoch_run_name: str):
        # No 'model' to save
        pass


class Policy:

    def __init__(self, state_size, action_size):
        pass


class MLPPolicy(nn.Module, Policy):
    def __init__(self, state_size, action_size):
        super(MLPPolicy, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, action_size)

    def forward(self, state):
        x = self.fc1(state)
        x = torch.relu(x)
        x = self.fc2(x)
        x = torch.sigmoid(x)
        return x


@dataclass
class ObservationData:
    num_cups: int
    num_coffee: int
    num_milk: int
    num_sugar: int
    recipe_coffee: float
    recipe_milk: float
    recipe_sugar: float
    temperature: int
    temperature_description: List[int]  # 4-dimensional vector
    reputation: float
    balance: float

    STATE_SIZE = 15


@dataclass
class ActionData:
    recipe_coffee: float
    recipe_milk: float
    recipe_sugar: float
    price: float
    # Num times is capped from [0, 5]
    # Buy options are probabilistic, >0.5 equals yes
    buy_cups_option_1: int
    buy_cups_option_1_num_times: int
    buy_cups_option_2: int
    buy_cups_option_2_num_times: int
    buy_cups_option_3: int
    buy_cups_option_3_num_times: int

    buy_coffee_option_1: int
    buy_coffee_option_1_num_times: int
    buy_coffee_option_2: int
    buy_coffee_option_2_num_times: int
    buy_coffee_option_3: int
    buy_coffee_option_3_num_times: int

    buy_milk_option_1: int
    buy_milk_option_1_num_times: int
    buy_milk_option_2: int
    buy_milk_option_2_num_times: int
    buy_milk_option_3: int
    buy_milk_option_3_num_times: int

    buy_sugar_option_1: int
    buy_sugar_option_1_num_times: int
    buy_sugar_option_2: int
    buy_sugar_option_2_num_times: int
    buy_sugar_option_3: int
    buy_sugar_option_3_num_times: int

    STATE_SIZE = 28


class RLModel(CoffeeShopModel):

    temperature_description_df = pd.get_dummies(pd.Series(['freezing', 'cold', 'cool', 'warm']))
    action_names_map = {
        field.name: idx for idx, field in enumerate(dataclasses.fields(ActionData))
    }
    MAX_PURCHASE_AMOUNT = 1

    def __init__(self,
                 policy=MLPPolicy,
                 state_size=ObservationData.STATE_SIZE,
                 action_size=ActionData.STATE_SIZE):
        super().__init__()
        self.policy = policy(state_size, action_size)
        self.state_size = state_size
        self.action_size = action_size
        self.__output = None
        self.__output_array = None
        self.__optimizer = torch.optim.Adam(self.policy.parameters())


    def load_observations(self, observation_data):
        input_vector = []
        input_vector.extend(observation_data[DataNames.inventory].values())
        input_vector.extend(observation_data[DataNames.recipe].values())
        input_vector.append(observation_data[DataNames.price])
        input_vector = self.__get_weather_data(observation_data, input_vector)
        input_vector.append(observation_data[DataNames.reputation])
        input_vector.append(observation_data[DataNames.balance])
        return torch.Tensor(input_vector)

    def get_model_output(self, observation_data):
        self.__output = self.policy(self.load_observations(observation_data))
        self.__output_array = self.__output.clone().detach().numpy()

    def get_recipe(self, day: int):
        recipe_limits = np.array([4, 2, 4])
        return list(tuple(zip(['coffee', 'milk', 'sugar'], recipe_limits * self.__output_array[:3])))

    def get_purchases(self, day: int):
        # 24 outputs to handle!
        purchase_decoder = _PurchaseDecoder(self.action_names_map, self.__output_array, self.MAX_PURCHASE_AMOUNT)
        purchases = purchase_decoder.decode_purchases()
        return purchases

    def get_price(self, day: int):
        """
            Converts output from (0, 1) range to (0.05, 10) range
        """
        price_idx = self.action_names_map['price']
        model_output_price = self.__output_array[price_idx]

        price_min, price_max = (0.05, 10)
        data_min, data_max = (0, 1)

        price_range = 9.95
        data_range = 1

        converted_price = (((model_output_price - data_min) * price_range) / data_range) + price_min
        return converted_price

    def save_model(self, data_path: Path, epoch_run_name: str):
        file_path = data_path / f'{epoch_run_name}_model.pth'
        torch.save(self.policy.state_dict(), file_path)

    # TODO: go back to drawing board on actually training the model, look more into Q-learning or PPO, environment needs to be differentiable wrt to the weights, or at least estimated somehow
    # TODO: for now collect data w/ classic ML purposes in mind
    # def train_model(self, reward):
    #     loss =

    def __get_weather_data(self, observation_data, input_vector: List) -> List:
        input_vector.append(observation_data[DataNames.weather]['temperature'])
        temperature_description = observation_data[DataNames.weather]['temperature_description']
        encoded_temperature_description = self.temperature_description_df[temperature_description].astype(int)
        input_vector.extend(encoded_temperature_description)
        return input_vector


class _PurchaseDecoder:
    # TODO: assess function names, cleanup where needed
    def __init__(self, action_names_map, output_array, max_purchase_amount):
        self.action_names_map = action_names_map
        self.__output_array = output_array
        self.MAX_PURCHASE_AMOUNT = max_purchase_amount

    def decode_purchases(self):
        buy_map = self.__handle_purchase_decision()
        purchase_map = {}
        for decision_locator, decision in buy_map.items():
            if decision:
                amount_locator = decision_locator + '_num_times'
                purchase_amount = self.__handle_purchase_amounts(amount_locator)
                purchase_map[amount_locator] = purchase_amount
        purchases = self.__decode_purchases(purchase_map)
        return purchases

    def __handle_purchase_decision(self):
        items = ['cups', 'coffee', 'milk', 'sugar']
        buy_map = {}
        for item in items:
            for option in range(1, 4):
                item_option_locator = f'buy_{item}_option_{option}'
                item_option_idx = self.action_names_map[item_option_locator]
                purchase_decision = self.__output_array[item_option_idx] > 0.5
                buy_map[item_option_locator] = purchase_decision
        return buy_map

    def __handle_purchase_amounts(self, amount_locator):
        amount_idx = self.action_names_map[amount_locator]
        raw_amount = self.__output_array[amount_idx]

        amount_min, amount_max = (1, self.MAX_PURCHASE_AMOUNT)
        data_min, data_max = (0, 1)

        amount_range = amount_max - amount_min
        data_range = 1

        converted_amount = (((raw_amount - data_min) * amount_range) / data_range) + amount_min

        return round(converted_amount)

    @staticmethod
    def __decode_purchases(purchase_map):
        #  Returns a list of tuples
        purchases = []
        for purchase_info, amount in purchase_map.items():
            item_name = purchase_info.split('_')[1]
            option_number = int(purchase_info.split('_')[3]) - 1  # option ranges from (0, 2), hence the minus one
            purchases.extend([(item_name, option_number) for _ in range(amount)])
        return purchases


#
# class RLModel
#
#
#
#     import torch
#     import torch.nn as nn
#
#     # Define the MLP architecture.
#     class MLPPolicy(nn.Module):
#         def __init__(self, state_size, action_size):
#             super(MLPPolicy, self).__init__()
#             self.fc1 = nn.Linear(state_size, 128)
#             self.fc2 = nn.Linear(128, action_size)
#
#         def forward(self, state):
#             x = self.fc1(state)
#             x = torch.relu(x)
#             x = self.fc2(x)
#             return x
#
#     # Initialize the MLP parameters.
#     model = MLPPolicy(10, 10)
#
#     # Define the loss function.
#     loss_fn = nn.CrossEntropyLoss()
#
#     # Define the optimizer.
#     optimizer = torch.optim.Adam(model.parameters())

    # # Train the MLP model.
    # for epoch in range(10):
    #     # Get a batch of data.
    #     state = torch.randint(0, 2, (10, 10))
    #     action = model(state)
    #
    #     # Calculate the loss.
    #     loss = loss_fn(model(state), action)
    #
    #     # Backpropagate the loss.
    #     optimizer.zero_grad()
    #     loss.backward()
    #     optimizer.step()
    #
    # # Evaluate the MLP model.
    # state = torch.randint(0, 2, (10, 10))
    # action = model(state)
    #
    # # Print the action.
    # print(action)
