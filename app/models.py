from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from flask import g, current_app
from datetime import datetime


# TABLES
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(128), index=True)
    email = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self):
        hextoken = uuid.uuid4().hex
        self.token = hextoken

    @staticmethod
    def verify_auth_token(token):
        user = User.query.filter_by(token = token).first()
        if not user:
            return False
        g.user = user
        return True




order_product = db.Table('order_product',
    db.Column('order_id', db.Integer, db.ForeignKey('orders.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'))
)



class Product(db.Model) :
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True)
    alias = db.Column(db.String(64), index=True)
    
    


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now())
    products = db.relationship('Product', secondary=order_product, backref=db.backref('products', lazy='dynamic'), lazy='dynamic', cascade='all')    

