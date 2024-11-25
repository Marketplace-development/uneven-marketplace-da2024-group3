from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Users model
class Users(db.Model):
    __tablename__ = 'users'
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # Username should be unique
    email = db.Column(db.String(80), unique=True, nullable=False)  # Email should also be unique
    libraries = db.relationship('Libraries', backref='user', lazy=True)
    buyers = db.relationship('Buyers', backref='user', lazy=True, uselist=False)  # Assuming a user can be a buyer once
    sellers = db.relationship('Sellers', backref='user', lazy=True, uselist=False)  # Assuming a user can be a seller once
    records = db.relationship('Records', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

# Libraries model
class Libraries(db.Model):
    __tablename__ = 'libraries'
    libraryid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)
    library_records = db.relationship('LibraryRecords', backref='library', lazy=True)

# Buyers model
class Buyers(db.Model):
    __tablename__ = 'buyers'
    buyerid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False, unique=True)  # One-to-one with user
    address = db.Column(db.String(80), nullable=False)  # Assume multiple people can have the same address
    transactions = db.relationship('Transactions', backref='buyer', lazy=True)

    def __repr__(self):
        return f'Address {self.address}'

# Records model
class Records(db.Model):
    __tablename__ = 'records'
    recordid = db.Column(db.Integer, primary_key=True)
    albumname = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    size = db.Column(db.String(100), nullable=False)
    condition = db.Column(db.String(100), nullable=False)
    colour = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Float, nullable=False)
    ownerid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)  # Foreign key to Users
    library_records = db.relationship('LibraryRecords', backref='record', lazy=True)
    transactions = db.relationship('Transactions', backref='record', lazy=True)

    def __repr__(self):
        return f'<Record {self.albumname}, ${self.price}>'

# Sellers model
class Sellers(db.Model):
    __tablename__ = 'sellers'
    sellerid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False, unique=True)  # One-to-one with user

    def __repr__(self):
        return f'<Seller ID {self.sellerid}>'

# LibraryRecords model (linking libraries and records)
class LibraryRecords(db.Model):
    __tablename__ = 'library_records'
    recordid = db.Column(db.Integer, db.ForeignKey('records.recordid'), primary_key=True)
    libraryid = db.Column(db.Integer, db.ForeignKey('libraries.libraryid'), primary_key=True)

# Transactions model
class Transactions(db.Model):
    __tablename__ = 'transactions'
    transactionid = db.Column(db.Integer, primary_key=True)
    recordid = db.Column(db.Integer, db.ForeignKey('records.recordid'), nullable=False)  # Link to Records
    buyerid = db.Column(db.Integer, db.ForeignKey('buyers.buyerid'), nullable=False)
    status = db.Column(db.String(100), nullable=False)  # Making status non-nullable
    reviews = db.relationship('Reviews', backref='transaction', lazy=True)

    def __repr__(self):
        return f'Transaction {self.transactionid}, Status {self.status}'

# Reviews model
class Reviews(db.Model):
    __tablename__ = 'reviews'
    reviewid = db.Column(db.Integer, primary_key=True)
    transactionid = db.Column(db.Integer, db.ForeignKey('transactions.transactionid'), nullable=False)
    reviewscore = db.Column(db.Numeric, nullable=False)
    reasoning = db.Column(db.String(100))

    def __repr__(self):
        return f'<Review {self.reviewscore}, {self.reasoning}>'
