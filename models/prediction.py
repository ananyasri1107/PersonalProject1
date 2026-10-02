from extensions import db
from datetime import datetime


class Prediction(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    image_filename = db.Column(
        db.String(255),
        nullable=False
    )

    disease_name = db.Column(
        db.String(150),
        nullable=False
    )

    result = db.Column(
        db.String(50),
        nullable=False
    )

    confidence = db.Column(
        db.Float,
        nullable=False
    )

    treatment = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        back_populates="predictions"
    )
