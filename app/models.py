from . import db
from datetime import datetime


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    bucketlist = db.relationship("Bucketlist", backref="user", lazy="dynamic",
                                 cascade="all, delete-orphan")

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return "<User %s>" % self.username


class Bucketlists(db.Model):
    __tablename__ = "bucketlists"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    date_modified = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    items = db.relationship("Items", backref="bucketlist", lazy="dynamic",
                            cascade="all, delete-orphan")

    def __repr__(self):
        return '<Bucketlist %s>' % self.title


class Items(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False)
    date_modified = db.Column(db.DateTime)
    status = db.Column(db.String(5), default=False)
    bucket_id = db.Column(db.Integer, db.ForeignKey("bucketlists.id"))

    def __repr__(self):
        return "<Item %s>" % self.item_name
