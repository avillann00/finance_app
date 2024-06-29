# import the data base
from . import db
from flask_login import UserMixin # usermixin gives user properties that make it easier to login and logout
from sqlalchemy.sql import func # allows the date to be extracted

# payment template
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True) # unique payment id 
    amount = db.Column(db.Float) # amount of the payment
    tag = db.Column(db.String(50)) # reason for the payment
    date = db.Column(db.DateTime(timezone=True), default=func.now()) # date the payment was made
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # the user the payment is associated with

# monthly expense template
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True) # unique expense id 
    amount = db.Column(db.Float) # amount of the expense
    tag = db.Column(db.String(50)) # reason for the for the expense
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # the user the expense is associated with

# user template
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) # unique user id
    email = db.Column(db.String(150), unique=True) # user email
    password = db.Column(db.String(150)) # user password
    first_name = db.Column(db.String(150)) # user first name
    monthly = db.Column(db.Float) # monthly income
    yearly = db.Column(db.Float) # yearly income
    expenses = db.relationship('Expense')
    payments = db.relationship('Payment')
