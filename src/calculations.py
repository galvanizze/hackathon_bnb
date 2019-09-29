from collections import defaultdict
from decimal import Decimal
from datetime import datetime, timedelta

from src.db_init import db
from src.loaders import load_trades
from src.models import Trade
from src.decimal_convert import decimal_to_float

class TradeCalculator:

    def __init__(self, addresses, qoute_currency):
        self.trades_query = load_trades(addresses, qoute_currency)
        self.addresses = addresses

    def sort_all(self):
        if self.trades_query.count() > 200000:
            return {}

        fees_dict = defaultdict(Decimal)
        volume_dict = defaultdict(Decimal)

        for trade in self.trades_query.all():
            pair = '{}/{}'.format(trade.base_asset, trade.quote_asset)
            fees_dict[trade.buy_single_fee_asset] += trade.buy_fee
            volume_dict[pair] += trade.volume*trade.target_price

        data = {
            'fee': decimal_to_float(dict(fees_dict)),
            'volume': decimal_to_float(dict(volume_dict)),
        }

        final = {}
        for d in data:

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
            d = trade.date
            if d not in dates_dict:
                dates_dict[d] = {
                    'count': 0,
                    'quantity': defaultdict(Decimal),
                    'cost': defaultdict(Decimal)
                }

            pair = (trade.base_asset, trade.quote_asset)
            dates_dict[d]['count'] += 1
            dates_dict[d]['quantity'][pair] += trade.quantity
            dates_dict[d]['cost'][pair] += trade.volume*trade.target_price
            bases.add(pair)

        cost = {'datasets': [], 'labels': []}
        quantity = {'datasets': [], 'labels': []}
        values = {'cost': defaultdict(list), 'quantity': defaultdict(list)}
        min_date = min(dates_dict.keys())
        max_date = max(dates_dict.keys())
        date_list = [min_date + timedelta(days=x) for x in range((max_date-min_date).days)]

        for d in date_list:
            datum = d.strftime("%Y-%m-%d")
            cost['labels'].append(datum)
            quantity['labels'].append(datum)

            if d in dates_dict:
                dates_dict[d]['quantity'] = dict(dates_dict[d]['quantity'])
                dates_dict[d]['cost'] = dict(dates_dict[d]['cost'])

                for b in bases:
                    values['cost'][b].append(dates_dict[d]['cost'].get(b, 0))
                    values['quantity'][b].append(dates_dict[d]['quantity'].get(b, 0))
            else:
                for b in bases:
                    values['cost'][b].append(0)
                    values['quantity'][b].append(0)


        for c in values['cost']:
            cost['datasets'].append({'data': values['cost'][c], 'label': c[0]+"/"+c[1]})

        for c in values['quantity']:
            quantity['datasets'].append({'data': values['quantity'][c], 'label': c[0]+"/"+c[1]})

        return decimal_to_float({'cost': cost, 'quantity': quantity})

# class AggregatedData:
#
#     def __init__(self):
#         self.trades_query = load_trades(None, 'USD')
#
#     def aggregate(self):
#         total_txs = self.trades_query.count()
#         fees = self.trades_query.
