# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import export as export
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_login import current_user, login_user
from sqlalchemy.orm.exc import NoResultFound

from apps.config import Config
from .models import Users, db, OAuth

google_blueprint = make_google_blueprint(
    client_id='176358603267-eneir8r4hl41comtr0rn96o18b3m65gk.apps.googleusercontent.com',
    client_secret='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',

    scope=["openid", "email", "profile"],

    storage=SQLAlchemyStorage(
        OAuth,
        db.session,
        user=current_user,
        user_required=False,
    ),

)
import os

@oauth_authorized.connect_via(google_blueprint)
def google_logged_in(blueprint, token):
    info = google.get("/oauth2/v2/userinfo")
    os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'
    if info.ok:
        account_info = info.json()
        email = account_info["email"]

        query = Users.query.filter_by(email=email)
        try:
            user = query.one()
            login_user(user)
        except NoResultFound:
            # Save to db
            user = Users()
            user.email = email
            # You can set other user properties here
            db.session.add(user)
            db.session.commit()
            login_user(user)
