import os
import uuid

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from config import Config
from extensions import db, login_manager
from models import User, Prediction, Contact
from tokens import generate_reset_token, verify_reset_token
from mailer import send_reset_email


# =========================================================
# CREATE APP
# =========================================================

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    # Create required folders
    os.makedirs(
        os.path.join(app.instance_path),
        exist_ok=True
    )

    os.makedirs(
        app.config["UPLOAD_FOLDER"],
        exist_ok=True
    )

    # Initialize database
    db.init_app(app)

    # Initialize login manager
    login_manager.init_app(app)

    login_manager.login_view = "login"

    login_manager.login_message = (
        "Please log in to access that page."
    )

    login_manager.login_message_category = "info"

    # Create database tables
    with app.app_context():
        db.create_all()

    # Register routes
    register_routes(app)

    return app


# =========================================================
# ALLOWED FILE
# =========================================================

def allowed_file(filename: str, app: Flask) -> bool:

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in app.config["ALLOWED_EXTENSIONS"]
    )


# =========================================================
# ROUTES
# =========================================================

def register_routes(app: Flask):

    # =====================================================
    # USER LOADER
    # =====================================================

    @login_manager.user_loader
    def load_user(user_id):

        return db.session.get(
            User,
            int(user_id)
        )


    # =====================================================
    # HOME
    # =====================================================

    @app.route("/")
    def home():

        return render_template("home.html")


    # =====================================================
    # REGISTER / ACCOUNT
    # =====================================================

    @app.route("/account", methods=["GET", "POST"])
    def account():

        if current_user.is_authenticated:
            return redirect(
                url_for("dashboard")
            )

        if request.method == "POST":

            full_name = request.form.get(
                "name",
                ""
            ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip().lower()

            password = request.form.get(
                "password",
                ""
            )

            confirm_password = request.form.get(
                "confirmPassword",
                ""
            )

            error = None

            if not full_name or not email or not password:

                error = "Please fill in all fields."

            elif password != confirm_password:

                error = "Passwords do not match."

            elif len(password) < 8:

                error = (
                    "Password must be at least 8 characters long."
                )

            elif User.query.filter_by(
                email=email
            ).first():

                error = (
                    "An account with that email already exists."
                )

            if error:

                flash(
                    error,
                    "error"
                )

                return render_template(
                    "account.html",
                    name=full_name,
                    email=email
                )

            user = User(
                full_name=full_name,
                email=email
            )

            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            login_user(user)

            flash(
                f"Welcome to PlantAI, {user.full_name}!",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        return render_template(
            "account.html"
        )


    # =====================================================
    # LOGIN
    # =====================================================

    @app.route("/login", methods=["GET", "POST"])
    def login():

        if current_user.is_authenticated:

            return redirect(
                url_for("dashboard")
            )

        if request.method == "POST":

            email = request.form.get(
                "email",
                ""
            ).strip().lower()

            password = request.form.get(
                "password",
                ""
            )

            user = User.query.filter_by(
                email=email
            ).first()

            if user is None or not user.check_password(password):

                flash(
                    "Invalid email or password.",
                    "error"
                )

                return render_template(
                    "login.html",
                    email=email
                )

            login_user(
                user,
                remember=bool(
                    request.form.get("remember")
                )
            )

            flash(
                f"Welcome back, {user.full_name}!",
                "success"
            )

            next_page = request.args.get("next")

            return redirect(
                next_page or url_for("dashboard")
            )

        return render_template(
            "login.html"
        )


    # =====================================================
    # FORGOT PASSWORD
    # =====================================================

    @app.route(
        "/forgot-password",
        methods=["GET", "POST"]
    )
    def forgot_password():

        if current_user.is_authenticated:

            return redirect(
                url_for("dashboard")
            )

        if request.method == "POST":

            email = request.form.get(
                "email",
                ""
            ).strip().lower()

            user = User.query.filter_by(
                email=email
            ).first()

            if user and not user.is_guest:

                token = generate_reset_token(
                    user.email
                )

                reset_url = url_for(
                    "reset_password",
                    token=token,
                    _external=True
                )

                send_reset_email(
                    user.email,
                    reset_url
                )

            flash(
                "If an account exists for that email, "
                "a password reset link has been sent.",
                "info"
            )

            return redirect(
                url_for("login")
            )

        return render_template(
            "forgot_password.html"
        )


    # =====================================================
    # RESET PASSWORD
    # =====================================================

    @app.route(
        "/reset-password/<token>",
        methods=["GET", "POST"]
    )
    def reset_password(token):

        if current_user.is_authenticated:

            return redirect(
                url_for("dashboard")
            )

        email = verify_reset_token(
            token
        )

        if email is None:

            flash(
                "That reset link is invalid or has expired. "
                "Please request a new one.",
                "error"
            )

            return redirect(
                url_for("forgot_password")
            )

        user = User.query.filter_by(
            email=email
        ).first()

        if user is None or user.is_guest:

            flash(
                "That reset link is invalid.",
                "error"
            )

            return redirect(
                url_for("forgot_password")
            )

        if request.method == "POST":

            password = request.form.get(
                "password",
                ""
            )

            confirm_password = request.form.get(
                "confirmPassword",
                ""
            )

            if len(password) < 8:

                flash(
                    "Password must be at least 8 characters long.",
                    "error"
                )

                return render_template(
                    "reset_password.html",
                    token=token
                )

            if password != confirm_password:

                flash(
                    "Passwords do not match.",
                    "error"
                )

                return render_template(
                    "reset_password.html",
                    token=token
                )

            user.set_password(
                password
            )

            db.session.commit()

            flash(
                "Your password has been reset. Please log in.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        return render_template(
            "reset_password.html",
            token=token
        )


    # =====================================================
    # GUEST LOGIN
    # =====================================================

    @app.route("/guest")
    def guest_login():

        if current_user.is_authenticated:

            return redirect(
                url_for("dashboard")
            )

        guest = User(
            full_name="Guest",
            email=(
                f"guest_{uuid.uuid4().hex[:10]}"
                "@guest.local"
            ),
            is_guest=True
        )

        guest.set_password(
            uuid.uuid4().hex
        )

        db.session.add(guest)
        db.session.commit()

        login_user(
            guest
        )

        flash(
            "You're browsing as a guest. "
            "Create an account to save your scan history.",
            "info"
        )

        return redirect(
            url_for("dashboard")
        )


    # =====================================================
    # LOGOUT
    # =====================================================

    @app.route("/logout")
    @login_required
    def logout():

        logout_user()

        flash(
            "You have been logged out.",
            "info"
        )

        return redirect(
            url_for("home")
        )


    # =====================================================
    # DASHBOARD
    # =====================================================

    @app.route("/dashboard")
    @login_required
    def dashboard():

        predictions = (
            Prediction.query
            .filter_by(
                user_id=current_user.id
            )
            .order_by(
                Prediction.created_at.desc()
            )
            .limit(12)
            .all()
        )

        total_predictions = (
            Prediction.query
            .filter_by(
                user_id=current_user.id
            )
            .count()
        )

        healthy_count = (
            Prediction.query
            .filter_by(
                user_id=current_user.id,
                is_healthy=True
            )
            .count()
        )

        diseased_count = (
            Prediction.query
            .filter_by(
                user_id=current_user.id,
                is_healthy=False
            )
            .count()
        )

        return render_template(
            "dashboard.html",
            predictions=predictions,
            total_predictions=total_predictions,
            healthy_count=healthy_count,
            diseased_count=diseased_count
        )


    # =====================================================
    # PREDICT
    # =====================================================

    @app.route(
        "/predict",
        methods=["POST"]
    )
    @login_required
    def predict():

        from dl.predict import (
            predict_image,
            ModelNotTrainedError
        )

        file = request.files.get(
            "leaf_image"
        )

        if file is None or file.filename == "":

            flash(
                "Please choose an image to upload.",
                "error"
            )

            return redirect(
                url_for("dashboard")
            )

        if not allowed_file(
            file.filename,
            app
        ):

            flash(
                "Unsupported file type. "
                "Please upload a PNG or JPG image.",
                "error"
            )

            return redirect(
                url_for("dashboard")
            )

        filename = (
            f"{uuid.uuid4().hex}_{file.filename}"
        )

        save_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(
            save_path
        )

        try:

            result = predict_image(
                save_path
            )

        except ModelNotTrainedError:

            flash(
                "The AI model hasn't been trained yet. "
                "Run 'python dl/train.py --data_dir <dataset>' "
                "on the server first, then try again.",
                "error"
            )

            return redirect(
                url_for("dashboard")
            )

        except Exception as exc:

            flash(
                f"Could not analyze that image: {exc}",
                "error"
            )

            return redirect(
                url_for("dashboard")
            )

        record = Prediction(
            user_id=current_user.id,
            image_filename=filename,
            disease_name=result["class_name"],
            confidence=result["confidence"],
            plant_name=result["plant_name"],
            is_healthy=result["is_healthy"]
        )

        db.session.add(
            record
        )

        db.session.commit()

        history = (
            Prediction.query
            .filter_by(
                user_id=current_user.id
            )
            .order_by(
                Prediction.created_at.desc()
            )
            .limit(12)
            .all()
        )

        return render_template(
            "dashboard.html",
            result=result,
            history=history,
            uploaded_filename=filename
        )
    # =====================================================
    # SCAN HISTORY
    # =====================================================
    @app.route('/scan-history')
    @login_required
    def scan_history():

        predictions = Prediction.query.filter_by(
            user_id=current_user.id
        ).order_by(
            Prediction.created_at.desc()
        ).all()

        return render_template(
            'scan_history.html',
            predictions=predictions
        )

    # =====================================================
    # CONTACT PAGE
    # =====================================================

    @app.route(
        "/contact",
        methods=["GET"]
    )
    @login_required
    def contact_page():

        return render_template(
            "contact.html"
        )


    # =====================================================
    # CONTACT FORM SUBMIT
    # =====================================================

    @app.route(
        "/contact/send",
        methods=["POST"]
    )
    @login_required
    def contact():

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()

        if not name or not email or not subject or not message:

            flash(
                "Please fill all contact fields.",
                "error"
            )

            return redirect(
                url_for("contact_page")
            )

        try:

            contact_message = Contact(
                name=name,
                email=email,
                subject=subject,
                message=message
            )

            db.session.add(
                contact_message
            )

            db.session.commit()

            flash(
                "Your message has been sent successfully.",
                "success"
            )

        except Exception as exc:

            db.session.rollback()

            flash(
                f"Could not send message: {exc}",
                "error"
            )

        return redirect(
            url_for("contact_page")
        )


    # =====================================================
    # ADMIN PANEL
    # =====================================================

    @app.route(
        "/adminpanel"
    )
    @login_required
    def admin_panel():

        if not current_user.is_admin:

            abort(403)

        users = (
            User.query
            .filter_by(
                is_guest=False
            )
            .order_by(
                User.created_at.desc()
            )
            .all()
        )

        total_users = len(
            users
        )

        total_predictions = (
            Prediction.query.count()
        )

        return render_template(
            "admin.html",
            users=users,
            total_users=total_users,
            total_predictions=total_predictions
        )


    # =====================================================
    # 404 ERROR
    # =====================================================

    @app.errorhandler(404)
    def not_found(_e):

        return render_template(
            "error.html",
            code=404,
            message="Page not found."
        ), 404


    # =====================================================
    # 403 ERROR
    # =====================================================

    @app.errorhandler(403)
    def forbidden(_e):

        return render_template(
            "error.html",
            code=403,
            message="You don't have access to that page."
        ), 403


# =========================================================
# RUN APPLICATION
# =========================================================

app = create_app()


if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )