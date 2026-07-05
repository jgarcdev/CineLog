"""
tests/test_watchlist.py — CineLog

Tests for the watchlist service.
"""

import pytest

from app import createApp, db
from models import User, Film
from services.watchlistService import addToWatchlist
from services.collectionService import FilmNotFoundError


@pytest.fixture
def app():
  """Create an isolated test app with an in-memory database."""
  app = createApp(config={
    "TESTING": True,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
  })
  with app.app_context():
    db.create_all()
    yield app
    db.session.remove()
    db.drop_all()


@pytest.fixture
def sampleUser(app):
  """A user to use in tests."""
  with app.app_context():
    user = User(username="chiiaruel", email="CeciliaAndChii@grasscover.sw")
    db.session.add(user)
    db.session.commit()

    return user.id


@pytest.fixture
def sampleFilm(app):
  """A film to use in tests."""
  with app.app_context():
    film = Film(title="BitterlyWeptTheStars", year=2016, genre="tragedy")
    db.session.add(film)
    db.session.commit()

    return film.id


# ── Deduplication ────────────────────────────────────────────────────────────

def test_addToWatchlistDuplicateRaises(app, sampleUser, sampleFilm):
  """
  Adding the same film twice should raise AlreadyInWatchlistError.
  """
  from services.watchlistService import AlreadyInWatchlistError

  with app.app_context():
    entry = addToWatchlist(userId=sampleUser, filmId=sampleFilm)
    assert entry is not None

    with pytest.raises(AlreadyInWatchlistError):
      addToWatchlist(userId=sampleUser, filmId=sampleFilm)

# ── Nonexistent film ─────────────────────────────────────────────────────────

def test_addToWatchlistNonexistentFilmRaises(app, sampleUser):
  """
  Adding a film_id that doesn't exist in the database should raise FilmNotFoundError, not a database integrity error.
  """
  with app.app_context():
    fakeFilmId = 202072

    with pytest.raises(FilmNotFoundError):
      addToWatchlist(userId=sampleUser, filmId=fakeFilmId)
