from flask import Flask, Blueprint, request, jsonify, render_template, session, redirect, url_for
from .models import db, users, records, libraries, libraryrecords
from . import supabase
import logging

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

@main.route('/get_records_sellyes', methods=['GET'])
def get_records_sellyes():
    try:
        # Get the logged-in user's ID from the session
        userid = session.get('userid')  

        if not userid:
            return jsonify({"error": "User not logged in"}), 401

        # Fetch all records from Supabase
        response = supabase.table('records').select('*').execute()

        if not response.data:
            return jsonify({"message": "No records found"}), 404

        # Filter records where Sellyesorno is True and ownerid is not the logged-in user
        filteredrecords = [
            record for record in response.data 
            if record.get('Sellyesorno') and record.get('ownerid') != userid
        ]

        if filteredrecords:
            return jsonify(filteredrecords), 200
        else:
            return jsonify({"message": "No matching records found"}), 404
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
        Sellyesorno = request.form.get('Sellyesorno').lower() == 'true'  # Convert to boolean
        price = request.form.get('price', type=float) if Sellyesorno else None  # Price only required if selling
        description = request.form.get('description')

        # Create a new record
        new_record = records(
            albumname=albumname,
            artist=artist,
            genre=genre,
            size=size,
            condition=condition,
            colour=colour,
            Sellyesorno=Sellyesorno,
            price=price,
            description=description,
            ownerid=ownerid
        )

        try:
            db.session.add(new_record)
            db.session.commit()
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            logging.error(f"Error saving record: {e}")
            return "Error saving record", 500

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

from .models import transactions  
@main.route('/create_transaction/<int:recordid>', methods=['POST'])
def create_transaction(recordid):
    try:
        buyer_id = session.get('userid')
        if not buyer_id:
            logging.error("Geen gebruiker ingelogd.")
            return redirect(url_for('main.login'))

        # Haal het record op
        record = records.query.get(recordid)
        if not record:
            logging.error(f"Record met ID {recordid} niet gevonden.")
            return "Record niet gevonden", 404
        
        owner = record.ownerid

        # Check of de koper de eigenaar van het record is
        if record.ownerid == buyer_id:
            logging.error("Je kunt je eigen plaat niet kopen.")
            return "Je kunt je eigen plaat niet kopen", 400

        # Maak de transactie
        new_transaction = transactions(sellerid=owner, buyerid=buyer_id, recordid=recordid)
        db.session.add(new_transaction)

        # Update de ownerid van de record
        record.ownerid = buyer_id
        db.session.commit()
        logging.info(f"Transactie succesvol toegevoegd voor record {recordid} door gebruiker {buyer_id}.")

        return redirect(url_for('main.dashboard'))

    except Exception as e:
        logging.error(f"Fout bij het verwerken van de aankoop: {e}")
        db.session.rollback()
        return "Fout bij het verwerken van de aankoop", 500



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


@main.route('/my_purchases', methods=['GET'])
def get_my_purchases():
    # Haal de ingelogde gebruiker op uit de sessie
    logged_in_user_id = session.get('userid')

    if not logged_in_user_id:
        return "User not logged in", 401  # Geef een foutmelding als de gebruiker niet is ingelogd

    # Query alle transacties waarbij de gebruiker de koper is
    user_transactions = transactions.query.filter_by(buyerid=logged_in_user_id).all()

    # Controleer of er transacties zijn gevonden
    if not user_transactions:
        return render_template('my_purchases.html', purchases=[])

    # Haal de bijbehorende records op voor elke transactie
    purchases_data = []
    for transaction in user_transactions:
        record = records.query.get(transaction.recordid)  # Haal het record op met de ID
        if record:
            purchases_data.append({
                "transaction_id": transaction.transactionid,
                "record_id": record.recordid,
                "album_name": record.albumname,
                "artist": record.artist,
                "condition": record.condition,
                "price": record.price,
                "date": transaction.created_at  # Dit moet mogelijk aangepast worden naar een datumveld in "transactions"
            })

    # Render de HTML-template met de verzamelde gegevens
    return render_template('my_purchases.html', purchases=purchases_data)


@main.route('/my_sold_items', methods=['GET'])
def get_my_sold_items():
    # Haal de ingelogde gebruiker op uit de sessie
    logged_in_user_id = session.get('userid')

    if not logged_in_user_id:
        return "User not logged in", 401  # Geef een foutmelding als de gebruiker niet is ingelogd

    # Query alle transacties waarbij de gebruiker de koper is
    user_transactions = transactions.query.filter_by(buyerid=logged_in_user_id).all()

    # Controleer of er transacties zijn gevonden
    if not user_transactions:
        return render_template('my_purchases.html', purchases=[])

    # Haal de bijbehorende records op voor elke transactie
    purchases_data = []
    for transaction in user_transactions:
        record = records.query.get(transaction.recordid)  # Haal het record op met de ID
        if record:
            purchases_data.append({
                "transaction_id": transaction.transactionid,
                "record_id": record.recordid,
                "album_name": record.albumname,
                "artist": record.artist,
                "condtion": record.condition,
                "price": record.price,
                "date": transaction.created_at  # Dit moet mogelijk aangepast worden naar een datumveld in "transactions"
            })

    # Render de HTML-template met de verzamelde gegevens
    return render_template('my_purchases.html', purchases=purchases_data)

