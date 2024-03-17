# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from flask import request
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, DecimalField
from wtforms.validators import Email, DataRequired, Length, EqualTo, InputRequired

from apps import db
from apps.authentication.models import Users


# login and registration


class LoginForm(FlaskForm):
    username = StringField('Username',
                           id='username_create',
                           validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Нууц үг', validators=[DataRequired()])
    remember = BooleanField('Намайг сана')
    submit = SubmitField('Нэвтрэх')


class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                           id='username_create',
                           validators=[DataRequired()])
    email = StringField('Email',
                        id='email_create',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])


class UpdateExpenses(FlaskForm):

    expenseAmount = DecimalField('Amount', validators=[DataRequired()])

