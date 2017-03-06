"""__init__.py"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/teamp.db'

db = SQLAlchemy(app)

from teamp import views
