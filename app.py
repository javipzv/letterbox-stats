from flask import Flask, render_template, request
from script import info_profile

app = Flask(__name__)

@app.route("/")
def raiz():
    return render_template('index.html') 

@app.route("/results", methods=['POST', 'GET'])
def show_results():
    username = request.form.get('username')
    print(username)
    return render_template('result.html', username=username)

if __name__ == '__main__':
    app.run(debug=True)