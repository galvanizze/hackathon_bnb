import pytest

from src.db_init import db
from src.models import Trade
from src.loaders import load_trades

class TestLoader:

    def set_up(self):
        # TODO injection
        self.test_addresses = ['bnb1wvkpn8mtphdduzjlwejkcj4kc9kmw0hj6nz4r7']

    def clean_up(self):
        # TODO delete injected records
        pass

    def test_load_trades(self, capsys):
        self.set_up()

        trades = load_trades(self.test_addresses, 'USD')

        if trades.count() == 0:
            assert "Error in loading address trades"
