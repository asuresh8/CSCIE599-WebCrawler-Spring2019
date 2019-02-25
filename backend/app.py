from app_configure import app
import flask

@app.route('/')
def main():
    return flask.render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8001)