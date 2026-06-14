from app import db
from datetime import datetime

class Listing(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False,
        index=True

    )

    rank = db.Column(
        db.String(100)
    )

    server = db.Column(
        db.String(100)
    )

    image = db.Column(
        db.String(255)
    )

    status = db.Column(
        db.String(20),
        default="available",
        index=True
    )

    game_id = db.Column(
        db.Integer,
        db.ForeignKey("game.id"),
        index=True
    )

    game = db.relationship(
        "Game",
        backref = "listings"
    )

    created_at = db.Column(
        db.DateTime,
        default = datetime.utcnow
    )

    images = db.relationship(
        "ListingImage",
        backref="listing",
        lazy = True,
        cascade="all,delete"


    )

    featured = db.Column(
        db.Boolean,
        default= False,
        index=True

    )               

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )

    user = db.relationship(
        "User",
        backref="listing"
    )

    buy_price = db.Column(
        db.Float,
        default=0
    )

    sold_price = db.Column(
        db.Float,
        nullable=True
    )

    sold_at = db.Column(
        db.DateTime,
        nullable=True
    )

    sale_type = db.Column(
        db.String(50),
        nullable = True,
        default = "sale"
    )

