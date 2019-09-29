
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO

from src.calculations import TradeCalculator

app = Flask(__name__)

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
