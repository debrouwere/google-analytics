import os
from flask import Flask, request, redirect, jsonify
import googleanalytics

app = Flask(__name__)

flow = googleanalytics.auth.Flow(
    os.environ['GOOGLE_ANALYTICS_CLIENT_ID'],
    os.environ['GOOGLE_ANALYTICS_CLIENT_SECRET'],
    redirect_uri='http://localhost:5000/auth/google/callback')

@app.route('/auth/google')
def authorization():
    authorize_url = flow.step1_get_authorize_url()
    return redirect(authorize_url)

@app.route('/auth/google/callback')
def callback():
    credentials = flow.step2_exchange(request.args['code'])
    return jsonify(**credentials.serialize())

app.run()
