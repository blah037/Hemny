# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy.exc import SQLAlchemyError

from sqlalchemy.orm import relationship
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin

from apps import db, login_manager
from datetime import datetime
import pytz as pytz
from apps.authentication.util import hash_pass


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    incomes = db.relationship('Income', backref='owner', lazy=True)
    expenses = db.relationship('Expense', backref='owner', lazy=True)
    savings = db.relationship('Saving', backref='owner', lazy=True)
    budgets = db.relationship('Budget', backref='owner', lazy=True)

    def __init__(self, **kwargs):
        for property1, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack its value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property1 == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property1, value)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('Users', backref='user_budgets', lazy=True)
    daily_limit = db.Column(db.DECIMAL(10, 2), nullable=True)
    monthly_limit = db.Column(db.DECIMAL(10, 2), nullable=True)

    def __repr__(self):
        return f"Budget(ID: {self.id}, User: {self.UserID}," \
               f" Daily Limit: {self.daily_limit}, Monthly Limit: {self.monthly_limit})"


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    source = db.Column(db.String(255), nullable=True)
    incomeAmount = db.Column(db.DECIMAL(10, 2), nullable=False)
    current_time = datetime.now(pytz.timezone('Asia/Shanghai'))
    current_time = current_time.replace(microsecond=0)
    dateReceived = db.Column(db.DateTime, nullable=False, default=current_time)

    def __repr__(self):
        return f"Income(ID: {self.id}, Source: {self.source}," \
               f" Amount: {self.incomeAmount}, DateReceived: {self.dateReceived})"


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(255), nullable=True)
    expenseAmount = db.Column(db.DECIMAL(10, 2), nullable=False)
    current_time = datetime.now(pytz.timezone('Asia/Shanghai'))
    current_time = current_time.replace(microsecond=0)
    dateSpent = db.Column(db.DateTime, nullable=False, default=current_time)

    def __repr__(self):
        return f"Expense(ID: {self.id}, Category: {self.category}," \
               f" Amount: {self.expenseAmount}, DateSpent: {self.dateSpent})"

class Saving(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goalName = db.Column(db.String(255), nullable=True)
    targetAmount = db.Column(db.DECIMAL(10, 2), nullable=True)
    savingAmount = db.Column(db.DECIMAL(10, 2), nullable=True)
    dateSaved = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Shanghai')))
    deadline = db.Column(db.DateTime, nullable=True, default=None)

    def __repr__(self):
        return f"Saving(ID: {self.id}, GoalName: {self.GoalName}," \
               f" TargetAmount: {self.TargetAmount}, Deadline: {self.Deadline})"

    @classmethod
    def find_by_email(cls, email: str) -> "Users":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_username(cls, username: str) -> "Users":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "Users":
        return cls.query.filter_by(id=_id).first()

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()

        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)

    def delete_from_db(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
        return


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="cascade"), nullable=False)
    user = db.relationship(Users)
