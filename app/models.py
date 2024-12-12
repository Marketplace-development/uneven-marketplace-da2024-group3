from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
db = SQLAlchemy()


class users(db.Model):
    __tablename__ = 'users'
    
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)  # Username should be unique
    email = db.Column(db.String(80), unique=True, nullable=False)  # Email should also be unique
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)  # Timestamp for when the user was created
    address = db.Column(db.String(255))  # Address of the user
    telefoonnummer = db.Column(db.String(20), nullable=False)
    records = db.relationship('records', backref='user', lazy=True)
    transactions_as_buyer = db.relationship('transactions', foreign_keys='transactions.buyerid', backref='buyer', lazy=True)
    transactions_as_seller = db.relationship('transactions', foreign_keys='transactions.sellerid', backref='seller', lazy=True)
    favorites = db.relationship('favorites', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'



# Records model
class records(db.Model):
    __tablename__ = 'records'
    recordid = db.Column(db.Integer, primary_key=True)
    albumname = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(100), nullable=False)
    colour = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Float, nullable=True)
    ownerid = db.Column(db.Integer, db.ForeignKey('users.userid', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)  # Foreign key to Users
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    Sellyesorno = db.Column(db.Boolean, default=False, nullable=False)
    image = db.Column(db.String(1000), nullable=False)
    favorites = db.relationship('favorites', backref='record', lazy=True)
    transactions = db.relationship('transactions', backref='record', lazy=True)

    def __repr__(self):
        return f'<Record {self.albumname}, ${self.price}>'


class transactions(db.Model):
    __tablename__ = 'transactions'
    transactionid = db.Column(db.Integer, primary_key=True)
    recordid = db.Column(db.Integer, db.ForeignKey('records.recordid', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    buyerid = db.Column(db.Integer, db.ForeignKey('users.userid', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    sellerid = db.Column(db.Integer, db.ForeignKey('users.userid', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False)
    handledyesorno = db.Column(db.Boolean, default=False, nullable=False)
    purchaseprice = db.Column(db.Float, nullable=False)  # Houdt de aankoopprijs bij
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)  # Database vult deze in
    albumname = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(100), nullable=False)
    colour = db.Column(db.String(100), nullable=False)
    reviews = db.relationship('reviews', backref='transaction', lazy=True, uselist=False)

    def __repr__(self):
        return f'transaction {self.transactionid}, purchase price: ${self.purchase_price}'


# Reviews model
class reviews(db.Model):
    __tablename__ = 'reviews'
    reviewid = db.Column(db.Integer, primary_key=True)
    transactionid = db.Column(db.Integer, db.ForeignKey('transactions.transactionid', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    reviewscore = db.Column(db.Numeric, nullable=False)
    reasoning = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)

    def __repr__(self):
        return f'<review {self.reviewscore}, {self.reasoning}>'

class favorites(db.Model):
    _tablename_ = 'favorites'
    favoriteid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid', ondelete='CASCADE', onupdate='CASCADE'),  nullable=False)
    recordid = db.Column(db.Integer, db.ForeignKey('records.recordid', ondelete='SET NULL', onupdate='CASCADE'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    
    def __repr__(self):
        return f'<Favorite User {self.userid} for Record {self.recordid}>'