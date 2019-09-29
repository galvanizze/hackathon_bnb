import requests
from datetime import datetime, timedelta
from sqlalchemy import and_
from decimal import Decimal
from time import sleep

from src.db_init import db
from src.models import Trade, OHLC

"""Fetching OHLC from trades and api."""


def generate_ohlc_from_trades(start_date):
    d = start_date
    while d <= datetime.now():
        generate_daily_ohlc_from_trades(d)
        d += timedelta(days=1)


def generate_daily_ohlc_from_trades(date):
    date_low, date_high = _get_date_range(date)
    trades = db.session.query(Trade).filter(
        and_(Trade.date < date_high, Trade.date >= date_low)).all()

    ohlc = []
    pairs = set(t.symbol for t in trades)

    for symbol in pairs:
        sub_trades = [t for t in trades if t.symbol == symbol]
        sorted_trades = sorted(sub_trades, key=lambda k: k.date)

        ohlc.append(OHLC(
            base_asset=symbol.split('_')[0],
            quote_asset=symbol.split('_')[1],
            date=date,
            open=sorted_trades[0].price,
            high=max(sorted_trades, key=lambda k: k.date).price,
            low=min(sorted_trades, key=lambda k: k.date).price,
            close=sorted_trades[-1].price
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
    start_date = datetime(2019, 8, 22)
    generate_ohlc_from_trades(start_date)
    save_ohlc_from_cg(start_date)
