"""
routes/watchlist.py — CineLog (feature/watchlist branch)

Endpoints for the watchlist feature.
"""

from flask import Blueprint, jsonify, request
from services.watchlistService import addToWatchlist, getWatchlist
from services.collectionService import FilmNotFoundError


watchlistBp = Blueprint("watchlist", __name__)


@watchlistBp.route("/<user_id>", methods=["GET"])
def viewWatchlist(userId):
  """GET /watchlist/<user_id> — Return the user's watchlist."""
  films = getWatchlist(userId)

  return jsonify(films)


@watchlistBp.route("/<user_id>/add", methods=["POST"])
def addFilm(userId):
  """
  POST /watchlist/<user_id>/add

  Body: { "film_id": <int>, "public": <bool, optional> }
  """
  data = request.get_json()
  if not data or "film_id" not in data: return jsonify({"error": "film_id is required"}), 400

  entry = addToWatchlist(userId=userId, filmId=data["film_id"], public=data.get("public", True))

  return jsonify(entry.to_dict()), 201