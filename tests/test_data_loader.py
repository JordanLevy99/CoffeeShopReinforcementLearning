import unittest

from selenium import webdriver

from src.game.play import Game


class TestDataLoader(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.driver = webdriver.Firefox()
        cls.driver.get('file:///https __www.coolmathgames.com_0-coffee-shop.htm')

    def test_data_loaded(self):

        game = Game(self.driver)
        game.load_data()
        pass

        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
