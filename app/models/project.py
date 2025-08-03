from flask_sqlalchemy import SQLAlchemy
from app import db


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    about = db.Column(db.String(400), nullable=True)
    content = db.Column(db.Text)
    finished = db.Column(db.Boolean, nullable = False)
    image_url = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<Project {self.title}>'
    
