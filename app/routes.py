from flask import Flask, Blueprint, request, jsonify, render_template, session, redirect, url_for
from .models import db, users, records, libraries, libraryrecords
from . import supabase

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('overview_records.html')

@main.route('/get_records', methods=['GET'])
def get_records():
    try:
        response = supabase.table('records').select('*').execute()
        if response.data:
            return jsonify(response.data), 200
        else:
            return jsonify({"message": "No records found"}), 404
    except Exception as e:
        logging.error(f"Error fetching records: {e}")
        return jsonify({"error": "Unable to fetch records"}), 500

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        address = request.form.get('address')  # Fetch the address from the form
        telefoonnummer = request.form.get('telefoonnummer')

        # Check if the username already exists
        user = users.query.filter_by(username=username).first()
        if user:
            return render_template("register.html", errors="Gebruiker al geregistreerd!")

        # Create a new user entry
        new_user = users(username=username, email=email, address=address, telefoonnummer=telefoonnummer)
        try:
            db.session.add(new_user)
            db.session.commit()

            # Store username in session and redirect to the dashboard
            session['username'] = username
            return redirect(url_for('main.login'))
        except Exception as e:
            # Handle database errors or commit issues
            return render_template("register.html", errors="Er is een fout opgetreden bij registratie.")
    return render_template('register.html')

    
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')  # Fetch the username from the form

        # Check if the username exists in the database
        user = users.query.filter_by(username=username).first()
        if not user:
            return render_template("login.html", errors="Gebruiker niet gevonden!")  # User not found

        # Store username in session and redirect to the dashboard
        session['username'] = username
        session['userid'] = user.userid
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')  # Render login page for GET requests

@main.route('/dashboard', methods=['GET'])
def dashboard():
    username = session.get('username')  # Retrieve the logged-in user's username
    if not username:
        return redirect(url_for('main.login'))  # Redirect to login if no user is logged in
    return render_template('dashboard_records.html')

@main.route('/records', methods=['GET', 'POST'])
def manage_records():
    if request.method == 'POST':
        # Ensure user is logged in
        ownerid = session.get('userid')
        if not ownerid:
            return "User not logged in", 401

        # Extract form data
        albumname = request.form.get('albumname')
        artist = request.form.get('artist')
        genre = request.form.get('genre')
        size = request.form.get('size')
        condition = request.form.get('condition')
        colour = request.form.get('colour')
        Sellyesorno = request.form.get('Sellyesorno')
        price = request.form.get('price')
        description = request.form.get('description')

        # Insert record into Supabase
        supabase.table('records').insert({
            'albumname': albumname,
            'artist': artist,
            'genre': genre,
            'size': size,
            'condition': condition,
            'colour': colour,
            'Sellyesorno': Sellyesorno,
            'price': price,
            'description': description,
            'ownerid': ownerid  # Attach the logged-in user's ID
        }).execute()
        return redirect(url_for('main.dashboard'))

    return render_template('records.html')



@main.route('/transactions', methods=['GET', 'POST'])
def handle_transactions():
    if request.method == 'POST':
        recordid = request.form.get('recordid')

        # Delete the selected record from Supabase
        supabase.table('records').delete().eq('recordid', recordid).execute()

        return "Record gekocht!", 200  # Or redirect if needed

    # Fetch all records for the dropdown
    records = supabase.table('records').select('recordid, albumname, artist').execute().data

    # Dynamically generate options for the dropdown
    records_options = ''.join(
        f'<option value="{record["recordid"]}">{record["albumname"]} - {record["artist"]}</option>'
        for record in records
    )

    # Serve HTML with embedded options
    return render_template('transactions.html')


@main.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('main.index'))  # Redirect to login page

@main.route('/library', methods=['GET'])
def library_view():
    return render_template('zoek.html')


@main.route('/koop_1plaat/<int:recordid>', methods=['GET'])
def koop_1plaat(recordid):
    record = records.query.get(recordid)
    if not record:
        return "Record not found", 404

    return render_template('koop_1plaat.html', record=record)
    
@main.route('/delete_record/<int:recordid>', methods=['POST'])
def delete_record(recordid):
    try:
        # Delete the record from Supabase
        supabase.table('records').delete().eq('recordid', recordid).execute()
        return render_template('transactions.html')  # Redirect to the transactions page
    except Exception as e:
        logging.error(f"Error deleting record: {e}")
        return "Fout bij het verwijderen van de plaat.", 500

@main.route('/get_username', methods=['GET'])
def get_username():
    # Controleer of een gebruiker is ingelogd
    username = session.get('username')
    if username:
        return jsonify({"username": username}), 200
    else:
        return jsonify({"error": "Not logged in"}), 401

@main.route('/my_library', methods=['GET'])
def my_library():
    # Haal de ingelogde gebruiker op
    userid = session.get('userid')  # De unieke ID van de ingelogde gebruiker
    if not userid:
        return redirect(url_for('main.login'))  # Verwijs naar de loginpagina als de gebruiker niet is ingelogd

    try:
        # Haal alle records op die bij deze gebruiker horen
        response = supabase.table('records').select('*').eq('ownerid', userid).execute()
        if response.data:
            records = response.data
        else:
            records = []
    except Exception as e:
        logging.error(f"Error fetching user records: {e}")
        records = []

    return render_template('my_library.html', records=records)

@main.route('/library/search', methods=['GET'])
def search_library():
    # Haal de gebruikersnaam op uit de queryparameter
    username = request.args.get('username')

    if not username:
        # Als er geen gebruikersnaam is opgegeven, laad de zoekpagina opnieuw met een foutmelding
        return render_template('zoek.html', error="Vul een gebruikersnaam in.")

    try:
        # Zoek de gebruiker op basis van de opgegeven gebruikersnaam
        user_response = supabase.table('users').select('userid').eq('username', username).single().execute()

        if not user_response.data:
            # Als de gebruiker niet bestaat
            return render_template('zoek.html', error="Gebruiker niet gevonden.")

        # Haal de userid op van de gevonden gebruiker
        user_id = user_response.data['userid']

        # Zoek records die aan deze gebruiker toebehoren
        records_response = supabase.table('records').select('*').eq('ownerid', user_id).execute()

        # Controleer of er records zijn gevonden
        library_records = records_response.data if records_response.data else []

    except Exception as e:
        logging.error(f"Error fetching library records: {e}")
        return render_template('zoek.html', error="Er is een fout opgetreden bij het ophalen van de bibliotheek.")

    # Render de bibliotheekpagina met de records
    return render_template('library.html', username=username, library_records=library_records)