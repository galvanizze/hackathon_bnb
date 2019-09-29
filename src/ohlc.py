import requests
from datetime import datetime, timedelta
from sqlalchemy import and_
from decimal import Decimal
from time import sleep

from src.db_init import db
from src.models import Trade, OHLC

"""Fetching OHLC from trades and api."""


def generate_ohlc():
    start_date = datetime(2019, 8, 22)

    # first get coingecko data
    cg_ohlc = save_ohlc_from_cg(start_date)
    # TODO for some pairs there are no trades in some days, they have to be filled postpone
    generate_ohlc_from_trades(start_date, cg_ohlc)


def generate_ohlc_from_trades(start_date, cg_ohlc):
    d = start_date
    while d <= datetime.now():
        daily_cg_ohlc = [o for o in cg_ohlc if o.date.date() == d.date()]
        generate_daily_ohlc_from_trades(d, daily_cg_ohlc)
        d += timedelta(days=1)


def generate_daily_ohlc_from_trades(date, cg_ohlc):
    date_low, date_high = _get_date_range(date)
    trades = db.session.query(Trade).filter(
        and_(Trade.date < date_high, Trade.date >= date_low)).all()

    ohlc = []
    pairs = set(t.symbol for t in trades)

    for symbol in pairs:
        sub_trades = [t for t in trades if t.symbol == symbol]
        sorted_trades = sorted(sub_trades, key=lambda k: k.date)

        _base = symbol.split('_')[0]
        _quote = symbol.split('_')[1]
        _open = sorted_trades[0].price
        _max = max(sorted_trades, key=lambda k: k.date).price
        _min = min(sorted_trades, key=lambda k: k.date).price
        _close = sorted_trades[-1].price

        ohlc.append(OHLC(
            base_asset=_base,
            quote_asset=_quote,
            date=date,
            open=_open,
            high=_max,
            low=_min,
            close=_close
        ))

        # create OHLC from CG currencies
        if _base == 'BNB':
            continue

        for cg_o in cg_ohlc:
            ohlc.append(OHLC(
                base_asset=_base,
                quote_asset=cg_o.quote_asset,
                date=date,
                open=_open * cg_o.close,
                high=_max * cg_o.close,
                low=_min * cg_o.close,
                close=_close * cg_o.close
            ))

    db.session.add_all(ohlc)
    db.session.commit()


def _get_date_range(date=None):
    if date is None:
        date = datetime.utcnow()

    low = date  # datetime.combine(date, datetime.min.time())  # , datetime.min.time()
    height = low + timedelta(days=1)

    return low, height


def save_ohlc_from_cg(start_date, to_symbols=None):
    if not to_symbols:
        to_symbols = ['eur', 'usd', 'btc', 'eth']

    d = start_date
    ohlc = []
    while d <= datetime.now():
        history = get_cg_coin_history('binancecoin', d)
        if not history:
            print('There are missing data for date {}'.format(str(d)))
            continue

        prices = history.get('market_data', {}).get('current_price')
        for symbol in to_symbols:
            ohlc.append(OHLC(
                base_asset='BNB',
                quote_asset=symbol.upper(),
                date=d,
                close=Decimal(prices[symbol])
            ))
        d += timedelta(days=1)
        sleep(0.6)

    db.session.add_all(ohlc)
    db.session.commit()

    return ohlc


def get_cg_coin_history(currency_id, date):
    formatted_date = date.strftime('%d-%m-%Y')
    url = 'https://api.coingecko.com/api/v3/coins/{}/history?date={}&localization=false'.format(
        currency_id, formatted_date
    )
    try:
        json = requests.get(url).json()
    except:
        return {}
    return json


if __name__ == '__main__':
    generate_ohlc()