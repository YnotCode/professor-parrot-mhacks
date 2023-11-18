from flask import Flask
from flask import request, send_file

app = Flask(__name__)

@app.route("/")
def hello_world():
    return send_file("index.html")