from app import db


class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
    db.String(20),
    default="customer"
    )

    # listings = db.relationship(
    #     "Listing",
    #     backref="seller",
    #     lazy=True
    # )

    profile_image = db.Column(
    db.String(255)
    )

    telegram = db.Column(
        db.String(255)
    )

    messenger = db.Column(
        db.String(255)
    )

    viber = db.Column(
        db.String(255)
    )

    phone = db.Column(
        db.String(255)
    )
