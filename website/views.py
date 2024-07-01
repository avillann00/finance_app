# import everything for the financials related part of the app
from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_required, current_user
from .models import Payment, Expense
from . import db
from api_data import exchange, stocks
from apscheduler.schedulers.background import BackgroundScheduler
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import InputRequired, NumberRange
import matplotlib.pyplot as plt
import matplotlib
import io
import base64
import calendar

# make it so that the graph does not make a separatw window
matplotlib.use('agg')

# the template that is able to add and delete notes
views = Blueprint('views', __name__)

# hold the stocks and their prices and the currencies and their rates
rates_list = {}
stock_list = {}

# functions to update stocks and exchange rates
def update_rates():
    global rates_list
    rates_list = exchange.get_rates()

def update_stocks():
    global stock_list
    temp = stocks.get_stocks()
    if temp:
        stock_list = temp

# initialize the scheduler to update the stock prices and exchange rates
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_rates, trigger="interval", minutes=10)
scheduler.add_job(func=update_stocks, trigger="interval", minutes=10)
scheduler.start()

# call functions to update every 10 mins
update_stocks()
update_rates()

# form to hold amounts and tags for payments/expenses
class ExpenseForm(FlaskForm):
    amount = IntegerField('Amount', validators=[InputRequired(), NumberRange(min=0)])
    tag = StringField('Tag', validators=[InputRequired()])

# function to generate the spending bar graph
def generate_bar_graph(payments):
    # get the months 
    months = list(calendar.month_abbr)
    month_totals = {month: 0 for month in months[1:]}

    # get all the payments
    for payment in payments:
        month_name = payment.date.strftime('%b')
        month_totals[month_name] += payment.amount

    # total everything by the month
    for month in months[1:]:
        if month not in month_totals:
            month_totals[month] = 0

    # generate the graph
    plt.figure(figsize=(8, 6))
    plt.bar(month_totals.keys(), month_totals.values())
    plt.xlabel('Month')
    plt.ylabel('Total Amount Spent')
    plt.title('Monthly Spending for the Year')
    plt.tight_layout()

    # save it as a url
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)


# home page
@views.route('/', methods=['POST', 'GET'])
@login_required
def add_expense():
    # users monthly income
    monthly_income = current_user.monthly
    # all the expenses associated with that user
    total_expenses = sum(expense.amount for expense in current_user.expenses)

    # initialize the form
    form = ExpenseForm()

    # find info
    if request.method == 'POST':
        amount = float(request.form['amount'])
        tag = str(request.form.get('tag'))

        # error checks
        if len(tag) < 0:
            flash('Invalid tag', category='error')
        elif amount < 0:
            flash('Invalid amount', category='error')
        elif amount + total_expenses > monthly_income:
            flash('Expenses exceeds income', category='error')
        else:
            # add new expense
            new_expense = Expense(amount=amount, tag=tag, user_id=current_user.id)
            db.session.add(new_expense)
            db.session.commit()

    # re-total the total expenses
    total_expenses = sum(expense.amount for expense in current_user.expenses)

    # render the html template
    return render_template('fin/home.html', user=current_user, form=form, monthly_income=monthly_income, total_expenses=total_expenses)

# spending page
@views.route('/spending', methods=['POST', 'GET'])
@login_required
def add_payment():
    # currents users monthly income
    monthly_income = current_user.monthly
    # get all the payments for the user
    total_payments = sum(payment.amount for payment in current_user.payments)
    # generate the graph url
    graph_url = generate_bar_graph(current_user.payments)   

    # initialize the form
    form = ExpenseForm()

    # find info
    if request.method == 'POST':
        amount = float(request.form['amount'])
        tag = str(request.form.get('tag'))

        # error checks
        if len(tag) < 0:
            flash('Invalid tag', category='error')
        elif amount < 0:
            flash('Invalid amount', category='error')
        else:
            # add new payment
            new_payment = Payment(amount=amount, tag=tag, user_id=current_user.id)
            db.session.add(new_payment)
            db.session.commit()

    # re-total the payments and the graph
    total_payments = sum(payment.amount for payment in current_user.payments)
    graph_url = generate_bar_graph(current_user.payments)                 

    # render the html template
    return render_template('fin/spending.html', user=current_user, form=form, monthly_income=monthly_income, total_payments=total_payments, graph_url=graph_url)

# delete an expense
@views.route('/delete-expense/<int:expense_id>', methods=['post'])
def delete_expense(expense_id):  
    # get the expense
    expense = Expense.query.get(expense_id)
    if expense and expense.user_id == current_user.id:
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted successfully', category='success')

    # go back to home page
    return redirect(url_for('views.add_expense'))

# delete a payment
@views.route('/delete-payment/<int:payment_id>', methods=['POST'])
def delete_payment(payment_id):
    # get the payment
    payment = Payment.query.get(payment_id)
    if payment and payment.user_id == current_user.id:
        db.session.delete(payment)
        db.session.commit()
        flash('Payment deleted successfully!', category='success')

    # go back to spending page
    return redirect(url_for('views.add_payment'))


# stocks page
@views.route('/stocks')
@login_required
def stocks_info():
    # render the html template
    return render_template('fin/stock_prices.html', user=current_user, stock_list=stock_list)

# exchange rates page
@views.route('/exchange-rates')
@login_required
def rates_info():
    # render the html template
    return render_template('fin/exchange_rates.html', user=current_user, rates_list=rates_list)
