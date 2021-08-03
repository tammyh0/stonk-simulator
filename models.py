from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func


# Create database
db = SQLAlchemy()


# Stores users' account information
class User(db.Model, UserMixin):
  __tablename__ = "user"

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.Text, unique=True)
  password = db.Column(db.Text)
  cash = db.Column(db.Numeric(scale=2))
  holdings = db.relationship('Holding', backref='user', lazy=True)
  history = db.relationship('Transaction', backref='user', lazy=True)


# Stores users' current holdings 
class Holding(db.Model):
  __tablename__ = "holding"

  id = db.Column(db.Integer, primary_key=True)
  symbol = db.Column(db.Text)
  name = db.Column(db.Text)
  shares = db.Column(db.Integer)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# Stores users' transaction history
class Transaction(db.Model):
  __tablename__ = "transaction"

  id = db.Column(db.Integer, primary_key=True)
  timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
  symbol = db.Column(db.Text)
  name = db.Column(db.Text)
  price = db.Column(db.Numeric(scale=2))
  shares = db.Column(db.Integer)
  transaction_type = db.Column(db.Text)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)