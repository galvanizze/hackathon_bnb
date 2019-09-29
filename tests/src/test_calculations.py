import pytest

from src.db_init import db
from src.models import Trade
from src.loaders import load_trades
from src.calculations import TradeCalculator

class TestTradeCalculator:

    def set_up(self):
        # TODO injection
        test_addresses = ['bnb14cwvpg9u9vunnnqcslz4r766pacg30rle36zlt']
        self.trade_calculator = TradeCalculator(test_addresses, 'USD')

    def clean_up(self):
        # TODO delete injected records
        pass

    def test_sort_all(self, capsys):
        with capsys.disabled():
            self.set_up()

        with capsys.disabled():
            print(self.trade_calculator.sort_all())
            print(self.trade_calculator.sort_by_date())
