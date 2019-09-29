
from src.db_init import db
from src.models import Trade, OHLC

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
            Trade,
            fee.columns.close.label('fee_price'),
            target.columns.close.label('target_price')
        ).\
        filter(*filters).\
        join(fee, db.and_(
            Trade.buy_single_fee_asset == fee.columns.base_asset,
            db.func.date(Trade.date) == db.func.date(fee.columns.date),
        )).\
        join(target, db.and_(
            Trade.quote_asset == target.columns.base_asset,
            quote_asset == target.columns.quote_asset,
            db.func.date(Trade.date) == db.func.date(target.columns.date),
        ))

    return trades

def group_by_date(addresses, **kwargs):
    filters = get_filters(addresses, **kwargs)

    trades = db.session.\
        query(
            db.func.count(Trade.id),
            db.func.max(db.func.date(Trade.date),
            db.func.sum(Trade.quantity),
            db.func.sum(Trade.quantity*Trade.price)
        )).\
        filter(*filters).\
        group_by(db.func.date(Trade.date), Trade.base_asset)

    return trades

# def load_ohlc(currencies, quote_asset):
#
#     if isinstance(currencies, str) or len(currencies) == 1:
#         ohlcs = db.session(OHLC).\
#             filter()
