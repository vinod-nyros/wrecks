import os
from flask import Flask
from flask import Response
from flask import json

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World"

@app.route('/cities.json')
def cities():
    data = ['Amsterdam', 'San Francisco', 'Berlin', 'New York','kakinada','hyderabd','chennai','kolkata']
    resp = Response(json.dumps(data), status=200, mimetype='application/json')
    return resp

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
