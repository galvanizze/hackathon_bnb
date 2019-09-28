from .db_init import db


class Tx(db.Model):
    __tablename__ = "txs"
    id = db.Column(db.Integer(), primary_key=True)
    block_height = db.Column(db.Integer(), index=True)
    code = db.Column(db.Integer())
    # confirm_blocks = db.Column(db.String(64))
    data = db.Column(db.String(64))
    from_address = db.Column(db.String(64), index=True)
    order_id = db.Column(db.String(64))
    date = db.Column(db.DateTime(), index=True)
    to_address = db.Column(db.String(64), index=True)
    tx_age = db.Column(db.Integer())
    tx_asset = db.Column(db.String())
    tx_fee = db.Column(db.DECIMAL())
    tx_hash = db.Column(db.String())
    tx_type = db.Column(db.String())
    value = db.Column(db.DECIMAL())
    source = db.Column(db.Integer())
    sequence = db.Column(db.Integer())
    swap_id = db.Column(db.String())
    proposal_id = db.Column(db.String())


class Trade(db.Model):
    __tablename__ = "trades"
    id = db.Column(db.Integer(), primary_key=True)
    base_asset = db.Column(db.String(64), index=True)
    block_height = db.Column(db.Integer(), index=True)
    buy_fee = db.Column(db.String())
    # buy_fee = db.Column(db.DECIMAL())
    # buy_fee_asset = db.Column(db.String())
    buyer_id = db.Column(db.String(64))
    buyer_order_id = db.Column(db.String(64))
    buy_single_fee = db.Column(db.DECIMAL())
    buy_single_fee_asset = db.Column(db.String(64))
    price = db.Column(db.DECIMAL())
    quantity = db.Column(db.DECIMAL())
    quote_asset = db.Column(db.String(), index=True)
    sell_fee = db.Column(db.String())
    # sell_fee = db.Column(db.DECIMAL())
    # sell_fee_asset = db.Column(db.String())
    seller_id = db.Column(db.String())
    seller_order_id = db.Column(db.String())
    sell_single_fee = db.Column(db.DECIMAL())
    sell_single_fee_asset = db.Column(db.String(64))
    symbol = db.Column(db.String(64), index=True)
    tick_type = db.Column(db.String(64))
    date = db.Column(db.DateTime(), index=True)
    trade_id = db.Column(db.String(64))


class Token(db.Model):
    __tablename__ = "tokens"
    name = db.Column(db.String(64))
    symbol = db.Column(db.String(64))
    original_symbol = db.Column(db.String(64))
    total_supply = db.Column(db.DECIMAL())
    owner = db.Column(db.String(64))


class Market(db.Model):
    __tablename__ = "markets"
    base_asset_symbol = db.Column(db.String(64))
    quote_asset_symbol = db.Column(db.String(64))
    list_price = db.Column(db.DECIMAL())
    tick_size = db.Column(db.DECIMAL())
    lot_size = db.Column(db.DECIMAL())
