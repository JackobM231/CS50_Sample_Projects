
from flask import Flask, render_template, request

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/projects")
def projects():
    return render_template('projects.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/redirect")
def redirect():
    return render_template('redirect.html')

if __name__ == '__main__':
    app.run(debug=True)