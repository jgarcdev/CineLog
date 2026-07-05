"""
routes/collection.py — CineLog

Endpoints for a user's film collection (films they've logged as watched).
"""

from flask import Blueprint, jsonify, request
from services.collectionService import (
  addToCollection,
  removeFromCollection,
  getCollection,
  FilmNotFoundError,
  AlreadyInCollectionError,
  NotInCollectionError,
)


collectionBp = Blueprint("collection", __name__)


@collectionBp.route("/<user_id>", methods=["GET"])
def viewCollection(userId):
  """
  GET /collection/<user_id>
@collectionBp.route("/<user_id>", methods=["GET"])
def viewCollection(userId):
  """
  GET /collection/<user_id>

  Returns all films in a user's collection, sorted newest-first.
  """
  films = getCollection(userId)

  return jsonify(films)
  Returns all films in a user's collection, sorted newest-first.
  """
  films = getCollection(userId)

  return jsonify(films)


@collectionBp.route("/<user_id>/add", methods=["POST"])
def addFilm(userId):
  """
  POST /collection/<user_id>/add
@collectionBp.route("/<user_id>/add", methods=["POST"])
def addFilm(userId):
  """
  POST /collection/<user_id>/add

  Body: { "film_id": "<uuid>", "rating": 4 }  (rating optional)
  """
  data = request.get_json()
  if not data or "film_id" not in data: return jsonify({"error": "film_id is required"}), 400
  Body: { "film_id": "<uuid>", "rating": 4 }  (rating optional)
  """
  data = request.get_json()
  if not data or "film_id" not in data: return jsonify({"error": "film_id is required"}), 400

  try:
    entry = addToCollection(userId=userId, filmId=data["film_id"], rating=data.get("rating"))

    return jsonify(entry.to_dict()), 201
  except FilmNotFoundError as e: return jsonify({"error": str(e)}), 404
  except AlreadyInCollectionError as e: return jsonify({"error": str(e)}), 409
  try:
    entry = addToCollection(userId=userId, filmId=data["film_id"], rating=data.get("rating"))

    return jsonify(entry.to_dict()), 201
  except FilmNotFoundError as e: return jsonify({"error": str(e)}), 404
  except AlreadyInCollectionError as e: return jsonify({"error": str(e)}), 409


@collectionBp.route("/<user_id>/remove", methods=["DELETE"])
def removeFilm(userId):
  """
  DELETE /collection/<user_id>/remove
@collectionBp.route("/<user_id>/remove", methods=["DELETE"])
def removeFilm(userId):
  """
  DELETE /collection/<user_id>/remove

  Body: { "film_id": "<uuid>" }
  """
  data = request.get_json()
  if not data or "film_id" not in data: return jsonify({"error": "film_id is required"}), 400
  Body: { "film_id": "<uuid>" }
  """
  data = request.get_json()
  if not data or "film_id" not in data: return jsonify({"error": "film_id is required"}), 400

  try:
    removeFromCollection(userId=userId, filmId=data["film_id"])

    return jsonify({"message": "Removed from collection"}), 200
  except NotInCollectionError as e: return jsonify({"error": str(e)}), 404
  try:
    removeFromCollection(userId=userId, filmId=data["film_id"])

    return jsonify({"message": "Removed from collection"}), 200
  except NotInCollectionError as e: return jsonify({"error": str(e)}), 404