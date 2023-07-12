from dataclasses import dataclass


@dataclass
class DailyData:
    balance: float
    day: int
    temperature: int
    temperature_description: str
    reputation: str


@dataclass
class InventoryData:
    cups: int
    coffee: int
    milk: int
    sugar: int


@dataclass
class RecipeInfoData:
    coffee: int
    milk: int
    sugar: int
    cups: int = 1
