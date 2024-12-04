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

@main.route('/library/search', methods=['GET'])
def search_library_view():
    username = request.args.get('username')

    # Zoek de gebruiker in de database
    user = users.query.filter_by(username=username).first()
    if not user:
        return render_template('zoek.html', error="Gebruiker niet gevonden!")

    # Haal de bibliotheekrecords op
    library_records = (
        db.session.query(records)
        .join(libraryrecords, libraryrecords.recordid == records.recordid)
        .join(libraries, libraries.libraryid == libraryrecords.libraryid)
        .filter(libraries.userid == user.userid)
        .all()
    )

    return render_template('library.html', username=username, library_records=library_records)

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
