from flask import Blueprint, request, jsonify, session
from app import db
from app.models import Game, Listing, ListingImage, User
from datetime import datetime
from collections import defaultdict
from sqlalchemy import or_

admin_api = Blueprint("admin_api", __name__, url_prefix="/api/admin")


def require_admin():
    return session.get("role") == "admin"


def listing_to_dict(listing):
    return {
        "id": listing.id,
        "title": listing.title,
        "description": listing.description,
        "price": listing.price,
        "buy_price": listing.buy_price,
        "sold_price": listing.sold_price,
        "sale_type": listing.sale_type,
        "status": listing.status,
        "featured": listing.featured,
        "image": listing.image,
        "rank": listing.rank,
        "server": listing.server,
        "game_id": listing.game_id,
        "seller_id": listing.seller_id,
        "created_at": listing.created_at.isoformat() if listing.created_at else None,
        "sold_at": listing.sold_at.isoformat() if listing.sold_at else None,
        "detail_images": [
            {
                "id": img.id,
                "image": img.image
            }
            for img in getattr(listing, "images", [])
        ],
    }


def game_to_dict(game):
    return {
        "id": game.id,
        "name": game.name,
        "telegram": game.telegram,
        "messenger": game.messenger,
        "viber": game.viber,
        "phone": game.phone,
    }


def user_to_dict(user):
    return {
        "id": user.id,
        "username": getattr(user, "username", None),
        "telegram": user.telegram,
        "messenger": user.messenger,
        "viber": user.viber,
        "phone": user.phone,
        "profile_image": user.profile_image,
    }


@admin_api.route("/games", methods=["GET"])
def get_games():
    if not require_admin():
        return jsonify({"message": "Unauthorized"}), 401

    games = Game.query.all()

    return jsonify({
        "games": [game_to_dict(game) for game in games]
    }), 200


@admin_api.route("/games", methods=["POST"])
def add_game():
    if not require_admin():
        return jsonify({"message": "Unauthorized"}), 401

    data = request.get_json()

    game = Game(
        name=data.get("name"),
        telegram=data.get("telegram"),
        messenger=data.get("messenger"),
        viber=data.get("viber"),
        phone=data.get("phone"),
    )

    db.session.add(game)
    db.session.commit()

    return jsonify({
        "message": "Game added successfully",
        "game": game_to_dict(game)
    }), 201


@admin_api.route("/listings", methods=["GET"])
def get_listings():
    if not require_admin():
        return jsonify({"message": "Unauthorized"}), 401

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 6, type=int)

    query = Listing.query.filter_by(
        seller_id=session["user_id"]
    )

    search = request.args.get("search")

    if search:
        query = query.filter(
            or_(
                Listing.title.ilike(f"%{search}%"),
                Listing.description.ilike(f"%{search}%")
            )
        )

    status = request.args.get("status")

    if status and status != "all":
        query = query.filter_by(status=status)

    featured = request.args.get("featured")

    if featured == "yes":
        query = query.filter_by(featured=True)

    game_id = request.args.get("game_id")

    if game_id:
        query = query.filter_by(game_id=game_id)

    query = query.order_by(Listing.created_at.desc())

    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        "listings": [
            listing_to_dict(listing)
            for listing in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    }), 200


@admin_api.route("/listings", methods=["POST"])
def add_listing():
    if not require_admin():
        return jsonify({"message": "Unauthorized"}), 401

    import cloudinary.uploader

    title = request.form.get("title")
    description = request.form.get("description")
    price = request.form.get("price")
    buy_price = request.form.get("buy_price")
    game_id = request.form.get("game_id")
    sale_type = request.form.get("sale_type")

    image = request.files.get("image")
    detail_images = request.files.getlist("detail_images")

    image_url = None

    if image and image.filename:
        result = cloudinary.uploader.upload(image)
        image_url = result["secure_url"]

    listing = Listing(
        title=title,
        description=description,
        price=price,
        buy_price=buy_price,
        game_id=game_id,
        sale_type=sale_type,
        image=image_url,
        seller_id=session["user_id"]
    )

    db.session.add(listing)
    db.session.commit()

    for img in detail_images:
        if img.filename:
            result = cloudinary.uploader.upload(img)
            detail_url = result["secure_url"]

            new_image = ListingImage(
                image=detail_url,
                listing_id=listing.id
            )

            db.session.add(new_image)

    db.session.commit()

    return jsonify({
        "message": "Listing added successfully",
        "listing": listing_to_dict(listing)
    }), 201


@admin_api.route("/listings/<int:listing_id>", methods=["GET"])
def get_listing(listing_id):
    if not require_admin():
        return jsonify({"message": "Unauthorized"}), 401

    listing = Listing.query.get_or_404(listing_id)

    if listing.seller_id != session.get("user_id"):
        return jsonify({"message": "Forbidden"}), 403

    return jsonify({
        "listing": listing_to_dict(listing)
    }), 200


@admin_api.route("/listings/<int:listing_id>", methods=["PUT"])
def edit_listing(listing_id):
    if not require_admin():
        return jsonify({"message": "Unauthorized"}), 401

    listing = Listing.query.get_or_404(listing_id)

    if listing.seller_id != session.get("user_id"):
        return jsonify({"message": "Forbidden"}), 403

    data = request.get_json()

    listing.title = data.get("title", listing.title)
    listing.description = data.get("description", listing.description)
    listing.price = data.get("price", listing.price)
    listing.rank = data.get("rank", listing.rank)
    listing.server = data.get("server", listing.server)
    listing.game_id = data.get("game_id", listing.game_id)

    db.session.commit()

    return jsonify({
        "message": "Listing updated successfully",
        "listing": listing_to_dict(listing)
    }), 200


@admin_api.route("/listings/<int:listing_id>", methods=["DELETE"])
def delete_listing(listing_id):
    if not require_admin():
        return jsonify({"message": "Unauthorized"}), 401

    listing = Listing.query.get_or_404(listing_id)

    if listing.seller_id != session.get("user_id"):
        return jsonify({"message": "Forbidden"}), 403

    db.session.delete(listing)
    db.session.commit()

    return jsonify({
        "message": "Listing deleted successfully"
    }), 200


@admin_api.route("/listings/<int:listing_id>/mark-sold", methods=["PATCH"])
def mark_sold(listing_id):
    if not require_admin():
        return jsonify({"message": "Unauthorized"}), 401

    listing = Listing.query.get_or_404(listing_id)

    if listing.seller_id != session.get("user_id"):
        return jsonify({"message": "Forbidden"}), 403

    data = request.get_json()

    listing.sold_price = data.get("sold_price")
    listing.status = "sold"
    listing.sold_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "message": "Listing marked as sold",
        "listing": listing_to_dict(listing)
    }), 200


@admin_api.route("/listings/<int:listing_id>/toggle-featured", methods=["PATCH"])
def toggle_featured(listing_id):
    if not require_admin():
        return jsonify({"message": "Unauthorized"}), 401

    listing = Listing.query.get_or_404(listing_id)

    if listing.seller_id != session.get("user_id"):
        return jsonify({"message": "Forbidden"}), 403

    listing.featured = not listing.featured

    db.session.commit()

    return jsonify({
        "message": "Featured status updated",
        "listing": listing_to_dict(listing)
    }), 200


@admin_api.route("/dashboard", methods=["GET"])
def admin_dashboard():
    if not require_admin():
        return jsonify({"message": "Unauthorized"}), 401

    seller_id = session["user_id"]

    total_listings = Listing.query.filter_by(
        seller_id=seller_id
    ).count()

    available_listings = Listing.query.filter_by(
        status="available",
        seller_id=seller_id
    ).count()

    sold_listings_count = Listing.query.filter_by(
        status="sold",
        seller_id=seller_id
    ).count()

    recent_listings = Listing.query.filter_by(
        seller_id=seller_id
    ).order_by(
        Listing.created_at.desc()
    ).limit(5).all()

    listings = Listing.query.filter_by(
        seller_id=seller_id
    ).all()

    total_spending = sum(
        listing.buy_price or 0
        for listing in listings
        if listing.sale_type == "sale"
    )

    total_revenue = sum(
        listing.sold_price or 0
        for listing in listings
        if listing.sale_type == "sale"
    )

    total_profit = sum(
        (listing.sold_price or 0) - (listing.buy_price or 0)
        for listing in listings
        if listing.status == "sold" and listing.sale_type == "sale"
    )

    profit_by_day = defaultdict(float)

    for listing in listings:
        if listing.sold_at:
            day = listing.sold_at.strftime("%Y-%m-%d")
            profit = (listing.sold_price or 0) - (listing.buy_price or 0)
            profit_by_day[day] += profit

    return jsonify({
        "total_listings": total_listings,
        "available_listings": available_listings,
        "sold_listings": sold_listings_count,
        "recent_listings": [
            listing_to_dict(listing)
            for listing in recent_listings
        ],
        "total_spending": total_spending,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "profit_labels": list(profit_by_day.keys()),
        "profit_values": list(profit_by_day.values()),
    }), 200


@admin_api.route("/profile", methods=["GET"])
def get_profile():
    if not require_admin():
        return jsonify({"message": "Unauthorized"}), 401

    user = User.query.get_or_404(session["user_id"])

    return jsonify({
        "user": user_to_dict(user)
    }), 200


@admin_api.route("/profile", methods=["PUT"])
def update_profile():
    if not require_admin():
        return jsonify({"message": "Unauthorized"}), 401

    import cloudinary.uploader

    user = User.query.get_or_404(session["user_id"])

    user.telegram = request.form.get("telegram", user.telegram)
    user.messenger = request.form.get("messenger", user.messenger)
    user.viber = request.form.get("viber", user.viber)
    user.phone = request.form.get("phone", user.phone)

    image = request.files.get("profile_image")

    if image and image.filename:
        result = cloudinary.uploader.upload(image)
        user.profile_image = result["secure_url"]

    db.session.commit()

    return jsonify({
        "message": "Profile updated successfully",
        "user": user_to_dict(user)
    }), 200