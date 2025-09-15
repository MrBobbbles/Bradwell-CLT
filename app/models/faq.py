from flask_sqlalchemy import SQLAlchemy
from app import db


class Faq(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    question = db.Column(db.String(1027))
    answer = db.Column(db.String(1027))
    displayed = db.Column(db.Boolean, nullable=False)
    answered = db.Column(db.Boolean, nullable=False)
    
    def __repr__(self):
        return f'<Email {self.email}>'