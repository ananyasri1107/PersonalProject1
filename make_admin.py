from login import app
from extensions import db
from models import User

email = input("Enter registered email: ").strip().lower()

with app.app_context():

    user = User.query.filter_by(email=email).first()

    if user is None:
        print("User not found.")
        print("Please register this email first.")

    else:
        user.is_admin = True
        db.session.commit()

        print()
        print("================================")
        print("Admin access granted successfully!")
        print("Email:", user.email)
        print("is_admin:", user.is_admin)
        print("================================")