"""Shared Flask extension instances.

Kept in their own module (instead of app.py or models/__init__.py) so that
both the app factory and the model modules can import them without any
circular-import issues.
"""
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
