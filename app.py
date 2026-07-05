"""app.py — CineLog Flask application factory"""

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def createApp(config=None):
  app = Flask(__name__)
  app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///cinelog.db")
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
  app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
def createApp(config=None):
  app = Flask(__name__)
  app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///cinelog.db")
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
  app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

  if config: app.config.update(config)
  if config: app.config.update(config)

  db.init_app(app)
  db.init_app(app)

  from routes.films import filmsBp
  from routes.collection import collectionBp
  from routes.watchlist.watchlist import watchlistBp

  app.register_blueprint(filmsBp, url_prefix="/films")
  app.register_blueprint(collectionBp, url_prefix="/collection")
  app.register_blueprint(watchlistBp, url_prefix="/watchlist")

  with app.app_context():
    db.create_all()
  with app.app_context():
    db.create_all()

  return app
  return app


if __name__ == "__main__":
  app = createApp()
  app.run(debug=True)
  app = createApp()
  app.run(debug=True)