# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import locale
from datetime import datetime, timedelta

from sqlalchemy import func

from apps import db
from apps.authentication.forms import LoginForm, UpdateExpenses
from apps.authentication.models import Users, Expense, Income, Saving
from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound, TemplateError
from flask_wtf import FlaskForm


@blueprint.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        # Handle form submission to update profile information
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        if new_username != current_user.username:
            user = Users.query.filter_by(username=new_username).first()
            if user:
                flash('Нэр давхцаж байна, өөр нэр сонгонуу', 'username_error')
                return render_template('home/profile.html')

        current_user.username = new_username
        if new_email != current_user.email:
            user1 = Users.query.filter_by(email=new_email).first()
            if user1:
                flash('Имэйл давхцаж байна, өөр нэр сонгонуу', 'email_error')
                return render_template('home/profile.html')

        current_user.email = new_email
        # Update the current user's information in the database
        # Replace the following with your actual database update code

        # Assuming you're using SQLAlchemy, you would commit the changes to the database
        db.session.commit()

        # Redirect back to the profile page after updating
        return redirect(url_for('home_blueprint.route_template', template='profile.html'))


@blueprint.route('/update-expenses', methods=['POST'])
@login_required
def update_expenses():
    if request.method == 'POST':
        # Handle form submission to update profile information
        new_expense = request.form.get('expenseAmount')
        new_category = request.form.get('new_category')

        # Create new expense
        expense = Expense(UserID=current_user.id, expenseAmount=new_expense, category=new_category)

        db.session.add(expense)

        db.session.commit()

        return redirect(url_for('home_blueprint.index'))


@blueprint.route('/update-incomes', methods=['POST'])
@login_required
def update_incomes():
    if request.method == 'POST':
        # Handle form submission to update profile information
        new_expense = request.form.get('incomeAmount')
        new_source = request.form.get('new_source')
        # Create new expense
        income = Income(UserID=current_user.id, incomeAmount=new_expense, source=new_source)

        db.session.add(income)

        db.session.commit()

        flash('Expense added successfully', 'success')
        return redirect(url_for('home_blueprint.index'))


@blueprint.route('/update-savings', methods=['POST'])
@login_required
def update_savings():
    if request.method == 'POST':
        # Handle form submission to update profile information
        new_saving = request.form.get('savingAmount')

        # Create new expensesaving
        saving = Saving(UserID=current_user.id, savingAmount=new_saving)
        db.session.add(saving)

        db.session.commit()

        flash('Expense added successfully', 'success')
        return redirect(url_for('home_blueprint.index'))


def total_expense_last_n_days(n_days):
    # Calculate the date n days ago
    start_date = datetime.now() - timedelta(days=n_days)

    # Calculate the sum of expenseAmount for the last n days for the current user
    total_expense = db.session.query(func.sum(Expense.expenseAmount)).filter(
        Expense.UserID == current_user.id,
        Expense.dateSpent >= start_date
    ).scalar()

    # If total_expense_last_n_days is None (no expenses recorded), set it to 0
    total_expense = total_expense or 0

    # Format the total expense amount for the last n days
    formatted_total_expense = locale.format_string("%d", total_expense, grouping=True)
    formatted_total_expense = formatted_total_expense.replace(',', "'")

    return formatted_total_expense


def total_income_last_n_days(n_days):
    # Calculate the date n days ago
    start_date = datetime.now() - timedelta(days=n_days)

    # Calculate the sum of expenseAmount for the last n days for the current user
    total_income = db.session.query(func.sum(Income.incomeAmount)).filter(
        Income.UserID == current_user.id,
        Income.dateReceived >= start_date
    ).scalar()

    # If total_expense_last_n_days is None (no expenses recorded), set it to 0
    total_income = total_income or 0

    # Format the total expense amount for the last n days
    formatted_total_income = locale.format_string("%d", total_income, grouping=True)
    formatted_total_income = formatted_total_income.replace(',', "'")

    return formatted_total_income


def total_saving_last_n_days(n_days):
    # Calculate the date n days ago
    start_date = datetime.now() - timedelta(days=n_days)

    # Calculate the sum of expenseAmount for the last n days for the current user
    total_saving = db.session.query(func.sum(Saving.savingAmount)).filter(
        Saving.UserID == current_user.id,
        Saving.dateSaved >= start_date
    ).scalar()

    # If total_expense_last_n_days is None (no expenses recorded), set it to 0
    total_saving = total_saving or 0

    # Format the total expense amount for the last n days
    formatted_total_saving = locale.format_string("%d", total_saving, grouping=True)
    formatted_total_saving = formatted_total_saving.replace(',', "'")

    return formatted_total_saving


def expense_count_last_n_days(n_days):
    # Calculate the date n days ago
    start_date = datetime.now() - timedelta(days=n_days)

    # Calculate the sum of expenseAmount for the last n days for the current user
    total_expense_count = db.session.query(func.count(Expense.expenseAmount)).filter(
        Expense.UserID == current_user.id,
        Expense.dateSpent >= start_date
    ).scalar()

    # If total_expense_last_n_days is None (no expenses recorded), set it to 0
    total_expense_count = total_expense_count or 0

    return total_expense_count


def income_count_last_n_days(n_days):
    # Calculate the date n days ago
    start_date = datetime.now() - timedelta(days=n_days)

    # Calculate the sum of expenseAmount for the last n days for the current user
    total_income_count = db.session.query(func.count(Income.incomeAmount)).filter(
        Income.UserID == current_user.id,
        Income.dateReceived >= start_date
    ).scalar()

    # If total_expense_last_n_days is None (no expenses recorded), set it to 0
    total_income_count = total_income_count or 0

    return total_income_count


@blueprint.route('/index')
@login_required
def index():
    locale.setlocale(locale.LC_ALL, '')

    expense_categories_label = [{'category': 'Хоол'}, {'category': 'Түрээс'},
                                {'category': 'Лизинг'}]
    income_categories_label = [{'category': 'Цалин'}, {'category': 'Түрээс'},
                               {'category': 'Лизинг'}]
    expense_category_input = request.args.get('expense_category', 'Бусад')
    income_category_input = request.args.get('income_category', 'Бусад')

    periods = [{'label': '1 Өдөр', 'value': '1'}, {'label': '30 Өдөр', 'value': '30'},
               {'label': '365 Өдөр', 'value': '365'}]
    time_period = request.args.get('time_period', '1')

    expense_count = expense_count_last_n_days(int(time_period))

    income_count = income_count_last_n_days(int(time_period))

    expense_category = str(expense_category_input)

    income_category = str(income_category_input)

    # Display total expense
    total_expense_last_1_day = total_expense_last_n_days(1)
    total_expense_last_30_days = total_expense_last_n_days(30)
    total_expense_last_365_days = total_expense_last_n_days(365)

    # Display total income
    total_income_last_1_day = total_income_last_n_days(1)
    total_income_last_30_days = total_income_last_n_days(30)
    total_income_last_365_days = total_income_last_n_days(365)

    # Display total income
    total_saving_last_1_day = total_saving_last_n_days(1)
    total_saving_last_30_days = total_saving_last_n_days(30)
    total_saving_last_365_days = total_saving_last_n_days(365)

    return render_template('home/index.html', segment='index',
                           total_expense_last_1_day=total_expense_last_1_day,
                           total_expense_last_30_days=total_expense_last_30_days,
                           total_expense_last_365_days=total_expense_last_365_days,
                           total_income_last_1_day=total_income_last_1_day,
                           total_income_last_30_days=total_income_last_30_days,
                           total_income_last_365_days=total_income_last_365_days,
                           total_saving_last_1_day=total_saving_last_1_day,
                           total_saving_last_30_days=total_saving_last_30_days,
                           total_saving_last_365_days=total_saving_last_365_days,
                           expense_count=expense_count,
                           income_count=income_count,
                           time_period=time_period,
                           periods=periods,
                           expense_category=expense_category,
                           expense_categories_label=expense_categories_label,
                           income_category=income_category,
                           income_categories_label=income_categories_label
                           )


@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)
        user_data = Users.query.all()
        # Serve the file (if exists) from app/templates/home/FILE.html
        if template == 'tbl_bootstrap.html':
            # Render the profile template with the current user's information
            return render_template("home/tbl_bootstrap.html", segment=segment, current_user=current_user
                                   , user_data=user_data)
        else:
            return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except TemplateError:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
