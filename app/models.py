from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class users(db.Model):
    __tablename__ = 'users'
    
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)  # Username should be unique
    email = db.Column(db.String(80), unique=True, nullable=False)  # Email should also be unique
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for when the user was created
    address = db.Column(db.String(255))  # Address of the user
    telefoonnummer = db.Column(db.String(20), nullable=False)
    libraries = db.relationship('libraries', backref='user', lazy=True)
    records = db.relationship('records', backref='user', lazy=True)

   #def __repr__(self):
    #    return f'<User {self.username}>'

class libraries(db.Model):
    __tablename__ = 'libraries'
    libraryid = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)
    library_records = db.relationship('libraryrecords', backref='library', lazy=True)

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
    ownerid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)  # Foreign key to Users
    created_at = db.Column(db.DateTime, default=datetime.now)  
    library_records = db.relationship('libraryrecords', backref='record', lazy=True)
    transactions = db.relationship('transactions', backref='record', lazy=True)
    Sellyesorno = db.Column(db.Boolean, default=False, nullable=False)
    image = db.Column(db.String(1000), nullable=True)

    def __repr__(self):
        return f'<Record {self.albumname}, ${self.price}>'


# LibraryRecords model (linking libraries and records)
class libraryrecords(db.Model):
    __tablename__ = 'library_records'
    recordid = db.Column(db.Integer, db.ForeignKey('records.recordid'), primary_key=True)
    libraryid = db.Column(db.Integer, db.ForeignKey('libraries.libraryid'), primary_key=True)



from sqlalchemy.sql import func

class transactions(db.Model):
    __tablename__ = 'transactions'
    transactionid = db.Column(db.Integer, primary_key=True)
    recordid = db.Column(db.Integer, db.ForeignKey('records.recordid'), nullable=False)
    buyerid = db.Column(db.Integer, db.ForeignKey('users.userid'), nullable=False)
    sellerid = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable = False)  # Database vult deze in
    reviews = db.relationship('reviews', backref='transaction', lazy=True)

    def __repr__(self):
        return f'transaction {self.transactionid}'



# Reviews model
class reviews(db.Model):
    __tablename__ = 'reviews'
    reviewid = db.Column(db.Integer, primary_key=True)
    transactionid = db.Column(db.Integer, db.ForeignKey('transactions.transactionid'), nullable=False)
    reviewscore = db.Column(db.Numeric, nullable=False)
    reasoning = db.Column(db.String(100))

    def __repr__(self):
        return f'<review {self.reviewscore}, {self.reasoning}>'

class favorites(db.Model):
    _tablename_ = 'favorites'
    userid = db.Column(db.Integer, db.ForeignKey('users.userid'), primary_key=True, nullable=False)
    recordid = db.Column(db.Integer, db.ForeignKey('records.recordid'), primary_key=True, nullable=False)