from flask import (
    Blueprint,
    render_template,
    request
)

from app.models import Listing,Game,User

from sqlalchemy import or_


main = Blueprint(
    "main",
    __name__
)

@main.route("/")
def home():
    search = request.args.get("search", "").strip()

    games = Game.query.all()

    ml_game = next(
        (game for game in games if game.name.lower() in ["mobile legends", "mobile legend", "mlbb"]),
        None
    )
    pubg_game = next(
        (game for game in games if game.name.lower() in ["pubg", "pubg mobile"]),
        None
    )

    def section_query(game):
        query = Listing.query.filter_by(status="available")

        if game:
            query = query.filter(Listing.game_id == game.id)

        if search:
            query = query.filter(
                or_(
                    Listing.title.ilike(f"%{search}%"),
                    Listing.description.ilike(f"%{search}%")
                )
            )

        return query.order_by(
            Listing.featured.desc(),
            Listing.created_at.desc()
        ).limit(12).all()

    ml_listings = section_query(ml_game)
    pubg_listings = section_query(pubg_game)

    return render_template(
        "home.html",
        games=games,
        ml_game_id=ml_game.id if ml_game else None,
        pubg_game_id=pubg_game.id if pubg_game else None,
        ml_listings=ml_listings,
        pubg_listings=pubg_listings
    )


@main.route("/listing/<int:listing_id>")
def listing_details(listing_id):

    listing = Listing.query.get_or_404(
        listing_id
    )


    return render_template(
        "listing_details.html",
        listing=listing   
    )

@main.route("/view-all/<int:game_id>")
def view_all(game_id):

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "newest")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    
    query = Listing.query.filter_by(status="available",
                                    game_id = game_id)

    if search:
        query = query.filter(
            or_(
                Listing.title.ilike(f"%{search}%"),
                Listing.description.ilike(f"%{search}%")
            )
        )

    numeric_price = cast(Listing.price, Float)

    if min_price is not None:
        query = query.filter(numeric_price >= min_price)

    if max_price is not None:
        query = query.filter(numeric_price <= max_price)

    if sort == "price_asc":
        query = query.order_by(numeric_price.asc())
    elif sort == "price_desc":
        query = query.order_by(numeric_price.desc())
    else:
        query = query.order_by(
            Listing.featured.desc(),
            Listing.created_at.desc()
        )


    pagination = query.paginate(page=page, per_page=12)


    return render_template(
        "view_all.html",
        listings=pagination.items,
        pagination=pagination,
        search=search,
        sort=sort,
        min_price=request.args.get("min_price", ""),
        max_price=request.args.get("max_price", "")
    )

