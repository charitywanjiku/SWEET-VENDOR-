from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Sweet(db.Model, SerializerMixin):
    __tablename__ = 'sweets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Relationship with Vendor through VendorSweet (Many-to-Many)
    vendor_sweets = db.relationship(
        "Vendor",
        secondary='vendor_sweets',
        primaryjoin="Sweet.id == VendorSweet.sweet_id",
        secondaryjoin="Vendor.id == VendorSweet.vendor_id",
        backref="sweets",
    )

    # Limit recursion depth during serialization (optional)
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<Sweet {self.id} - {self.name}>'


class Vendor(db.Model, SerializerMixin):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Relationship with Sweet through VendorSweet (Many-to-Many)
    vendor_sweets = db.relationship(
        "Sweet",
        secondary='vendor_sweets',
        primaryjoin="Vendor.id == VendorSweet.vendor_id",
        secondaryjoin="Sweet.id == VendorSweet.sweet_id",
        backref="vendors",
    )

    # Limit recursion depth during serialization (optional)
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<Vendor {self.id} - {self.name}>'


class VendorSweet(db.Model, SerializerMixin):
    __tablename__ = 'vendor_sweets'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Relationships (one-to-many with cascade delete)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id', ondelete="CASCADE"))
    vendor = db.relationship("Vendor", backref=db.backref('vendor_sweet_associations', cascade="all, delete-orphan"))

    sweet_id = db.Column(db.Integer, db.ForeignKey('sweets.id', ondelete="CASCADE"))
    sweet = db.relationship("Sweet", backref=db.backref('vendor_sweet_associations', cascade="all, delete-orphan"))

    # Validation
    @validates('price')
    def validate_price(self, attr, price):
        if price is None or price < 0:
            raise ValueError("Price must be a positive number")
        return price

    
    # def to_dict(self):
    #     return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<VendorSweet {self.id} - Vendor: {self.vendor.name}, Sweet: {self.sweet.name}, Price: {self.price}>'
