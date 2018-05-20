from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os, config

# create application instance
app = Flask(__name__)
app.config.from_object(os.environ.get('FLASK_ENV') or 'config.ProductionConfig')

# initializes extensions
db = SQLAlchemy(app)

# import routes
from . import routes
