from app import db


class Game(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    image = db.Column(
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