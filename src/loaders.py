from src.db_init import db
from src.models import Trade, Tx, Balance, OHLC, Token
from datetime import datetime

def get_filters(addresses=None, **kwargs):
    """Loads trades for given filters. Returns session query.

    Args:
        * addresses - <list> of <str>, mandatory
        * base_asset - <str> token/currency id
        * symbol - <str> standardized XXX-NNN symbol
        * quantity - <float>
        * price - <float>
        * date_range - <list> of dates, first element
            date from, second element is date to
    """

    # filters
    filters = []

    if len(addresses) > 1:
        filters.append(db.or_(Trade.seller_id.in_(addresses), Trade.buyer_id.in_(addresses)))
    else:
        filters.append(db.or_(Trade.seller_id == addresses[0], Trade.buyer_id == addresses[0]))

    if kwargs.get('base_asset') is not None:
        filters.append(Trade.base_asset == kwargs['base_asset'])

    if kwargs.get('symbol') is not None:
        filters.append(Trade.base_asset == kwargs['symbol'])

    if kwargs.get('quantity') is not None:
        filters.append(
            eval("Trade.quantity kwargs['quantity']['condition'] kwargs['quantity']['value']")
        )

    if kwargs.get('price') is not None:
        filters.append(
            eval("Trade.price kwargs['price']['condition'] kwargs['price']['value']")
        )

    if kwargs.get('date_range') is not None:
        filters.append(Trade.date >= kwargs['date_range'][0])
        filters.append(Trade.date <= kwargs['date_range'][1])

    return filters


def load_trades(addresses, quote_asset, **kwargs):
    filters = get_filters(addresses, **kwargs)

    target = db.alias(OHLC)
    fee = db.alias(OHLC)
    trades = db.session.query(
            Trade.base_asset.label('base_asset'),
            Trade.quote_asset.label('quote_asset'),
            Trade.quantity.label('quantity'),
            Trade.price.label('price'),
            db.func.date(Trade.date).label('date'),
            Trade.buy_single_fee_asset.label('buy_single_fee_asset'),
            fee.columns.close.label('fee_price'),
            target.columns.close.label('target_price'),
            (Trade.buy_single_fee*fee.columns.close).label('buy_fee'),
            (Trade.price*Trade.quantity).label('volume')
        ).\
        filter(*filters).\
        join(fee, db.and_(
            Trade.buy_single_fee_asset == fee.columns.base_asset,
            quote_asset == fee.columns.quote_asset,
            db.func.date(Trade.date) == db.func.date(fee.columns.date),
        )).\
        join(target, db.and_(
        Trade.quote_asset == target.columns.base_asset,
        quote_asset == target.columns.quote_asset,
        db.func.date(Trade.date) == db.func.date(target.columns.date),
    ))

    return trades


def load_balances(addresses, target_asset):
    filter = []

    if len(addresses) > 1:
        filter.append(Balance.address.in_(addresses))
    else:
        filter.append(Balance.address == addresses[0])

    target = db.alias(OHLC)
    token = db.alias(Token)

    balances = db.session.query(
        Balance.symbol.label('symbol'),
        Balance.address.label('address'),
        Balance.amount.label('amount'),
        token.columns.name.label('token_name'),
        target.columns.quote_asset.label('target'),
        (db.func.count(Balance.amount) * target.columns.close).label('price')
    ). \
        join(token, Balance.symbol == token.columns.symbol). \
        join(target, db.and_(
        Balance.symbol == target.columns.base_asset,
        db.func.date(Balance.date) == db.func.date(target.columns.date)
    )). \
        filter(*(filter + [target.columns.quote_asset == target_asset])). \
        group_by(
        Balance.symbol,
        Balance.address,
        Balance.amount,
        token.columns.name,
        target.columns.close,
        target.columns.quote_asset
    )

    _balances = []
    for b in balances:
        _balances.append({
            'symbol': b.symbol,
            'address': b.address,
            'amount': float(b.amount),
            'token_name': b.token_name,
            'target': b.target,
            'price': float(b.price)
        })
    return _balances


def group_by_date(addresses, **kwargs):
    filters = get_filters(addresses, **kwargs)

    trades = db.session. \
        query(
        db.func.count(Trade.id),
        db.func.max(db.func.date(Trade.date),
                    db.func.sum(Trade.quantity),
                    db.func.sum(Trade.quantity * Trade.price)
                    )). \
        filter(*filters). \
        group_by(db.func.date(Trade.date), Trade.base_asset)

    return trades
