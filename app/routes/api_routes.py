from flask import Blueprint, jsonify, request
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, selectinload

from app.models import Game, Listing
from app.serializers import serialize_game, serialize_listing,serialize_listing_card


api = Blueprint("api", __name__, url_prefix="/api")


def available_listings_query():
    return Listing.query.options(
        joinedload(Listing.game),
        joinedload(Listing.seller),
    ).filter_by(status="available")


# def find_game_by_names(games_list, names):
#     normalized_names = {name.lower() for name in names}

#     for game in games_list:
#         if game.name.lower() in normalized_names:
#             return game

#     return None

from sqlalchemy import func

def find_game_by_names(names):
    names = [name.lower() for name in names]

    return (
        Game.query
        .filter(func.lower(Game.name).in_(names))
        .first()
    )

def apply_listing_filters(query):
    search = request.args.get("search", "").strip()
    game_id = request.args.get("game_id", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)

    
    if game_id:
        query = query.filter(Listing.game_id == game_id)

    if search:
        query = query.filter(
            or_(
                Listing.title.ilike(f"%{search}%"),
                Listing.description.ilike(f"%{search}%"),
            )
        )
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)

    if max_price is not None:
        query = query.filter(Listing.price <= max_price)

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


# @api.get("/home")
# def home():
#     games_list = Game.query.order_by(Game.name.asc()).all()
#     ml_game = find_game_by_names(games_list, ["mobile legends", "mobile legend", "mlbb"])
#     pubg_game = find_game_by_names(games_list, ["pubg", "pubg mobile"])

#     def section_listings(game):
#         query = available_listings_query()

#         if game:
#             query = query.filter(Listing.game_id == game.id)

#         query = apply_listing_filters(query)

#         return query.order_by(
#             Listing.featured.desc(),
#             Listing.created_at.desc(),
#         ).limit(12).all()

#     return jsonify(
#         {
#             "games": [
#                 serialize_game(game)
#                 for game in games_list
#             ],
#             "mobile_legends_listings": [
#                 serialize_listing(listing)
#                 for listing in section_listings(ml_game)
#             ],
#             "pubg_listings": [
#                 serialize_listing(listing)
#                 for listing in section_listings(pubg_game)
#             ],
#         }
#     )

@api.get("/home")
def home():
    games = Game.query.order_by(Game.name.asc()).all()

    ml_game = next(
        (
            g for g in games
            if g.name.lower() in ["mobile legends", "mobile legend", "mlbb"]
        ),
        None,
    )

    pubg_game = next(
        (
            g for g in games
            if g.name.lower() in ["pubg", "pubg mobile"]
        ),
        None,
    )

    def section_listings(game):
        query = available_listings_query()

        if game:
            query = query.filter(Listing.game_id == game.id)

        query = apply_listing_filters(query)

        return (
            query.order_by(
                Listing.featured.desc(),
                Listing.created_at.desc(),
            )
            .limit(12)
            .all()
        )

    return jsonify({
        "games": [serialize_game(game) for game in games],
        "mobile_legends_listings": [
            serialize_listing_card(listing)
            for listing in section_listings(ml_game)
        ],
        "pubg_listings": [
            serialize_listing_card(listing)
            for listing in section_listings(pubg_game)
        ],
    })

@api.get("/listings")
def listings():
    sort = request.args.get("sort", "newest")

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 6, type=int)

    query = apply_listing_filters(available_listings_query())
    
    if sort == "price_asc":
        query = query.order_by(Listing.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Listing.price.desc())
    else:
        query = query.order_by(
            Listing.featured.desc(),
            Listing.created_at.desc(),
        )
    
    # pagination = query.paginate(
    #     page=page,
    #     per_page=per_page,
    #     error_out=False
    # )


    query = (
    apply_listing_filters(available_listings_query())
    .options(
        joinedload(Listing.game),
        joinedload(Listing.seller)
    )
)

    listings_list = query.all()

    # return jsonify({
    #     "items": [
    #        serialize_listing_card(listing)
    #         for listing in pagination.items
    #     ],
    #     "page": pagination.page,
    #     "pages": pagination.pages,
    #     "total": pagination.total,
    #     "has_next": pagination.has_next,
    #     "has_prev": pagination.has_prev,
    # })
    return jsonify([
        serialize_listing_card(listing)
        for listing in listings_list
    ])


@api.get("/listings/<int:listing_id>")
def listing_details(listing_id):
    listing = (
        Listing.query
        .options(
            joinedload(Listing.game),
            joinedload(Listing.seller),
            selectinload(Listing.images),
        )
        .filter(Listing.id == listing_id)
        .first_or_404()
    )

    return jsonify(serialize_listing(listing, include_details=True))