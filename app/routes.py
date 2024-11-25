from flask import Blueprint, request, redirect, url_for, render_template, session
from .models import db, Users, Libraries, Buyers, Records, Sellers, LibraryRecords, Transactions, Reviews

main = Blueprint('main', __name__)  

@main.route('/')
def index():
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
        if user:
            records = Records.query.filter_by(ownerid=user.userid).all()  
            return render_template('home.html', username=user.username, listings=records)
    return render_template('home.html', username=None)

@main.route('/home')
def home():
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
        if user:
            records = Records.query.filter_by(ownerid=user.userid).all()  
            return render_template('home.html', username=user.username, listings=records)
    return render_template('home.html', username=None)
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if Users.query.filter_by(username=username).first() is None:
            new_user = Users(username=username, email="example@example.com")  
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.userid  
            return redirect(url_for('main.index'))
        return 'Username already registered'
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = Users.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.userid  
            return redirect(url_for('main.index'))
        return 'User not found'
    return render_template('login.html')

@main.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.index'))

@main.route('/add-listing', methods=['GET', 'POST'])
def add_listing():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        listing_name = request.form['listing_name']  
        price = float(request.form['price'])
        new_listing = Records(albumname=listing_name,price=price,ownerid=session['user_id'],  artist='Unknown',genre='Unknown',size='Unknown',condition='Unknown',colour='Unknown')
        db.session.add(new_listing)
        db.session.commit()
        return redirect(url_for('main.listings'))

    return render_template('add_listing.html')

@main.route('/listings')
def listings():
    all_listings = Records.query.all()
    return render_template('listings.html', listings=all_listings)

@main.route('/verkoopoffer')
def verkoopoffer():
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
        if user:
            user_listings = Records.query.filter_by(ownerid=user.userid).all()  
            return render_template('verkoopoffer.html', username=user.username, listings=user_listings)
    return redirect(url_for('main.login'))

@main.route('/bied')
def bied():
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
        if user:
            user_listings = Records.query.filter_by(ownerid=user.userid).all()  
            return render_template('bied.html', username=user.username, listings=user_listings)
    return redirect(url_for('main.login'))
