from flask_sqlalchemy import SQLAlchemy
from app import db


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100))
    image_url = db.Column(db.String(512))
    
    def __repr__(self):
        return f'<Person {self.name}>'
    
    infos = db.relationship('Info', backref='Person', lazy=True, cascade='all, delete-orphan')
