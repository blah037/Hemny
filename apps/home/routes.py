# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import locale
from datetime import datetime, timedelta
from decimal import Decimal

import requests
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound, TemplateError
from sqlalchemy import func
from sqlalchemy import not_

from apps import db
from apps.authentication.models import Users, Expense, Income, Saving, Budget
from apps.home import blueprint

url = 'https://v6.exchangerate-api.com/v6/3aac6de693162f270b16a70b/pair/'


@blueprint.route("/currency_converter", methods=["GET", "POST"])
@login_required
def currency_converter():
    if request.method == "POST":
        first_currency = request.form.get("first_currency")
        second_currency = request.form.get("second_currency")
        amount = request.form.get("amount")

        # Construct URL with selected currencies
        selected_url = f'{url}/{first_currency}/{second_currency}'

        # Get exchange rates
        response = requests.get(selected_url)
        response.raise_for_status()  # raises exception when not a 2xx response

        # Parse the JSON response and extract the conversion_rate
        data = response.json()
        conversion_rate = data.get("conversion_rate")

        if conversion_rate is not None:
            # Calculate the converted amount
            amount = float(amount)
            result = float(amount) * conversion_rate
            currency_info = {
                "first_currency": first_currency,
                "second_currency": second_currency,
                "amount": amount,
                "result": result,
                "conversion_rate": conversion_rate  # Include conversion_rate in the info dictionary
            }

            return render_template("home/currency_converter.html", info=currency_info)
        else:
            error_message = "Error fetching conversion rate from the API. Please try again later."
            return render_template("currency_converter.html", error=error_message)

    return render_template("currency_converter.html")


@blueprint.route('/update-targetAmount', methods=['POST'])
@login_required
def update_targetAmount():
    if request.method == 'POST':
        saving_target = request.form.get('targetAmount')
        new_goal_1 = request.form.get('new_goal_1')

        try:
            existing_goal = Saving.query.filter_by(goalName=new_goal_1, UserID=current_user.id).first()

            if existing_goal:
                existing_goal.targetAmount = saving_target
                db.session.commit()
            else:
                saving_target_update = Saving(UserID=current_user.id, targetAmount=saving_target, goalName=new_goal_1,
                                              savingAmount=0)
                db.session.add(saving_target_update)

            db.session.commit()

            return redirect(url_for('home_blueprint.index'))

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return redirect(url_for('home_blueprint.index'))

    return redirect(url_for('home/page-500.html'))


@blueprint.route('/update-savings', methods=['POST'])
@login_required
def update_savings():
    if request.method == 'POST':
        new_saving = request.form.get('savingAmount')
        new_goal = request.form.get('new_goal')

        try:
            existing_goal = Saving.query.filter_by(goalName=new_goal, UserID=current_user.id).first()

            if existing_goal:
                existing_goal.savingAmount += int(new_saving)
            else:
                saving_amount_update = Saving(UserID=current_user.id, savingAmount=new_saving, goalName=new_goal,
                                              targetAmount=0)
                db.session.add(saving_amount_update)

            db.session.commit()

            return redirect(url_for('home_blueprint.index'))

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return redirect(url_for('home_blueprint.index'))

    return redirect(url_for('home/page-500.html'))


@blueprint.route('/update-budget', methods=['POST'])
@login_required
def update_budget():
    if request.method == 'POST':
        daily_limit = request.form.get('daily_limit')
        monthly_limit = request.form.get('monthly_limit')

        budget = Budget(UserID=current_user.id, daily_limit=daily_limit, monthly_limit=monthly_limit)

        db.session.add(budget)
        db.session.commit()

        return redirect(url_for('home_blueprint.index'))

    return redirect(url_for('home/page-500.html'))


@blueprint.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    if request.method == 'POST':
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

        db.session.commit()

        return redirect(url_for('home_blueprint.route_template', template='profile.html'))


@blueprint.route('/update-expenses', methods=['POST'])
@login_required
def update_expenses():
    if request.method == 'POST':
        new_expense = request.form.get('expenseAmount')
        new_category = request.form.get('new_category')

        expense = Expense(UserID=current_user.id, expenseAmount=new_expense, category=new_category)

        db.session.add(expense)

        db.session.commit()

        return redirect(url_for('home_blueprint.index'))


@blueprint.route('/update-incomes', methods=['POST'])
@login_required
def update_incomes():
    if request.method == 'POST':
        new_expense = request.form.get('incomeAmount')
        new_source = request.form.get('new_source')
        income = Income(UserID=current_user.id, incomeAmount=new_expense, source=new_source)

        db.session.add(income)

        db.session.commit()

        flash('Expense added successfully', 'success')
        return redirect(url_for('home_blueprint.index'))


def total_expense_last_n_days(n_days):
    start_date = datetime.now() - timedelta(days=n_days)

    total_expense = db.session.query(func.sum(Expense.expenseAmount)).filter(
        Expense.UserID == current_user.id,
        Expense.dateSpent >= start_date
    ).scalar()

    total_expense = total_expense or 0

    return total_expense


def total_income_last_n_days(n_days):
    start_date = datetime.now() - timedelta(days=n_days)

    total_income = db.session.query(func.sum(Income.incomeAmount)).filter(
        Income.UserID == current_user.id,
        Income.dateReceived >= start_date
    ).scalar()

    total_income = total_income or 0

    formatted_total_income = total_income

    return formatted_total_income


def total_saving_last_n_days(n_days):
    start_date = datetime.now() - timedelta(days=n_days)

    total_saving = db.session.query(func.sum(Saving.savingAmount)).filter(
        Saving.UserID == current_user.id,
        Saving.dateSaved >= start_date
    ).scalar()

    total_saving = total_saving or 0

    formatted_total_saving = total_saving

    return formatted_total_saving


def expense_count_last_n_days(n_days):
    start_date = datetime.now() - timedelta(days=n_days)

    total_expense_count = db.session.query(func.count(Expense.expenseAmount)).filter(
        Expense.UserID == current_user.id,
        Expense.dateSpent >= start_date
    ).scalar()

    total_expense_count = total_expense_count or 0

    return total_expense_count


def income_count_last_n_days(n_days):
    start_date = datetime.now() - timedelta(days=n_days)

    total_income_count = db.session.query(func.count(Income.incomeAmount)).filter(
        Income.UserID == current_user.id,
        Income.dateReceived >= start_date
    ).scalar()

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

    # Display total expense n day
    total_expense_last_1_day = total_expense_last_n_days(1)
    total_expense_last_30_days = total_expense_last_n_days(30)
    total_expense_last_365_days = total_expense_last_n_days(365)

    # Display total income n day
    total_income_last_1_day = total_income_last_n_days(1)
    total_income_last_30_days = total_income_last_n_days(30)
    total_income_last_365_days = total_income_last_n_days(365)

    # Display total saving n day
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

        if time_period == 1:
            limit = daily_limit
        elif time_period == 30:  #
            limit = monthly_limit
        elif time_period == 365:
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

    current_user_id = current_user.id

    goal_name = request.args.get('selectedGoalName')

    goal_data = Saving.query.filter_by(goalName=goal_name, UserID=current_user_id).first()

    if goal_data:
        target_amount = goal_data.targetAmount
        saving_amount = goal_data.savingAmount
    else:
        target_amount = None
        saving_amount = 0

    if target_amount is not None and saving_amount is not None:
        completion_percentage = (saving_amount / target_amount) * 100
    else:
        completion_percentage = 0

    if saving_amount is not None:
        formatted_saving_amount = '{:,.0f}'.format(saving_amount) + '₮'
    else:
        formatted_saving_amount = '0₮'

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
                           completion_percentage=completion_percentage,
                           formatted_saving_amount=formatted_saving_amount
                           )


@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'

        segment = get_segment(request)
        user_data = Users.query.filter_by(id=current_user.id).all()
        expenses = db.session.query(
            func.date(Expense.dateSpent).label('expense_date'),
            func.sum(Expense.expenseAmount).label('total_expense'),
            Expense.category.label('expense_category')
        ).filter(
            Expense.UserID == current_user.id
        ).group_by(
            func.date(Expense.dateSpent),
            Expense.category
        ).all()

        expense_chart_data = [
            {'x': expense.expense_date, 'y': float(expense.total_expense), 'category': expense.expense_category} for
            expense in
            expenses]

        incomes = db.session.query(
            func.date(Income.dateReceived).label('income_date'),
            func.sum(Income.incomeAmount).label('total_income'),
            Income.source.label('income_category')  # .strftime("%Y-%m-%d")
        ).filter(
            Income.UserID == current_user.id
        ).group_by(
            func.date(Income.dateReceived),
            Income.source
        ).all()

        income_chart_data = [
            {'x': income.income_date, 'y': float(income.total_income), 'source': income.income_category} for income
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


# Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
