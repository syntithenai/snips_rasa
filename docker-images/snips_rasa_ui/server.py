#!/opt/rasa/anaconda/bin/python

from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort, send_from_directory
import os
 
app = Flask(__name__)
 
@app.route('/')
def home():
    return render_template('index.html')

# support files
@app.route('/res/<path:path>')
def send_js(path):
    return send_from_directory('res', path) 
 
# save stories
@app.route('/save', methods=['POST'])
def do_save():
    flash('saving!')
    print(request.data)
    return home()
 
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)
