from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite3'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(100))
    github = db.Column(db.String(100))
    email = db.Column(db.String(100))
    bio = db.Column(db.String(1000))

def __init__(self, image, github, email, bio):
   self.image = image
   self.github = github
   self.email = email
   self.bio = bio

db.create_all()