from dataclasses import dataclass

from selenium.webdriver.common.by import By


@dataclass(frozen=True)
class InventoryDataLocators:
    name = 'inventory'
    names = ['cups', 'coffee', 'milk', 'sugar']
    cups = ('', '')
    coffee = ('', '')
    milk = ('', '')
    sugar = ('', '')
    map = {}
    for idx, name in enumerate(names):
        map[name] = ('xpath', f'/html/body/div[2]/section[3]/div[3]/div[1]/div[1]/div/div[{idx + 1}]/p[1]/b')
        exec(f"{name} = ('xpath', '/html/body/div[2]/section[3]/div[3]/div[1]/div[1]/div/div[{idx + 1}]/p[1]/b')")


@dataclass(frozen=True)
class ButtonLocators:
    play = (By.XPATH, "/html/body/div[2]/section[1]/ul/li[1]/button")
    skip_tutorial = (By.XPATH, "/html/body/div[2]/section[5]/div/p/button[1]")
    next = (By.XPATH, "/html/body/div[2]/section[5]/div/p/button[3]")
    start_day = (By.XPATH, "/html/body/div[2]/section[3]/div[3]/button")

    buy_map = {
        InventoryDataLocators.names[row - 1]: {(idx - 2): (
            By.XPATH, f'/html/body/div[2]/section[3]/div[3]/div[1]/div[1]/div/div[{row}]/p[{idx}]/button')
            for idx in range(2, 5)
        }
        for row in range(1, 5)
    }

#
# '/html/body/div[2]/section[3]/div[3]/div[1]/div[1]/div/div[1]/p[2]/button'
# '/html/body/div[2]/section[3]/div[3]/div[1]/div[1]/div/div[1]/p[4]/button'
# @dataclass(frozen=True)
# class InventoryBuyButtonLocators:
#     names = ['cups', 'coffee', 'milk', 'sugar']
#     cups = ('','')
#     coffee = ('','')
#     milk = ('','')
#     sugar = ('','')
#     for idx, name in enumerate(names):
#         exec(f"{name} = ('xpath', '/html/body/div[2]/section[3]/div[3]/div[1]/div[1]/div/div[1]/p[{idx+1}]/b')")
#
#
# if __name__ == "__main__":
#     # print(InventoryDataLocators.cups)
#     print(ButtonLocators.buy_map)
#     pass
