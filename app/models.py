from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    pass_hash = db.Column(db.String(255), nullable=False)
    bucketlist = db.relationship("Bucketlists", backref="user", lazy="dynamic",
                                 cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.pass_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.pass_hash, password)

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
