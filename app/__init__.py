
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

from src.calculations import TradeCalculator, get_address_data

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})

db_set = "postgresql://localhost:5432/hackathon_bnb"
app.debug = True
app.secret_key = 'whatev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config.update({
    'SQLALCHEMY_DATABASE_URI': db_set,
    "SQLACHEMY_POOL_SIZE": 2,
    "SQLACHEMY_MAX_OVERFLOW": 50,
    "SQLACHEMY_POOL_RECYCLE": 10,
    "PROTOPY_SCHEMA": "user",
    "PUBLIC_SCHEMA_TABLES": [],
    "GET_SCHEMAS_QUERY": "select nspname from pg_namespace"
})

db = SQLAlchemy()
db.init_app(app)

@app.route('/')
def index():
    return "Hello world"

@app.route('/addresses/sort_all', methods=['GET', 'POST'])
@cross_origin(origin='*')
def sort_all():
    data = request.data
    c = TradeCalculator(['bnb14cwvpg9u9vunnnqcslz4r766pacg30rle36zlt',
        'bnb1xazt0qc6h29nvr9sksyfdvtc87vg6vcp3hz72n',
        'bnb1pryxsu30ausk3ypywqjrl56r8fnhy84yxmpaxf'], 'USD')
    trades = c.sort_all()
    return jsonify(trades)

@app.route('/addresses/sort_by_date', methods=['GET', 'POST'])
@cross_origin(origin='*')
def sort_by_date():
    data = request.data
    c = TradeCalculator(['bnb14cwvpg9u9vunnnqcslz4r766pacg30rle36zlt',
        'bnb1xazt0qc6h29nvr9sksyfdvtc87vg6vcp3hz72n',
        'bnb1pryxsu30ausk3ypywqjrl56r8fnhy84yxmpaxf'], 'USD')
    trades = c.sort_by_date()
    return jsonify(trades)

@app.route('/addresses/balances', methods=['GET', 'POST'])
@cross_origin(origin='*')
def get_balances():
    balances = get_address_data(['bnb14cwvpg9u9vunnnqcslz4r766pacg30rle36zlt',
        'bnb1xazt0qc6h29nvr9sksyfdvtc87vg6vcp3hz72n',
        'bnb1pryxsu30ausk3ypywqjrl56r8fnhy84yxmpaxf'], 'USD')

    return jsonify(decimal_to_float(balances[0]))

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

if __name__ == "__main__":
    app.run(host='192.168.51.38', port=5000)
