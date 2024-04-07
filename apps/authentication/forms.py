# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField
from wtforms.validators import Email, DataRequired


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
