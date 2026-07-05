"""
tests/test_watchlist.py — CineLog

Tests for the watchlist service.
"""

import pytest

from app import createApp, db
from models import User, Film
from services.watchlistService import addToWatchlist, removeFromWatchlist, getWatchlist
from services.watchlistService import AlreadyInWatchlistError, FilmNotFoundError, NotInWatchlistError


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
  with app.app_context():
    entry = addToWatchlist(userId=sampleUser, filmId=sampleFilm)
    assert entry is not None

    with pytest.raises(AlreadyInWatchlistError):
      addToWatchlist(userId=sampleUser, filmId=sampleFilm)

# ── Nonexistent film ─────────────────────────────────────────────────────────

def test_addToWatchlistNonexistentFilmRaises(app, sampleUser):
  """
  Adding a filmId that doesn't exist in the database should raise FilmNotFoundError, not a database integrity error.
  """
  with app.app_context():
    fakeFilmId = 202072

    with pytest.raises(FilmNotFoundError):
      addToWatchlist(userId=sampleUser, filmId=fakeFilmId)

# ── Visibility ───────────────────────────────────────────────────────────────

def test_addToWatchlistPublicDefaultsTrue(app, sampleUser, sampleFilm):
  """
  Not passing `public` should default the entry to public.
  """
  with app.app_context():
    entry = addToWatchlist(userId=sampleUser, filmId=sampleFilm)
    assert entry.public is True

def test_addToWatchlistPublicCanBeSetFalse(app, sampleUser, sampleFilm):
  """
  Passing `public=False` should save the entry as private.
  """
  with app.app_context():
    entry = addToWatchlist(userId=sampleUser, filmId=sampleFilm, public=False)
    assert entry.public is False

# --- Removal ───────────────────────────────────────────────────────────────

def test_removeFromWatchlistRemovesEntry(app, sampleUser, sampleFilm):
  """
  Removing a film from the watchlist should delete the entry.
  """
  with app.app_context():
    addToWatchlist(userId=sampleUser, filmId=sampleFilm)

    # Confirm it exists
    entry = db.session.query(Film).filter_by(id=sampleFilm).first()
    assert entry is not None

    # Remove it
    result = removeFromWatchlist(userId=sampleUser, filmId=sampleFilm)
    assert result is True

    # Confirm it's gone
    # Check the watchlist entry
    entry = getWatchlist(userId=sampleUser)
    assert entry == []

def test_removeFromWatchlistNonexistentFilmRaises(app, sampleUser):
  """
  Removing a film that isn't in the watchlist should raise NotInWatchlistError.
  """
  with app.app_context():
    fakeFilmId = 202072

    with pytest.raises(NotInWatchlistError):
      removeFromWatchlist(userId=sampleUser, filmId=fakeFilmId)