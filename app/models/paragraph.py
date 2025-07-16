from flask_sqlalchemy import SQLAlchemy
from app import db


class Paragraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2000))
    image_url = db.Column(db.String(255))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)

