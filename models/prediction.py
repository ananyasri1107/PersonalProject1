from datetime import datetime, timezone

from extensions import db


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    image_filename = db.Column(db.String(255), nullable=False)
    disease_name = db.Column(db.String(150), nullable=False)
    confidence = db.Column(db.Float, nullable=False)  # 0-100
    plant_name = db.Column(db.String(80), nullable=True)
    is_healthy = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Prediction {self.disease_name} ({self.confidence:.1f}%)>"
