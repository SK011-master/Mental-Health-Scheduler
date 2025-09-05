from .extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(128), primary_key=True)  # Descope userId (string)
    email = db.Column(db.String(320), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)