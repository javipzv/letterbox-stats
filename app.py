from flask import Flask, render_template, request
from scripts.script import info_profile
import pandas as pd

app = Flask(__name__)

@app.route("/")
def raiz():
    return render_template('index.html') 

@app.route("/results", methods=['POST', 'GET'])
def show_results():
    username = request.form.get('username')
    directors, actors = info_profile(username)
    return render_template('result.html', 
                           username=username,
                           cols_dir = directors.columns.values,
                           cols_act = actors.columns.values, 
                           rows_dir = directors.values.tolist(),
                           rows_act = actors.values.tolist(),
                           zip=zip)

if __name__ == '__main__':
    app.run(debug=True)