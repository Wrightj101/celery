import os
from flask import Flask, flash, render_template, redirect, request
from tasks import add, elvaco_data_handler

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', "super-secret")


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/add', methods=['POST'])
def add_inputs():
    x = int(request.form['x'] or 0)
    y = int(request.form['y'] or 0)
    add.delay(x, y)
    flash("Your addition job has been submitted.")
    return redirect('/')


@app.route('/elvacorender/<site>', methods=['POST'])
def parse_elvaco_data(site):

    content = request.get_data().decode('cp855').split('\r\n')

    task = elvaco_data_handler.delay(site, content)

    return 202