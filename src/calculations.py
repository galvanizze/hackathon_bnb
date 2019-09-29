from collections import defaultdict
from decimal import Decimal

from src.db_init import db
from src.loaders import load_trades
from src.models import Trade
from src.decimal_convert import decimal_to_float

class TradeCalculator:

    def __init__(self, trades_query, addresses):
        self.trades_query = trades_query
        self.addresses = addresses

    def sort_all(self):
        if self.trades_query.count() > 200000:
            return {}

        trades = self.trades_query.all()

        buy_trades = [(t.Trade.buy_single_fee, t.Trade.buy_single_fee_asset,
            t.Trade.base_asset, t.Trade.quantity)
            for t in trades if t.Trade.buyer_id in self.addresses]

        buy_fees_dict = defaultdict(Decimal)
        buy_quantity_dict = defaultdict(Decimal)
        max_buy = max([t[3] for t in buy_trades])

        for fee, fee_asset, base_asset, q in buy_trades:
            buy_fees_dict[fee_asset] += fee
            buy_quantity_dict[base_asset] += q

        sell_trades = [(t.Trade.sell_single_fee, t.Trade.sell_single_fee_asset,
            t.Trade.base_asset, t.Trade.quantity)
            for t in trades if t.Trade.seller_id in self.addresses]

        sell_fees_dict = defaultdict(Decimal)
        sell_quantity_dict = defaultdict(Decimal)
        max_sell = max([t[3] for t in sell_trades])

        for fee, fee_asset, base_asset, q in sell_trades:
            sell_fees_dict[fee_asset] += fee
            sell_quantity_dict[base_asset] += q

        data = {
            'buy_fee': decimal_to_float(dict(buy_fees_dict)),
            'sell_fee': decimal_to_float(dict(sell_fees_dict)),
            'buy_quantity': decimal_to_float(dict(buy_quantity_dict)),
            'sell_quantity': decimal_to_float(dict(sell_quantity_dict))
        }

        final = {}
        for d in data:
            if d in ['max_buy', 'max_sell']:
                final[d] = data[d]
                continue

            final[d] = {'datasets': [], 'labels': []}

            for k in data[d]:
                final[d]['datasets'].append(data[d][k])
                final[d]['labels'].append(k)

        return final

    def sort_by_date(self):
        if self.trades_query.count() > 200000:
            return {}

        trades = self.trades_query.all()
        bases = set()
        dates_dict = {}
        for trade in trades:
            d = trade.Trade.date.date()
            if d not in dates_dict:
                dates_dict[d] = {
                    'count': 0,
                    'quantity': defaultdict(Decimal),
                    'cost': defaultdict(Decimal)
                }

            pair = (trade.Trade.base_asset, trade.Trade.quote_asset)
            dates_dict[d]['count'] += 1
            dates_dict[d]['quantity'][pair] += trade.Trade.quantity
            dates_dict[d]['cost'][pair] += trade.Trade.quantity*trade.Trade.price
            bases.add(pair)

        cost = {'datasets': [], 'labels': []}
        quantity = {'datasets': [], 'labels': []}
        values = {'cost': defaultdict(list), 'quantity': defaultdict(list)}
        for d in dates_dict:
            datum = d.strftime("%Y-%m-%d")
            dates_dict[d]['quantity'] = dict(dates_dict[d]['quantity'])
            dates_dict[d]['cost'] = dict(dates_dict[d]['cost'])

            cost['labels'].append(datum)
            quantity['labels'].append(datum)

            for b in bases:
                values['cost'][b].append(dates_dict[d]['cost'].get(b, 0))
                values['quantity'][b].append(dates_dict[d]['quantity'].get(b, 0))


        for c in values['cost']:
            cost['datasets'].append({'data': values['cost'][c], 'label': c[0]+"/"+c[1]})

        for c in values['quantity']:
            quantity['datasets'].append({'data': values['quantity'][c], 'label': c[0]+"/"+c[1]})

        return decimal_to_float({'cost': cost, 'quantity': quantity})
