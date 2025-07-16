from flask_sqlalchemy import SQLAlchemy
from app import db


class Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
