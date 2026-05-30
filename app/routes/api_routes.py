from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from app.models import Game, Listing
from app.serializers import serialize_game, serialize_listing


api = Blueprint("api", __name__, url_prefix="/api")


def available_listings_query():
    return Listing.query.filter_by(status="available")


def find_game_by_names(names):
    normalized_names = {name.lower() for name in names}

    for game in Game.query.all():
        if game.name.lower() in normalized_names:
            return game

    return None


def apply_listing_filters(query):
    search = request.args.get("search", "").strip()
    game_id = request.args.get("game_id", type=int)

    if search:
        query = query.filter(
            or_(
                Listing.title.ilike(f"%{search}%"),
                Listing.description.ilike(f"%{search}%"),
            )
        )

    if game_id:
        query = query.filter(Listing.game_id == game_id)

    return query


@api.get("/health")
def health_check():
    return jsonify({"status": "ok"})


@api.get("/games")
def games():
    games_list = Game.query.order_by(Game.name.asc()).all()

    return jsonify([
        serialize_game(game)
        for game in games_list
    ])


@api.get("/home")
def home():
    ml_game = find_game_by_names(["mobile legends", "mobile legend", "mlbb"])
    pubg_game = find_game_by_names(["pubg", "pubg mobile"])

    def section_listings(game):
        query = available_listings_query()

        if game:
            query = query.filter(Listing.game_id == game.id)

        query = apply_listing_filters(query)

        return query.order_by(
            Listing.featured.desc(),
            Listing.created_at.desc(),
        ).limit(12).all()

    return jsonify(
        {
            "games": [
                serialize_game(game)
                for game in Game.query.order_by(Game.name.asc()).all()
            ],
            "mobile_legends_listings": [
                serialize_listing(listing)
                for listing in section_listings(ml_game)
            ],
            "pubg_listings": [
                serialize_listing(listing)
                for listing in section_listings(pubg_game)
            ],
        }
    )


@api.get("/listings")
def listings():
    query = apply_listing_filters(available_listings_query())
    listings_list = query.order_by(
        Listing.featured.desc(),
        Listing.created_at.desc(),
    ).all()

    return jsonify([
        serialize_listing(listing)
        for listing in listings_list
    ])


@api.get("/listings/<int:listing_id>")
def listing_details(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    return jsonify(serialize_listing(listing, include_details=True))
