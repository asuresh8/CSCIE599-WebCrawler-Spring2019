import flask
FLASK_NAME = "web_crawler_backend"

def create_app():
    app = flask.Flask(__name__)
    app.secret_key = '\x17!\xa8B\x08o\xd8\xe5\xd6\xd6\xcb9n\xde`2\x8bj=\xb8\xa8J\xa8L'
    return app

app = create_app()

