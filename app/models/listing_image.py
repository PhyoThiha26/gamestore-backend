from app import db

class ListingImage(db.Model):
    id= db.Column(db.Integer,
                  primary_key=True)
    
    image= db.Column(db.String(255))

    listing_id = db.Column(db.Integer,db.ForeignKey("listing.id"))