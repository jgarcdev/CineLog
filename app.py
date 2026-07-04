"""app.py — CineLog Flask application factory"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def createApp(config=None):
  app = Flask(__name__)
  app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///cinelog.db")
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
  app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

  if config: app.config.update(config)

  db.init_app(app)

  from routes.films import filmsBp
  from routes.collection import collectionBp

  app.register_blueprint(filmsBp, url_prefix="/films")
  app.register_blueprint(collectionBp, url_prefix="/collection")

  with app.app_context():
    db.create_all()

  return app


if __name__ == "__main__":
  app = createApp()
  app.run(debug=True)