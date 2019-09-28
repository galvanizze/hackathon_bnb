import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db_set = "postgresql://localhost:5432/hackathon_bnb"

app = Flask(__name__, template_folder='templates')
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

db = SQLAlchemy(app)
