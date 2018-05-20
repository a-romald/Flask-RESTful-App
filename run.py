#!/usr/bin/env python
import os
from app import app, db
from app.models import User, Product, Order
from flask_script import Manager, Shell

manager = Manager(app)


if __name__ == '__main__':
    db.create_all()
    manager.run()