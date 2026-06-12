from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash
)

from app import db
from app.models import Game, Listing, ListingImage, User

from werkzeug.utils import secure_filename
import os

from datetime import datetime

from collections import defaultdict

from sqlalchemy import or_

admin = Blueprint(
    "admin",
    __name__
)

@admin.route("/admin/add-game", methods= ["GET","POST"])
def add_game():

    if session.get("role") != "admin":

        return redirect("/")
    
    if request.method == "POST":

        name = request.form.get("name")

        game = Game(
            name=name,
            telegram=request.form.get("telegram"),
            messenger=request.form.get("messenger"),
            viber=request.form.get("viber"),
            phone=request.form.get("phone"),
        )

        db.session.add(game)
        db.session.commit()

        return redirect("/admin/add-game")
    
    return render_template("/admin/add_game.html")

@admin.route("/admin/add-listing", methods=["GET", "POST"])
def add_listing():

    if session.get("role") != "admin":

        return redirect("/")

    games = Game.query.all()

    if request.method == "POST":

        title = request.form.get("title")

        description = request.form.get("description")

        price = request.form.get("price")

        buy_price = request.form.get(
                    "buy_price"
                    )
                
        game_id = request.form.get("game_id")

        sale_type = request.form.get("sale_type")

        image = request.files.get("image")

        detail_images = request.files.getlist(
            "detail_images"
        )

        # filename = None

        # if image:

        #     filename = secure_filename(
        #         image.filename
        #     )

        #     image_path = os.path.join(
        #         "app/static/uploads",
        #         filename
        #     )
        #     print("Saving image to:", image_path)

        #     image.save(image_path)

        #     print("File exists after save:",
        #         os.path.exists(image_path))

        import cloudinary.uploader

        image_url = None

        if image and image.filename:

            result = cloudinary.uploader.upload(image)

            image_url = result["secure_url"]

        listing = Listing(
            title=title,
            description=description,
            price=price,
            game_id=game_id,
            # image=filename,
            image=image_url,
            buy_price=buy_price,
            sale_type=sale_type,
            seller_id = session["user_id"]
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


        flash("Listing added successfully")

        return redirect("/admin/add-listing")

    return render_template(
        "/admin/add_listing.html",
        games=games
    )

@admin.route("/admin/admin-listings")
def admin_listing():

    if session.get("role") != "admin":

        return redirect("/")
    
    

    page = request.args.get(
        "page",
        1,
        type=int
    )

    query = Listing.query.filter_by(
        seller_id=session["user_id"]
    )

    search = request.args.get("search")

    if search:

        query = query.filter(

            or_(

                Listing.title.ilike(
                    f"%{search}%"
                ),

                Listing.description.ilike(
                    f"%{search}%"
                )

            )
        )

    status = request.args.get("status")

    if status and status != "all":

        query= query.filter_by(
            status = status
        )

    featured = request.args.get("featured")

    if featured == "yes":

        query= query.filter_by(
            featured=True
        ) 

    game_id = request.args.get(
            "game_id"
        )

    if game_id:

        query = query.filter_by(
            game_id=game_id
        )

    query = query.order_by(
        Listing.created_at.desc()
    )   

    pagination = query.paginate(
        page = page,
        per_page = 6
    )

    listings = pagination.items

    games = Game.query.all()

    return render_template(
        "/admin/admin_listings.html",
        listings=listings,
        pagination = pagination,
        games=games
    )

@admin.route("/delete-listing/<int:listing_id>")
def delete_listing(listing_id):

    if session.get("role") != "admin":

        return redirect("/")

    listing = Listing.query.get_or_404(
        listing_id
    )

    db.session.delete(listing)

    db.session.commit()

    flash("Listing deleted")

    return redirect("/admin/admin-listings")

@admin.route("/mark-sold/<int:listing_id>", methods=["GET","POST"])
def mark_sold(listing_id):

    if session.get("role") != "admin":

        return redirect("/")
    
    listing = Listing.query.get_or_404(
        listing_id
    )

    if listing.seller_id != session.get(
        "user_id"
    ):

        return redirect("/")

    sold_price = request.form.get(
        "sold_price"
    )

    listing.sold_price = sold_price

    listing.status = "sold"

    listing.sold_at = datetime.utcnow()

    db.session.commit()

    return redirect("/admin/admin-listings")

@admin.route("/admin/edit-listing/<int:listing_id>", methods=["GET","POST"])
def edit_listing(listing_id):
    if session.get("role") != "admin":

        return redirect("/")
    listing = Listing.query.get_or_404(listing_id)

    games = Game.query.all()

    if request.method == "POST":

        listing.title = request.form.get(
            "title"
        )

        listing.description = request.form.get(
            "description"
        )

        listing.price = request.form.get(
            "price"
        )

        listing.rank = request.form.get(
            "rank"
        )

        listing.server = request.form.get(
            "server"
        )

        listing.game_id = request.form.get(
            "game_id"
        )

        db.session.commit()

        flash("Listing updated")

        return redirect("/admin/admin-listings")
    
    return render_template(
        "/admin/edit_listing.html",
        listing=listing,
        games=games
    )

@admin.route("/admin/dashboard")
def admin_dashboard():

    total_listings = Listing.query.filter_by(
        seller_id=session["user_id"]
    ).count()

    available_listings = Listing.query.filter_by(
        status="available",
        seller_id=session["user_id"]
    ).count()

    sold_listings_count = Listing.query.filter_by(
        status="sold",
        seller_id=session["user_id"]
    ).count()

    recent_listings = Listing.query.filter_by(seller_id=session["user_id"]).order_by(
        Listing.created_at.desc()
    ).limit(5)

    listings = Listing.query.filter_by(
        seller_id= session["user_id"]
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

        (listing.sold_price or 0)
        -
        (listing.buy_price or 0)

        for listing in listings

        if (
            listing.status == "sold"
            and listing.sale_type == "sale"
        )
    )

    profit_by_day = defaultdict(float)

    sold_listings= Listing.query.filter_by(
        seller_id = session["user_id"]
    ).all()

    for listing in sold_listings:

        if listing.sold_at:

            day = listing.sold_at.strftime(
                "%Y-%m-%d"
            )

            profit = (
                (listing.sold_price or 0)
                -
                (listing.buy_price or 0)
            )

            profit_by_day[day] += profit

    profit_labels = list(
        profit_by_day.keys()
    )

    profit_values = list(
        profit_by_day.values()
    )
    return render_template(

        "admin/dashboard.html",

        total_listings=total_listings,

        available_listings=available_listings,

        sold_listings=sold_listings_count,

        recent_listings=recent_listings,

        total_spending=total_spending,

        total_revenue=total_revenue,

        total_profit=total_profit,

        profit_labels=profit_labels,

        profit_values=profit_values,
    )

@admin.route("/toggle-featured/<int:id>")
def toggle_featured(id):

    listing = Listing.query.get_or_404(id)

    listing.featured= not listing.featured

    db.session.commit()

    return redirect(
        "/admin/admin-listings"
    )

@admin.route("/admin/profile", methods=["GET","POST"])
def seller_profile():

    user = User.query.get(
        session["user_id"]
    )

    if request.method == "POST":

        user.telegram = request.form.get(
            "telegram"
        )

        user.messenger = request.form.get(
            "messenger"
        )

        user.viber = request.form.get(
            "viber"
        )

        user.phone = request.form.get(
            "phone"
        )

        image = request.files.get(
            "profile_image"
        )

        import cloudinary.uploader

        image_url = None

        if image and image.filename:

            result = cloudinary.uploader.upload(image)

            image_url = result["secure_url"]

        # if image and image.filename != "":

        #     filename = secure_filename(
        #         image.filename
        #     )

        #     image_path = os.path.join(
        #         "app/static/uploads",
        #         filename
        #     )

        #     image.save(image_path)

        #     user.profile_image = filename

        user.profile_image = image

        db.session.commit()

        return redirect(
            "/admin/profile"
        )

    return render_template(
        "admin/profile.html",
        user=user
    )
