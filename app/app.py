from requests_oauthlib import OAuth2Session
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

client_id = '48019a51fbcd7126be7d'
client_secret = 'fda032fe3c826f2074ff369a50c914fee1ee84e5'
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    image = db.Column(db.String(100))
    github = db.Column(db.String(100))
    email = db.Column(db.String(100))
    bio = db.Column(db.String(1000))

def __init__(self, username, image, github, email, bio):
   self.username = username
   self.image = image
   self.github = github
   self.email = email
   self.bio = bio

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/oauth')
def oauth():
    github = OAuth2Session(client_id)
    authorization_url, state = github.authorization_url(authorization_base_url)
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback', methods=['GET'])
def callback():
    github = OAuth2Session(client_id, state=session['oauth_state'])
    token = github.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)
    session['oauth_token'] = token
    return redirect(url_for('profile'))

@app.route('/profile', methods=['GET'])
def profile():
    if 'oauth_token' in session:
        github = OAuth2Session(client_id, token=session['oauth_token'])
        data = github.get('https://api.github.com/user').json()
        user = User.query.filter_by(username=data['login']).first()
        if not user:
            user = User(
                username=data['login'],
                image=data['avatar_url'],
                github=data['html_url'],
                bio=data['bio']
            )
            db.session.add(user)
            db.session.commit()
        session['user'] = user.id
        return render_template('profile.html', user=user)
    else:
        return redirect(url_for('home'))

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if 'user' in session:
        user = User.query.filter_by(id=session['user']).first()
        if request.method == 'POST':
            user.bio = request.form['bio']
            db.session.commit()
            return redirect(url_for('profile'))
        return render_template('edit.html', user=user)
    else:
        return redirect(url_for('home'))

@app.route('/delete', methods=['GET'])
def delete():
    if 'user' in session:
        User.query.filter_by(id=session['user']).delete()
        db.session.commit()
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    db.create_all()
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.secret_key = os.urandom(24)
    app.run(debug=True)