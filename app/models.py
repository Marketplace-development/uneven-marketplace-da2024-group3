from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'
    
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)  # Username should be unique
    email = db.Column(db.String(80), unique=True, nullable=False)  # Email should also be unique
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for when the user was created
    address = db.Column(db.String(255))  # Address of the user

    libraries = db.relationship('Libraries', backref='user', lazy=True)
    records = db.relationship('Records', backref='user', lazy=True)

   #def __repr__(self):
    #    return f'<User {self.username}>'

class Libraries(db.Model):
    __tablename__ = 'libraries'
    libraryid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)
    library_records = db.relationship('LibraryRecords', backref='library', lazy=True)



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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    library_records = db.relationship('LibraryRecords', backref='record', lazy=True)
    transactions = db.relationship('Transactions', backref='record', lazy=True)

    def __repr__(self):
        return f'<Record {self.albumname}, ${self.price}>'


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
