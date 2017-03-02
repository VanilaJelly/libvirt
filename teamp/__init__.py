"""init.py"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

db = SQlAlchemy(app)

from teamp import views
