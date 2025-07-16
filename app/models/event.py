from flask_sqlalchemy import SQLAlchemy
from app import db


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255))
    date = db.Column(db.Date)
    description = db.Column(db.String(1027))
    
    
    def __repr__(self):
        return f'<Event {self.name}>'