import os
import uuid

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, abort, send_from_directory
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)

from config import Config
from extensions import db, login_manager
from models import User, Prediction


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(os.path.join(app.instance_path), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Please log in to access that page."
    login_manager.login_message_category = "info"

    with app.app_context():
        db.create_all()

    register_routes(app)
    return app


def allowed_file(filename: str, app: Flask) -> bool:
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


def register_routes(app: Flask):

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ---------------------------------------------------------------- HOME
   
    
    @app.route("/")
    def home():
        return render_template("home.html")
    
# ---------------------------------------------------------------- TEST

    @app.route("/test")
    def test():
        return "PlantAI Flask Backend is Working!"

    # ------------------------------------------------------------- REGISTER
    @app.route("/account", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            full_name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirmPassword", "")

            error = None
            if not full_name or not email or not password:
                error = "Please fill in all fields."
            elif password != confirm_password:
                error = "Passwords do not match."
            elif len(password) < 8:
                error = "Password must be at least 8 characters long."
            elif User.query.filter_by(email=email).first():
                error = "An account with that email already exists."

            if error:
                flash(error, "error")
                return render_template("account.html", name=full_name, email=email)

            user = User(full_name=full_name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash(f"Welcome to PlantAI, {user.full_name}!", "success")
            return redirect(url_for("dashboard"))

        return render_template("account.html")

    # ---------------------------------------------------------------- LOGIN
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            user = User.query.filter_by(email=email).first()

            if user is None or not user.check_password(password):
                flash("Invalid email or password.", "error")
                return render_template("login.html", email=email)

            login_user(user, remember=bool(request.form.get("remember")))
            flash(f"Welcome back, {user.full_name}!", "success")

            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))

        return render_template("login.html")

    # ----------------------------------------------------------------- GUEST
    @app.route("/guest")
    def guest_login():
        """
        Create a throwaway guest account so visitors can try the detector
        without registering. Guest accounts are plainly marked in the DB
        and are excluded from the admin user list.
        """
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        guest = User(
            full_name="Guest",
            email=f"guest_{uuid.uuid4().hex[:10]}@guest.local",
            is_guest=True,
        )
        guest.set_password(uuid.uuid4().hex)  # random, never shared with anyone
        db.session.add(guest)
        db.session.commit()

        login_user(guest)
        flash("You're browsing as a guest. Create an account to save your scan history.", "info")
        return redirect(url_for("dashboard"))

    # --------------------------------------------------------------- LOGOUT
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("home"))

    # ------------------------------------------------------------- DASHBOARD
    @app.route("/dashboard")
    @login_required
    def dashboard():
        history = (
            Prediction.query
            .filter_by(user_id=current_user.id)
            .order_by(Prediction.created_at.desc())
            .limit(12)
            .all()
        )
        return render_template("dashboard.html", history=history)

    # --------------------------------------------------------------- PREDICT
    @app.route("/predict", methods=["POST"])
    @login_required
    def predict():
        from dl.predict import predict_image, ModelNotTrainedError

        file = request.files.get("leaf_image")

        if file is None or file.filename == "":
            flash("Please choose an image to upload.", "error")
            return redirect(url_for("dashboard"))

        if not allowed_file(file.filename, app):
            flash("Unsupported file type. Please upload a PNG or JPG image.", "error")
            return redirect(url_for("dashboard"))

        filename = f"{uuid.uuid4().hex}_{file.filename}"
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        try:
            result = predict_image(save_path)
        except ModelNotTrainedError:
            flash(
                "The AI model hasn't been trained yet. Run "
                "'python dl/train.py --data_dir <dataset>' on the server first, "
                "then try again.",
                "error",
            )
            return redirect(url_for("dashboard"))
        except Exception as exc:  # noqa: BLE001 - surface any inference error to the user
            flash(f"Could not analyze that image: {exc}", "error")
            return redirect(url_for("dashboard"))

        record = Prediction(
            user_id=current_user.id,
            image_filename=filename,
            disease_name=result["class_name"],
            confidence=result["confidence"],
            plant_name=result["plant_name"],
            is_healthy=result["is_healthy"],
        )
        db.session.add(record)
        db.session.commit()

        history = (
            Prediction.query
            .filter_by(user_id=current_user.id)
            .order_by(Prediction.created_at.desc())
            .limit(12)
            .all()
        )
        return render_template("dashboard.html", result=result, history=history, uploaded_filename=filename)

    # ---------------------------------------------------------------- ADMIN
    @app.route("/adminpanel")
    @login_required
    def admin_panel():
        if not current_user.is_admin:
            abort(403)
        users = User.query.filter_by(is_guest=False).order_by(User.created_at.desc()).all()
        total_predictions = Prediction.query.count()
        return render_template("admin.html", users=users, total_predictions=total_predictions)

    # -------------------------------------------------------------- 404/403
    @app.errorhandler(404)
    def not_found(_e):
        return render_template("error.html", code=404, message="Page not found."), 404

    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("error.html", code=403, message="You don't have access to that page."), 403


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
