from flask import Flask, render_template, request
from scripts.script import info_profile, compare_profiles

app = Flask(__name__)

@app.route("/", methods=["GET"])
def raiz():
    return render_template('index.html') 

@app.route("/profile", methods=["GET"])
def write_username():
    return render_template('profile.html')

@app.route("/profile/stats", methods=['POST', 'GET'])
def show_results():
    username = request.form.get('username')
    directors, actors, error = info_profile(username)
    if not error:
        return render_template('stats.html', 
                           username=username,
                           cols_dir = directors.columns.values,
                           cols_act = actors.columns.values, 
                           rows_dir = directors.values.tolist(),
                           rows_act = actors.values.tolist(),
                           zip=zip)
    
    return render_template('profile.html')

@app.route("/compare-profiles", methods=["GET"])
def page_compare_profiles():
    return render_template('compare-profiles.html')

@app.route("/comparison-stats", methods=['POST', 'GET'])
def show_comparison():
    u1 = request.form.get('username1')
    u2 = request.form.get('username2')
    df_score = compare_profiles(u1, u2)
    return render_template('comparison.html',
                           username1 = u1,
                           username2 = u2,
                           cols = df_score.columns.values,
                           rows = df_score.values.tolist(),
                           enumerate=enumerate)

@app.route("/contact", methods=["GET"])
def contact_me():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)