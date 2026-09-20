import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:

    # Flask Secret Key
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "dev-secret-key-change-me"
    )

    # SQLite Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'plantai.db')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload Settings
    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "static",
        "uploads"
    )

    ALLOWED_EXTENSIONS = {
        "png",
        "jpg",
        "jpeg",
        "webp"
    }

    # Maximum image size = 8 MB
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024

    # Deep Learning Model
    MODEL_PATH = os.path.join(
        BASE_DIR,
        "dl",
        "saved_model",
        "plant_disease_model.h5"
    )

    # Class names/indexes
    CLASS_INDEX_PATH = os.path.join(
        BASE_DIR,
        "dl",
        "saved_model",
        "class_indices.json"
    )

    # Input image size for CNN
    IMG_SIZE = (224, 224)