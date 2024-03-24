# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import locale
from datetime import datetime, timedelta, date

from sqlalchemy import func

from apps import db
from apps.authentication.forms import LoginForm, UpdateExpenses
from apps.authentication.models import Users, Expense, Income, Saving, Budget
from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound, TemplateError
from decimal import Decimal
from sqlalchemy import not_
from flask_wtf import FlaskForm


@blueprint.route('/update-targetAmount', methods=['POST'])
@login_required
def update_targetAmount():
    if request.method == 'POST':
        # Get the target amount and goal name from the form data
        saving_target = request.form.get('targetAmount')
        new_goal_1 = request.form.get('new_goal_1')

        try:
            existing_goal = Saving.query.filter_by(goalName=new_goal_1).first()

            # If the goal exists, update its target amount
            if existing_goal:
                existing_goal.targetAmount = saving_target
                db.session.commit()
            # If the goal doesn't exist, create a new one
            else:
                saving_target_update = Saving(UserID=current_user.id, targetAmount=saving_target, goalName=new_goal_1,
                                              savingAmount=0)
                db.session.add(saving_target_update)

            # Commit the changes to the database
            db.session.commit()

            return redirect(url_for('home_blueprint.index'))

        # Handle any potential exceptions
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"An error occurred: {str(e)}")
            return redirect(url_for('home_blueprint.index'))

    # Handle other HTTP methods or errors
    return redirect(url_for('home/page-500.html'))


@blueprint.route('/update-savings', methods=['POST'])
@login_required
def update_savings():
    if request.method == 'POST':
        # Handle form submission to update profile information
        new_saving = request.form.get('savingAmount')
        new_goal = request.form.get('new_goal')

        # Create new expensesaving
        try:
            existing_goal = Saving.query.filter_by(goalName=new_goal).first()

            # If the goal exists, update its target amount
            if existing_goal:
                existing_goal.savingAmount += int(new_saving)
            # If the goal doesn't exist, create a new one
            else:
                saving_amount_update = Saving(UserID=current_user.id, savingAmount=new_saving, goalName=new_goal,
                                              targetAmount=0)
                db.session.add(saving_amount_update)

            # Commit the changes to the database
            db.session.commit()

            return redirect(url_for('home_blueprint.index'))

        # Handle any potential exceptions
        except Exception as e:
            # Log the error or handle it appropriately
            print(f"An error occurred: {str(e)}")
            return redirect(url_for('home_blueprint.index'))

    # Handle other HTTP methods or errors
    return redirect(url_for('home/page-500.html'))


@blueprint.route('/update-budget', methods=['POST'])
@login_required
def update_budget():
    if request.method == 'POST':
        # Get the daily and monthly budget limits from the form data
        daily_limit = request.form.get('daily_limit')
        monthly_limit = request.form.get('monthly_limit')

        # Update the current user's budget limits in the database
        budget = Budget(UserID=current_user.id, daily_limit=daily_limit, monthly_limit=monthly_limit)

        db.session.add(budget)
        db.session.commit()

        return redirect(url_for('home_blueprint.index'))

    # Handle other HTTP methods or errors
    return redirect(url_for('home/page-500.html'))


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

    return total_expense


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
    formatted_total_income = formatted_total_income

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
    formatted_total_saving = formatted_total_saving

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
    saving_categories_label = [{'category': 'Гэнэтийн үеийн хадгаламж'}, {'category': 'Байрны хадгаламж'},
                               {'category': 'Автомашины хадгаламж'}]
    expense_category_input = request.args.get('expense_category', 'Бусад')
    income_category_input = request.args.get('income_category', 'Бусад')
    saving_category_input = request.args.get('saving_category', 'Бусад')

    periods = [{'label': '1 Өдөр', 'value': '1'}, {'label': '30 Өдөр', 'value': '30'},
               {'label': '365 Өдөр', 'value': '365'}]
    time_period = request.args.get('time_period', '1')

    expense_count = expense_count_last_n_days(int(time_period))

    income_count = income_count_last_n_days(int(time_period))

    expense_category = str(expense_category_input)
    income_category = str(income_category_input)
    saving_category = str(saving_category_input)

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

    daily_limit = db.session.query(Budget.daily_limit). \
        filter(Budget.UserID == current_user.id). \
        filter(not_(Budget.daily_limit.is_(None))). \
        order_by(Budget.id.desc()). \
        first()
    monthly_limit = db.session.query(Budget.monthly_limit). \
        filter(Budget.UserID == current_user.id). \
        filter(not_(Budget.monthly_limit.is_(None))). \
        order_by(Budget.id.desc()). \
        first()

    if monthly_limit and daily_limit is not None and monthly_limit[0] and monthly_limit[0] is not None:
        daily_limit = Decimal(daily_limit[0])
        monthly_limit = Decimal(monthly_limit[0])
    else:
        daily_limit = Decimal(1)
        monthly_limit = Decimal(1)
    if monthly_limit != 0 or monthly_limit != 0:

        time_period = int(time_period)
        total_expense = total_expense_last_n_days(time_period)

        if time_period == 1:  # Daily limit
            limit = daily_limit
        elif time_period == 30:  # Monthly limit
            limit = monthly_limit
        elif time_period == 365:  # Monthly limit
            limit = monthly_limit
        else:
            raise ValueError("Invalid time period")

        expense_progress = (total_expense / limit) * 100
    else:
        expense_progress = 0

    if total_income_last_n_days != 0:
        time_period = int(time_period)
        total_income = total_income_last_n_days(time_period)
    else:
        pass

    goal_name = request.args.get('selectedGoalName')

    # Query the database for the targetAmount and savingAmount with the specified goalName
    goal_data = Saving.query.filter_by(goalName=goal_name).first()

    # Check if the goal data exists
    if goal_data:
        # Extract targetAmount and savingAmount from the goal_data object
        target_amount = goal_data.targetAmount
        saving_amount = goal_data.savingAmount
    else:
        target_amount = None
        saving_amount = 0

    # Check if both target_amount and saving_amount are not None
    if target_amount is not None and saving_amount is not None:
        # Calculate the percentage completion
        completion_percentage = (saving_amount / target_amount) * 100
    else:
        # Handle the case where either target_amount or saving_amount is None
        completion_percentage = 0

    # Check if monthly_limit_row is not None before accessing its value

    # Calculate monthly progress only if monthly_limit is not 0 to avoid division by zero error

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
                           income_categories_label=income_categories_label,
                           saving_category=saving_category,
                           saving_categories_label=saving_categories_label,
                           daily_limit=daily_limit,
                           monthly_limit=monthly_limit,
                           expense_progress=expense_progress,
                           total_expense=total_expense,
                           total_income=total_income,
                           target_amount=target_amount,
                           saving_amount=saving_amount,
                           completion_percentage=completion_percentage
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
        expenses = db.session.query(
            func.date(Expense.dateSpent).label('expense_date'),
            func.sum(Expense.expenseAmount).label('total_expense'),
            Expense.category.label('expense_category')  # Include the category column
        ).group_by(
            func.date(Expense.dateSpent),
            Expense.category  # Group by category as well
        ).all()  # Fetch all expenses from the database

        expense_chart_data = [{'x': expense.expense_date, 'y': float(expense.total_expense), 'category': expense.expense_category} for
                              expense in
                              expenses]

        incomes = db.session.query(
            func.date(Income.dateReceived).label('income_date'),
            func.sum(Income.incomeAmount).label('total_income'),
            Income.source.label('income_category')                                   # .strftime("%Y-%m-%d")
        ).group_by(
            func.date(Income.dateReceived),
            Income.source
        ).all()  # Fetch all expenses from the database

        income_chart_data = [{'x': income.income_date, 'y': float(income.total_income), 'source': income.income_category} for income
                             in
                             incomes]

        # Serve the file (if exists) from app/templates/home/FILE.html
        if template == 'tbl_bootstrap.html':
            # Render the profile template with the current user's information
            return render_template("home/tbl_bootstrap.html", segment=segment, current_user=current_user
                                   , user_data=user_data)
        elif template == 'chart-morris.html':
            return render_template('home/chart-morris.html', expense_chart_data=expense_chart_data,
                                   income_chart_data=income_chart_data)
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
