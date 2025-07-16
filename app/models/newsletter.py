from flask_sqlalchemy import SQLAlchemy
from datetime import date
from app import db


class Newsletter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    date = db.Column(db.Date, default=date.today)
    filepath = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Newsletter {self.name}>'