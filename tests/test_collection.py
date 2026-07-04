"""
tests/test_collection.py — CineLog

Tests for the collection service.
These tests demonstrate the patterns used across the codebase — read them
before writing your own tests for the watchlist feature (see Comment 4).
"""

import pytest
from app import createApp, db
from models import User, Film, CollectionEntry
from services.collectionService import (
  addToCollection,
  removeFromCollection,
  getCollection,
  FilmNotFoundError,
  AlreadyInCollectionError,
  NotInCollectionError,
)


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
    user = User(username="testuser", email="test@example.com")
    db.session.add(user)
    db.session.commit()
    return user.id


@pytest.fixture
def sampleFilm(app):
  """A film to use in tests."""
  with app.app_context():
    film = Film(title="Paddington 2", year=2017, genre="Comedy")
    db.session.add(film)
    db.session.commit()
    return film.id


# ── Basic add ───────────────────────────────────────────────────────────────

def test_addToCollectionCreatesEntry(app, sampleUser, sampleFilm):
  """
  Adding a valid film should create a CollectionEntry in the database.
  """
  with app.app_context():
    entry = addToCollection(userId=sampleUser, filmId=sampleFilm)

    assert entry is not None
    assert entry.userId == sampleUser
    assert entry.filmId == sampleFilm

    # Verify it persisted
    inDb = CollectionEntry.query.filter_by(userId=sampleUser, filmId=sampleFilm).first()
    assert inDb is not None


# ── Deduplication ────────────────────────────────────────────────────────────

def test_addToCollectionDuplicateRaises(app, sampleUser, sampleFilm):
  """
  Adding the same film twice should raise AlreadyInCollectionError,
  not silently create a duplicate entry.
  """
  with app.app_context():
    addToCollection(userId=sampleUser, filmId=sampleFilm)

    with pytest.raises(AlreadyInCollectionError):
      addToCollection(userId=sampleUser, filmId=sampleFilm)

    # Confirm only one entry exists
    count = CollectionEntry.query.filter_by(userId=sampleUser, filmId=sampleFilm).count()
    assert count == 1


# ── Nonexistent film ─────────────────────────────────────────────────────────

def test_addToCollectionNonexistentFilmRaises(app, sampleUser):
  """
  Adding a film_id that doesn't exist in the database should raise
  FilmNotFoundError, not a database integrity error.
  """
  with app.app_context():
    fakeFilmId = "00000000-0000-0000-0000-000000000000"

    with pytest.raises(FilmNotFoundError):
      addToCollection(userId=sampleUser, filmId=fakeFilmId)


# ── getCollection sort order ────────────────────────────────────────────────

def test_getCollectionReturnsNewestFirst(app, sampleUser):
  """
  getCollection() should return films sorted by date_added descending
  (most recently added first).
  """
  with app.app_context():
    from datetime import datetime, timezone, timedelta
    from models import Film, CollectionEntry

    filmA = Film(title="Alien", year=1979, genre="Horror")
    filmB = Film(title="Blade Runner", year=1982, genre="Sci-Fi")
    db.session.add_all([filmA, filmB])
    db.session.commit()

    earlier = datetime.now(timezone.utc) - timedelta(days=5)
    later = datetime.now(timezone.utc)

    entryA = CollectionEntry(userId=sampleUser, filmId=filmA.id, dateAdded=earlier)
    entryB = CollectionEntry(userId=sampleUser, filmId=filmB.id, dateAdded=later)
    db.session.add_all([entryA, entryB])
    db.session.commit()

    collection = getCollection(sampleUser)
    titles = [f["title"] for f in collection]

    # Blade Runner was added later, so it should come first
    assert titles[0] == "Blade Runner"
    assert titles[1] == "Alien"