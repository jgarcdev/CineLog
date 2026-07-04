"""
services/collection_service.py — CineLog

Business logic for managing a user's film collection (films they've already watched).
All functions follow the project's verb_to_noun naming convention.
"""

from app import db
from models import Film, CollectionEntry


class FilmNotFoundError(Exception):
  """Raised when a filmId does not exist in the database."""
  pass


class AlreadyInCollectionError(Exception):
  """Raised when a film is already in the user's collection."""
  pass


class NotInCollectionError(Exception):
  """Raised when trying to remove a film that isn't in the collection."""
  pass


def addToCollection(userId, filmId, rating=None):
  """
  Add a film to a user's collection (i.e., mark it as watched).

  Args:
    userId (str): UUID of the user.
    filmId (str): UUID of the film.
    rating (int, optional): Rating from 1-5. May be added later.

  Returns:
    CollectionEntry: The newly created entry.

  Raises:
    FilmNotFoundError: If filmId does not exist.
    AlreadyInCollectionError: If the film is already in the user's collection.
  """
  film = Film.query.get(filmId)
  if film is None: raise FilmNotFoundError(f"No film found with id '{filmId}'")

  existing = CollectionEntry.query.filter_by(userId=userId, filmId=filmId).first()
  if existing: raise AlreadyInCollectionError(f"Film '{filmId}' is already in this user's collection")

  entry = CollectionEntry(userId=userId, filmId=filmId, rating=rating)
  db.session.add(entry)
  db.session.commit()

  return entry


def removeFromCollection(userId, filmId):
  """
  Remove a film from a user's collection.

  Args:
    userId (str): UUID of the user.
    filmId (str): UUID of the film.

  Returns:
    bool: True if the entry was removed.

  Raises:
    NotInCollectionError: If the film is not in the user's collection.
  """
  entry = CollectionEntry.query.filter_by(userId=userId, filmId=filmId).first()
  if entry is None: raise NotInCollectionError(f"Film '{filmId}' is not in this user's collection")

  db.session.delete(entry)
  db.session.commit()

  return True


def getCollection(userId):
  """
  Return all films in a user's collection, sorted by date added (newest first).

  Args:
    userId (str): UUID of the user.

  Returns:
    list[dict]: List of film dicts (not CollectionEntry objects) with the date_added and rating from the entry attached.
  """
  entries = (
    CollectionEntry.query
      .filter_by(userId=userId)
      .order_by(CollectionEntry.dateAdded.desc())
      .all()
  )

  result = []
  for entry in entries:
    filmDict = entry.film.to_dict()
    filmDict["date_added"] = entry.dateAdded.isoformat()
    filmDict["rating"] = entry.rating
    result.append(filmDict)

  return result