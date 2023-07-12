# This is a sample Python script.
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    # try:
    driver = webdriver.Firefox()
    driver.install_addon('ublock_origin-1.50.0.xpi', temporary=True)
    driver.get("https://www.coolmathgames.com/0-coffee-shop")

    # element = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.ID, "screen-main"))
    # )

    print("waiting 10 seconds")
    time.sleep(10)
    print(driver.page_source)
    element = driver.find_elements(By.ID, "screen-main")
    print(element)

    # except Exception as e:
    #     print(e)
    # finally:
    #     driver.close()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
