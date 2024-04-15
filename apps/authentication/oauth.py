# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import json
import secrets
import string

from flask import flash
from flask_login import current_user, login_user
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
from .models import Users, db, OAuth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

blueprint = make_google_blueprint(
    scope=[
        "openid",
        "https://www.googleapis.com/auth/gmail.labels",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/gmail.readonly"
    ],
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user),
)


def generate_random_password(length=12):
    # Define the character set for the password
    characters = string.ascii_letters + string.digits + string.punctuation + '!$()?=^_;:,.-'

    # Generate a random password by sampling characters from the defined character set
    password = ''.join(secrets.choice(characters) for i in range(length))

    return password


@oauth_authorized.connect_via(blueprint)
def google_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in.", category="error")
        return False

    resp = blueprint.session.get("/oauth2/v1/userinfo")
    if not resp.ok:
        msg = "Failed to fetch user info."
        flash(msg, category="error")
        return False

    info = resp.json()
    user_id = info["id"]

    # Find this OAuth token in the database, or create it
    query = OAuth.query.filter_by(provider=blueprint.name, provider_user_id=user_id)
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(provider=blueprint.name, provider_user_id=user_id, token=token)

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in.")
    else:
        # Create a new local user account for this user
        email = info["email"]
        # Use the part of the email before the "@" symbol as the username
        username = email.split("@")[0]
        password = generate_random_password()  # Set a default password for new users
        user = Users(username=username, email=email, password=password)
        # Associate the new local user account with the OAuth token
        oauth.user = user
        # Save and commit our database models
        db.session.add_all([user, oauth])
        db.session.commit()
        # Log in the new local user account
        login_user(user)
        flash("Successfully signed in.")

    # Disable Flask-Dance's default behavior for saving the OAuth token
    return False


def fetch_email_messages(token):
    email_contents = []
    try:
        # Create credentials object from the token
        creds = credentials.Credentials.from_authorized_user_info(token)

        service = build('gmail', 'v1', credentials=creds)
        # Call the Gmail API to fetch the latest 10 emails
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])

        # Process the fetched emails as needed
        for message in messages:
            message_id = message['id']
            # Fetch the email content using message_id
            email_content = service.users().messages().get(userId='me', id=message_id).execute()
            # Process the email content as needed
            email_contents.append(email_content)
    except HttpError as e:
        print("Gmail API error:", e)
    except Exception as e:
        print("Error:", e)
    return email_contents

# notify on OAuth provider error
@oauth_error.connect_via(blueprint)
def google_error(blueprint, message, response):
    msg = "OAuth error from {name}! " "message={message} response={response}".format(
        name=blueprint.name, message=message, response=response
    )
    flash(msg, category="error")
