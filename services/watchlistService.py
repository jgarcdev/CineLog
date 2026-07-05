"""
services/watchlist_service.py — CineLog (feature/watchlist branch)

Business logic for the watchlist feature.
"""

from typing import Any

from app import db
from models import Film, WatchlistEntry
from services.collectionService import FilmNotFoundError


class AlreadyInWatchlistError(Exception):
  """Raised when a film is already in the user's watchlist."""
  pass

def addToWatchlist(userId:str, filmId:int) -> WatchlistEntry:
  """
  Save a film to a user's watchlist.

  Args:
    userId (str): UUID of the user.
    filmId (int): ID of the film. (Note: integer — pre-refactor)

  Returns:
    WatchlistEntry: The newly created entry.

  Raises:
    FilmNotFoundError: If filmId does not exist.
  """
  film = db.session.get(Film, filmId)
  if film is None: raise FilmNotFoundError(f"No film found with id '{filmId}'")

  # Check if the film is already in the watchlist
  existing = WatchlistEntry.query.filter_by(userId=userId, filmId=filmId).first()
  if existing: raise AlreadyInWatchlistError(f"Film with id '{filmId}' is already in the watchlist for user '{userId}'")

  entry = WatchlistEntry(userId=userId, filmId=filmId)
  db.session.add(entry)
  db.session.commit()

  return entry


def getWatchlist(userId:str) -> list[dict[str, Any]]:
  """
  Return all films on a user's watchlist.

  Args:
    userId (str): UUID of the user.

  Returns:
    list[dict]: List of film dicts with watchlist metadata attached.
  """
  entries:list[WatchlistEntry] = (
    WatchlistEntry.query
      .filter_by(userId=userId)
      .join(Film)
      .order_by(Film.title.asc())
      .all()
  )

  result:list[dict[str, Any]] = []
  for entry in entries:
    filmDict:dict[str, Any] = entry.film.to_dict()
    filmDict["date_added"] = entry.dateAdded.isoformat()
    filmDict["public"] = entry.public
    result.append(filmDict)

  return result