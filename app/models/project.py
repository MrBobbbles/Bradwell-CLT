from flask_sqlalchemy import SQLAlchemy
from app import db


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    about = db.Column(db.String(400), nullable=True)
    content = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Project {self.title}>'
    
    paragraphs = db.relationship('Paragraph', backref='project', lazy=True, cascade='all, delete-orphan')
