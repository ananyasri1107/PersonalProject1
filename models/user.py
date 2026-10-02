predictions = db.relationship(
    "Prediction",
    back_populates="user",
    cascade="all, delete-orphan"
)