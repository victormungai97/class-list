# app/security.py

"""
Here, we shall create an instance of URLSafeTimedSerializer from itsdangerous
which gives us tools to send sensitive data into untrusted environments
(like sending an email confirmation token to an unconfirmed email)
"""

from itsdangerous import URLSafeTimedSerializer
from app import app

ts = URLSafeTimedSerializer(app.config['SECRET_KEY'])
