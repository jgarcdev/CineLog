"""
services/watchlist_service.py — CineLog (feature/watchlist branch)

Business logic for the watchlist feature.
"""

from app import db
from models import Film, WatchlistEntry
from services.collectionService import FilmNotFoundError


def addToWatchlist(userId, filmId):
  """
  Save a film to a user's watchlist.

  Args:
      user_id (str): UUID of the user.
      film_id (int): ID of the film. (Note: integer — pre-refactor)

  Returns:
      WatchlistEntry: The newly created entry.

  Raises:
      FilmNotFoundError: If film_id does not exist.
  """
  film = db.session.get(Film, filmId)
  if film is None: raise FilmNotFoundError(f"No film found with id '{filmId}'")

  entry = WatchlistEntry(userId=userId, filmId=filmId)
  db.session.add(entry)
  db.session.commit()

  return entry


def getWatchlist(userId):
  """
  Return all films on a user's watchlist.

  Args:
    userId (str): UUID of the user.

  Returns:
    list[dict]: List of film dicts with watchlist metadata attached.
  """
  entries = (
    WatchlistEntry.query
      .filter_by(userId=userId)
      .join(Film)
      .order_by(Film.title.asc())
      .all()
  )

  result = []
  for entry in entries:
    filmDict = entry.film.to_dict()
    filmDict["date_added"] = entry.date_added.isoformat()
    filmDict["public"] = entry.public
    result.append(filmDict)

  return result