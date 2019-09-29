from sqlalchemy import func

from src.db_init import db
from src.models import Trade, Tx, Balance

def load_trades(addresses, **kwargs):
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

    trades = db.session.query(Trade).\
        filter(*filters)

    return trades


def load_balances(addresses):
    addr_filter = []

    if len(addresses) > 1:
        addr_filter.append(Balance.address.in_(addresses))
    else:
        addr_filter.append(Balance.address == addresses[0])

    balances = db.session.\
        query(Balance.symbol, func.count(Balance.amount)).\
        group_by(Balance.symbol).\
        filter(*addr_filter).\
        all()

    return balances

