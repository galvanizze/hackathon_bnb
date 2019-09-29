import pytest

from src.db_init import db
from src.models import Trade
from src.loaders import load_trades
from src.calculations import TradeCalculator

class TestTradeCalculator:

    def set_up(self):
        # TODO injection
        test_addresses = ['bnb1eff4hzx4lfsun3px5walchdy4vek4n0njcdzyn']
        trades = load_trades(test_addresses)
        self.trade_calculator = TradeCalculator(trades, test_addresses)

    def clean_up(self):
        # TODO delete injected records
        pass

    def test_sort_all(self, capsys):
        self.set_up()

        with capsys.disabled():
            print(len(self.trade_calculator.trades))
            print(self.trade_calculator.sort_all())
