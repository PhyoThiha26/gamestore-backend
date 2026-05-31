from flask import url_for


# def upload_url(filename):
#     if not filename:
#         return None

#     return url_for("static", filename=f"uploads/{filename}", _external=True)

def upload_url(image):
    if not image:
        return None

    # already full URL (Cloudinary or external)
    if image.startswith("http://") or image.startswith("https://"):
        return image

    # fallback for old local files
    return url_for("static", filename=f"uploads/{image}", _external=True)

def serialize_game(game):
    return {
        "id": game.id,
        "name": game.name,
        "image": game.image,
        # "image_url": upload_url(game.image),
        "telegram": game.telegram,
        "messenger": game.messenger,
        "viber": game.viber,
        "phone": game.phone
    }


def serialize_seller(user):
    if not user:
        return None

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "profile_image": user.profile_image,
        "profile_image_url": upload_url(user.profile_image),
        "telegram": user.telegram,
        "messenger": user.messenger,
        "viber": user.viber,
        "phone": user.phone,
    }


def serialize_listing_image(image):
    return {
        "id": image.id,
        "image": image.image,
        "image_url": upload_url(image.image),
    }


def serialize_listing(listing, include_details=False):
    data = {
        "id": listing.id,
        "title": listing.title,
        "description": listing.description,
        "price": listing.price,
        "rank": listing.rank,
        "server": listing.server,
        "image": listing.image,
        "image_url": upload_url(listing.image),
        "status": listing.status,
        "game_id": listing.game_id,
        "game": listing.game.name if listing.game else None,
        "featured": listing.featured,
        "sale_type": listing.sale_type,
        "created_at": listing.created_at.isoformat() if listing.created_at else None,
        "seller_id": listing.seller_id,
        "seller": serialize_seller(listing.seller),
    }

    if include_details:
        data.update(
            {
                "buy_price": listing.buy_price,
                "sold_price": listing.sold_price,
                "sold_at": listing.sold_at.isoformat() if listing.sold_at else None,
                "images": [
                    serialize_listing_image(image)
                    for image in listing.images
                ],
            }
        )

    return data
