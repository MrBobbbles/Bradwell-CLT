from flask_sqlalchemy import SQLAlchemy
from app import db


class Email(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Email {self.email}>'