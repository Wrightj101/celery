import os
from flask import Flask, flash, render_template, redirect, request, jsonify
from tasks import add, elvaco_data_handler
import json
import base64

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

    data_bytes = request.get_data().decode('cp855')

    #bytes_encoded = base64.b64encode(data_bytes)

    #final_bytes_string = bytes_encoded.decode('ascii')

    #elv_sn = request.headers

    content = str(data_bytes)

    #byte_data = request.get_data()

    #json_data = json.loads(str(byte_data, 'cp855'))

    #content = json_data

    #content = request
    #encoded64 = base64.b64encode(request.get_data())

    #content = encoded64.decode('ascii')

    #content = request.get_data().decode('cp855').split('\r\n')
    #content = request.get_data()

    task = elvaco_data_handler.delay(site, content)
    
    return json.dumps({'success':True}), 200

    #return f"Recieved data from {site} on elvaco {elv_sn}",200