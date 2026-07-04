"""
models.py — CineLog

SQLAlchemy models. Film IDs use UUIDs throughout.
(This is the post-refactor state on main — integer IDs were migrated to UUIDs.)
"""

import uuid
from datetime import datetime, timezone
from app import db


def generateUuid(): return str(uuid.uuid4())


class User(db.Model):
  id = db.Column(db.String(36), primary_key=True, default=generateUuid)
  username = db.Column(db.String(64), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  createdAt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

  collectionEntries = db.relationship("CollectionEntry", backref="user", lazy=True)

  def to_dict(self):
    return {"id": self.id, "username": self.username, "email": self.email}


class Film(db.Model):
  # Film IDs are UUIDs — refactored from integer in commit:
  # "refactor: migrate film IDs from integer to UUID"
  id = db.Column(db.String(36), primary_key=True, default=generateUuid)
  title = db.Column(db.String(200), nullable=False)
  year = db.Column(db.Integer, nullable=True)
  director = db.Column(db.String(200), nullable=True)
  genre = db.Column(db.String(100), nullable=True)
  posterUrl = db.Column(db.String(500), nullable=True)
  averageRating = db.Column(db.Float, default=0.0)

  collectionEntries = db.relationship("CollectionEntry", backref="film", lazy=True)

  def to_dict(self):
    return {
      "id": self.id,
      "title": self.title,
      "year": self.year,
      "director": self.director,
      "genre": self.genre,
      "poster_url": self.posterUrl,
      "average_rating": self.averageRating,
    }


class CollectionEntry(db.Model):
  """Represents a film a user has already watched and logged."""
  id = db.Column(db.String(36), primary_key=True, default=generateUuid)
  userId = db.Column(db.String(36), db.ForeignKey("user.id"), nullable=False)
  filmId = db.Column(db.String(36), db.ForeignKey("film.id"), nullable=False)
  dateAdded = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
  rating = db.Column(db.Integer, nullable=True)  # 1–5, optional

  __table_args__ = (db.UniqueConstraint("userId", "filmId", name="unique_user_film_collection"),)

  def to_dict(self):
    return {
      "id": self.id,
      "user_id": self.userId,
      "film_id": self.filmId,
      "date_added": self.dateAdded.isoformat(),
      "rating": self.rating,
    }