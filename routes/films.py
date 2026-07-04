"""
routes/films.py — CineLog

Endpoints for browsing and looking up films. Read-only.
Film data is seeded; there is no admin endpoint for creating films here.
"""

from flask import Blueprint, jsonify, request
from models import Film

filmsBp = Blueprint("films", __name__)


@filmsBp.route("/", methods=["GET"])
def listFilms():
  """
  GET /films/

  Returns a list of all films. Supports optional ?genre= and ?year= query params.
  """
  genre = request.args.get("genre")
  year = request.args.get("year", type=int)

  query = Film.query
  if genre:query = query.filter(Film.genre.ilike(f"%{genre}%"))
  if year: query = query.filter_by(year=year)

  films = query.order_by(Film.title).all()

  return jsonify([f.to_dict() for f in films])


@filmsBp.route("/<film_id>", methods=["GET"])
def getFilm(filmId):
  """
  GET /films/<film_id>

  Returns a single film by its UUID.
  """
  film = Film.query.get(filmId)
  if film is None: return jsonify({"error": "Film not found"}), 404

  return jsonify(film.to_dict())