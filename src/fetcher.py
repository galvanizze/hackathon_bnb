from src.models import Tx, Trade, Token, Market, db

from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
from decimal import Decimal
from blockapi.services import Service, set_default_args_values


class BinanceAPI(Service):
    """
    coins: binance coin
    API docs: https://docs.binance.org/api-reference/dex-api/paths.html
    Explorer: https://explorer.binance.org
    """

    active = True

    symbol = 'BNB'
    base_url = 'https://dex.binance.org/api/v1'
    rate_limit = 1
    start_offset = 0
    max_items_per_page = 1000
    page_offset_step = 1

    supported_requests = {
        'get_txs': '/transactions?address={address}&startTime={start_time}&endTime={end_time}'
                   '&offset={offset}&limit={limit}',
        'get_trades': '/trades?startTime={start_time}&endTime={end_time}&offset={offset}&limit={limit}',
        'get_tokens': '/tokens?offset={offset}&limit={limit}',
        'get_markets': '/markets?offset={offset}&limit={limit}'
    }

    @set_default_args_values
    def get_txs(self, address, start_time, end_time, offset=None, limit=None):
        response = self.request(
            'get_txs',
            with_rate_limit=False,
            address=address,
            start_time=start_time,
            end_time=end_time,
            offset=offset,
            limit=limit
        )

        return [self.parse_tx(t) for t in response['tx']]

    def parse_tx(self, raw_tx):
        return Tx(
            block_height=int(raw_tx['blockHeight']),
            code=int(raw_tx['code']),
            data=raw_tx['data'],
            from_address=raw_tx['fromAddr'],
            order_id=raw_tx['orderId'],
            date=datetime.strptime(raw_tx['timeStamp'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            to_address=raw_tx['toAddr'],
            tx_age=int(raw_tx['txAge']),
            tx_asset=raw_tx['txAsset'],
            tx_fee=Decimal(raw_tx['txFee']),
            tx_hash=raw_tx['txHash'],
            tx_type=raw_tx['txType'],
            value=Decimal(raw_tx['value']),
            source=int(raw_tx['source']),
            sequence=int(raw_tx['sequence']),
            swap_id=raw_tx['swapId'],
            proposal_id=raw_tx['proposalId']
        )

    @set_default_args_values
    def get_trades(self, start_time, end_time, offset=None, limit=None):
        response = self.request(
            'get_trades',
            with_rate_limit=False,
            start_time=start_time,
            end_time=end_time,
            offset=offset,
            limit=limit
        )

        return [self.parse_trade(t) for t in response['trade']]

    def parse_trade(self, raw_trade):
        return Trade(
            base_asset=raw_trade['baseAsset'],
            block_height=int(raw_trade['blockHeight']),
            buy_fee=raw_trade['buyFee'],
            # buy_fee=Decimal(raw_trade['buyFee'].split(':')[1].replace(';', '')),
            # buy_fee_asset=raw_trade['buyFee'].split(':')[0],
            buyer_id=raw_trade['buyerId'],
            buyer_order_id=raw_trade['buyerOrderId'],
            buy_single_fee=Decimal(raw_trade['buySingleFee'].split(':')[1].replace(';', '')),
            buy_single_fee_asset=raw_trade['buySingleFee'].split(':')[0],
            price=Decimal(raw_trade['price']),
            quantity=Decimal(raw_trade['quantity']),
            quote_asset=raw_trade['quoteAsset'],
            sell_fee=raw_trade['sellFee'],
            # sell_fee=Decimal(raw_trade['sellFee'].split(':')[1].replace(';', '')),
            # sell_fee_asset=raw_trade['sellFee'].split(':')[0],
            seller_id=raw_trade['sellerId'],
            seller_order_id=raw_trade['sellerOrderId'],
            sell_single_fee=Decimal(raw_trade['sellSingleFee'].split(':')[1].replace(';', '')),
            sell_single_fee_asset=raw_trade['sellSingleFee'].split(':')[0],
            symbol=raw_trade['symbol'],
            tick_type=raw_trade['tickType'],
            date=datetime.fromtimestamp(int(raw_trade['time']) / 1000.0, pytz.utc),
            trade_id=raw_trade['tradeId']
        )

    @set_default_args_values
    def get_tokens(self, offset=None, limit=None):
        response = self.request(
            'get_tokens', with_rate_limit=False, offset=offset, limit=limit
        )

        return [self.parse_token(t) for t in response]

    def parse_token(self, raw_token):
        return Token(
            name=raw_token['name'],
            symbol=raw_token['symbol'],
            original_symbol=raw_token['original_symbol'],
            total_supply=Decimal(raw_token['total_supply']),
            owner=raw_token['owner']
        )

    @set_default_args_values
    def get_markets(self, offset=None, limit=None):
        response = self.request(
            'get_markets', with_rate_limit=False, offset=offset, limit=limit
        )

        return [self.parse_token(m) for m in response]

    def parse_market(self, raw_market):
        return Market(
            base_asset_symbol=raw_market['base_asset_symbol'],
            quote_asset_symbol=raw_market['quote_asset_symbol'],
            list_price=Decimal(raw_market['list_price']),
            tick_size=Decimal(raw_market['tick_size']),
            lot_size=Decimal(raw_market['lot_size'])
        )


class PaginatedRequest:
    """Fetching data from api in multiple paginated calls.
    It could be any type of records, which can be fetched by pagination."""

    def __init__(self, api, method, start_offset=None,
                 since=None, until=None, until_field={}, **method_kwargs):
        self.api = api
        self.method = method
        self.method_kwargs = method_kwargs

        if start_offset:
            self.offset = start_offset
        else:
            self.offset = self.api.start_offset

        self.since = since
        self.until = until

        self.until_name, self.until_value = None, None
        if until_field:
            self.until_name, self.until_value = list(until_field.items())[0]

        self.items = []
        self.fetched = False

        self._last_response_hash = None
        self.last_offset = None
        self._stop_fetching = False

    def fetch(self):
        """Yields all records from api."""

        self._stop_fetching = False
        while True:
            print('processing items in {} round'.format(self.offset + 1))

            items = getattr(self.api, self.method)(
                offset=self.offset, **self.method_kwargs
            )
            if not items:
                break

            items = self._preprocess_and_filter(items)
            self.items.extend(items)

            yield items

            if self._stop_fetching:
                break

            self.offset += self.api.page_offset_step

        self.fetched = True

    def _preprocess_and_filter(self, items):
        self.last_offset = self.offset

        # compare hashes of 2 last responses, if equals then stop
        current_hash = hash(str(items))

        if self._last_response_hash:
            if current_hash == self._last_response_hash:
                self._stop_fetching = True
                # in case of the same response as previous, last success offset
                # was the previous one
                self.last_offset -= 1
                return []

        self._last_response_hash = current_hash

        # filter items by order
        if items[0].date > items[-1].date:
            return self._filter_descending(items)
        else:
            return self._filter_ascending(items)

    def _filter_descending(self, items):
        if self.until_value:
            # remove all records after (and including) last value
            last_idx = next((i for i, item in enumerate(items)
                             if getattr(item, self.until_name) == self.until_value), None)
            # idx can be 0
            if not (last_idx is None):
                items = items[:last_idx]
                self._stop_fetching = True

        if self.since:
            orig_len = len(items)
            items = [i for i in items if i.date >= self.since]
            if orig_len > len(items):
                self._stop_fetching = True

        if self.until:
            items = [i for i in items if i.date <= self.until]

        return items

    def _filter_ascending(self, items):
        if self.until_value:
            # remove all records after (and including) first value
            last_idx = next((i for i, item in list(enumerate(items))[::-1]
                             if getattr(item, self.until_name) == self.until_value), None)
            # idx can be 0
            if not (last_idx is None):
                items = items[(last_idx + 1):]

        if self.since:
            items = [i for i in items if i.date >= self.since]

        if self.until:
            orig_len = len(items)
            items = [i for i in items if i.date <= self.until]
            if orig_len > len(items):
                self._stop_fetching = True

        return items


def fetch_txs():
    newest = db.session.query(Tx).order_by(Tx.date.desc()).first()
    until_field = {'tx_hash': newest.tx_hash}
    _fetch_new_items('get_txs', newest.date, until_field)


def fetch_trades():
    newest = db.session.query(Trade).order_by(Trade.date.desc()).first()
    until_field = {'trade_id': newest.trade_id}
    _fetch_new_items('get_trades', newest.date, until_field)


def _fetch_new_items(method, since_date, until_field=None):
    # use date from last record, or set date of first tx in dex bnb exchange
    if since_date:
        since_ts = int(since_date.timestamp())
    else:
        since_ts = int(datetime(2019, 8, 22, tzinfo=pytz.utc).timestamp())

    if not until_field:
        until_field = {}

    # TODO This will not work after 22.11., call paginated request in cycle
    # max window for data is 3 months
    until_ts = int((since_date + relativedelta(months=3)).timestamp())

    bnb_api = BinanceAPI()
    paginated_request = PaginatedRequest(
        bnb_api,
        method,
        # do not use standard since and until dates
        # they are used in api calling, see below
        until_field=until_field,
        # args for calling api method
        start_time=since_ts,
        end_time=until_ts
    )

    # from multiprocessing import Pool
    # pool = Pool(2)
    #
    # items_generator = paginated_request.fetch()
    # pool.imap(_save_items, items_generator)
    # pool.close()

    for items_list in paginated_request.fetch():
        _save_items(items_list)


def fetch_tokens():
    bnb_api = BinanceAPI()
    paginated_request = PaginatedRequest(bnb_api, 'get_tokens')

    for items_list in paginated_request.fetch():
        db.session.add_all(items_list)

    Token.query.delete()
    db.session.commit()


def fetch_markets():
    bnb_api = BinanceAPI()
    paginated_request = PaginatedRequest(bnb_api, 'get_markets')

    for items_list in paginated_request.fetch():
        db.session.add_all(items_list)

    Market.query.delete()
    db.session.commit()


def _save_items(items_list):
    print('saving items')
    db.session.add_all(items_list)
    db.session.commit()


if __name__ == '__main__':
    fetch_trades()
