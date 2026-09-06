from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "MultiBranch Pipeline Application is working!"


@app.route("/health")
def health():
    return "OK"

@app.route("/environment")
def environment():
    return "Staging Environment"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
