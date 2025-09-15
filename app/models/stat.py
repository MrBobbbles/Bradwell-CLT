from flask_sqlalchemy import SQLAlchemy
from app import db


class Stat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    value = db.Column(db.String(50))

    def __repr__(self):
        return f'<Text {self.text}>'