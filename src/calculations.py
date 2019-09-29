from collections import defaultdict
from decimal import Decimal

from src.db_init import db
from src.loaders import load_trades
from src.models import Trade

class TradeCalculator:

    def __init__(self, trades_query, addresses):
        self.trades_query = trades_query
        self.addresses = addresses

    def sort_all(self):
    
        buy_fees = [(t.buy_single_fee, t.buy_single_fee_asset, t.base_asset, t.quantity)
            for t in self.trades if t.buyer_id in self.addresses]

        buy_fees_dict = defaultdict(Decimal)
        buy_quantity_dict = defaultdict(Decimal)

        for fee, fee_asset, base_asset, q in buy_fees:
            buy_fees_dict[fee_asset] += fee
            buy_quantity_dict[base_asset] += q

        sell_fees = [(t.sell_single_fee, t.sell_single_fee_asset, t.base_asset, t.quantity)
            for t in self.trades if t.seller_id in self.addresses]

        sell_fees_dict = defaultdict(Decimal)
        sell_quantity_dict = defaultdict(Decimal)

        for fee, fee_asset, base_asset, q in sell_fees:
            sell_fees_dict[fee_asset] += fee
            sell_quantity_dict[base_asset] += q

        return {
            'buy_fee': buy_fees_dict,
            'sell_fee': sell_fees_dict,
            'buy_quantity': buy_quantity_dict,
            'sell_quantity': sell_quantity_dict
        }
