
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

from src.calculations import TradeCalculator

app = Flask(__name__)
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

@app.route('/address/sort_all', methods=['GET', 'POST'])
def parse_request():
    data = request.data
    c = TradeCalculator(['bnb1wvkpn8mtphdduzjlwejkcj4kc9kmw0hj6nz4r7'], 'USD')
    trades = c.sort_all()
    return "Message received"

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')
