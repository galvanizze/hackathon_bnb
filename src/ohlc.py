from datetime import datetime, timedelta
from sqlalchemy import and_

from src.db_init import db
from src.models import Trade, OHLC

"""Fetching OHLC from data and api."""


def generate_ohlc_from_trades():
    d = datetime(2019, 8, 22)
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


if __name__ == '__main__':
    generate_daily_ohlc_from_trades(datetime(2019, 9, 29))
