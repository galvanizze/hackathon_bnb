from src.db_init import db
from src.models import Trade, Tx, Token, Market, OHLC


def reset_tables():
    Trade.__table__.drop(db.engine)
    Trade.__table__.create(db.engine)

    Tx.__table__.drop(db.engine)
    Tx.__table__.create(db.engine)

    Token.__table__.drop(db.engine)
    Token.__table__.create(db.engine)

    Market.__table__.drop(db.engine)
    Market.__table__.create(db.engine)

    OHLC.__table__.drop(db.engine)
    OHLC.__table__.create(db.engine)


if __name__ == '__main__':
    OHLC.__table__.create(db.engine)
