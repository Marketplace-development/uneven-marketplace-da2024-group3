from flask import Blueprint, request, redirect, url_for, render_template, session
from .models import db, Users, Libraries, Buyers, Records,Sellers, Transactions,Reviews
from supabase import create_client, Client


main = Blueprint('main', __name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@main.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        response = supabase.table('Users').select("*").eq('userid', user_id).execute()
        user = response.data[0] if response.data else None
        if user:
            records_response = supabase.table('Records').select("*").eq('ownerid', user['userid']).execute()
            records = records_response.data if records_response.data else []
            return render_template('home.html', username=user['username'], listings=records)
    return render_template('home.html', username=None)

@main.route('/home')
def home():
    if 'user_id' in session:
        user_id = session['user_id']
        response = supabase.table('Users').select("*").eq('userid', user_id).execute()
        user = response.data[0] if response.data else None
        if user:
            records_response = supabase.table('Records').select("*").eq('ownerid', user['userid']).execute()
            records = records_response.data if records_response.data else []
            return render_template('home.html', username=user['username'], listings=records)
    return render_template('home.html', username=None)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        response = supabase.table('Users').select("*").eq('username', username).execute()
        if not response.data:  # User not already registered
            new_user = {
                'username': username,
                'email': "example@example.com"  # Replace with actual email field if available
            }
            insert_response = supabase.table('Users').insert(new_user).execute()
            if insert_response.data:
                session['user_id'] = insert_response.data[0]['userid']
                return redirect(url_for('main.index'))
        return 'Username already registered'
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        response = supabase.table('Users').select("*").eq('username', username).execute()
        if response.data:
            user = response.data[0]
            session['user_id'] = user['userid']
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
        new_listing = {
            'albumname': listing_name,
            'price': price,
            'ownerid': session['user_id'],
            'artist': 'Unknown',
            'genre': 'Unknown',
            'size': 'Unknown',
            'condition': 'Unknown',
            'colour': 'Unknown'
        }
        supabase.table('Records').insert(new_listing).execute()
        return redirect(url_for('main.listings'))

    return render_template('add_listing.html')

@main.route('/listings')
def listings():
    all_listings_response = supabase.table('Records').select("*").execute()
    all_listings = all_listings_response.data if all_listings_response.data else []
    return render_template('listings.html', listings=all_listings)

@main.route('/verkoopoffer')
def verkoopoffer():
    if 'user_id' in session:
        user_id = session['user_id']
        response = supabase.table('Users').select("*").eq('userid', user_id).execute()
        user = response.data[0] if response.data else None
        if user:
            user_listings_response = supabase.table('Records').select("*").eq('ownerid', user['userid']).execute()
            user_listings = user_listings_response.data if user_listings_response.data else []
            return render_template('verkoopoffer.html', username=user['username'], listings=user_listings)
    return redirect(url_for('main.login'))

@main.route('/bied')
def bied():
    if 'user_id' in session:
        user_id = session['user_id']
        response = supabase.table('Users').select("*").eq('userid', user_id).execute()
        user = response.data[0] if response.data else None
        if user:
            user_listings_response = supabase.table('Records').select("*").eq('ownerid', user['userid']).execute()
            user_listings = user_listings_response.data if user_listings_response.data else []
            return render_template('bied.html', username=user['username'], listings=user_listings)
    return redirect(url_for('main.login'))
