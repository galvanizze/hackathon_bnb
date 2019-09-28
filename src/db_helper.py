from src.db_init import db
from src.models import Trade


def reset_tables():
    Trade.__table__.drop(db.engine)
    Trade.__table__.create(db.engine)


if __name__ == '__main__':
    reset_tables()