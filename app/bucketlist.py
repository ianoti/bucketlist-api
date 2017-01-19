from flask import Flask

app = Flask(__name__)

@app.route('/index')
def index():
    return "Move along nothing to see voom voom here"


if __name__ == "__main__":
    app.run(debug=True)
