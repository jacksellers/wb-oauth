from requests_oauthlib import OAuth2Session
from flask import Flask, render_template, request, redirect, session, url_for
from flask.json import jsonify
import os

app = Flask(__name__)

client_id = '48019a51fbcd7126be7d'
client_secret = 'fda032fe3c826f2074ff369a50c914fee1ee84e5'
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/oauth')
def oauth():
    github = OAuth2Session(client_id)
    authorization_url, state = github.authorization_url(authorization_base_url)
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route("/callback", methods=["GET"])
def callback():
    github = OAuth2Session(client_id, state=session['oauth_state'])
    token = github.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)
    session['oauth_token'] = token
    return redirect(url_for('.profile'))

@app.route("/profile", methods=["GET"])
def profile():
    github = OAuth2Session(client_id, token=session['oauth_token'])
    return jsonify(github.get('https://api.github.com/user').json())

if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
    app.secret_key = os.urandom(24)
    app.run(debug=True)