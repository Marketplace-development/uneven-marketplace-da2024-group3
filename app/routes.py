from flask import Flask, Blueprint, request, jsonify, render_template, session, redirect, url_for
from .models import db, users, records
import logging

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('overview_records.html')

@main.route('/get_records1', methods=['GET'])
def get_records1():
    try:
        # Fetch records from Supabase
        response = supabase.table('records').select('*').execute()

        # Check if data is returned
        if response.data:
            records = response.data  # List of records
        else:
            records = []  # No records found

        # Generate HTML for the listings
        records_html = ""
        if records:
            for record in records:
                records_html += f"""
                    <div class="listing">
                        <h3>{record['albumname']}</h3>
                        <p>Artist: {record['artist']}</p>
                        <p>Genre: {record['genre']}</p>
                        <p>Size: {record['size']}</p>
                        <p>Condition: {record['condition']}</p>
                        <p>Color: {record['colour']}</p>
                        <p>Description: {record.get('description', 'No description provided.')}</p>
                        <p>Price: €{record['price']:.2f}</p>
                    </div>
                """
        else:
            records_html = "<p>No listings available.</p>"

        return render_template('overview_records.html', records_html=records_html)
    except Exception as e:
        logging.error(f"Error fetching records: {e}")
        return render_template('overview_records.html', records_html="<p>Failed to load listings. Please try again later.</p>")

@main.route('/get_records2', methods=['GET'])
def get_records2():
    try:
        # Fetch records from Supabase
        response = supabase.table('records').select('*').execute()

        # Check if data is returned
        if response.data:
            records = response.data  # List of records
        else:
            records = []  # No records found

        # Generate HTML for the listings
        records_html = ""
        if records:
            for record in records:
                records_html += f"""
                    <div class="listing">
                        <h3>{record['albumname']}</h3>
                        <p>Artist: {record['artist']}</p>
                        <p>Genre: {record['genre']}</p>
                        <p>Size: {record['size']}</p>
                        <p>Condition: {record['condition']}</p>
                        <p>Color: {record['colour']}</p>
                        <p>Description: {record.get('description', 'No description provided.')}</p>
                        <p>Price: €{record['price']:.2f}</p>
                    </div>
                """
        else:
            records_html = "<p>No listings available.</p>"

        return render_template('dashboard_records.html', records_html=records_html)
    except Exception as e:
        logging.error(f"Error fetching records: {e}")
        return render_template('dashboard_records.html', records_html="<p>Failed to load listings. Please try again later.</p>")

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        address = request.form.get('address')  # Fetch the address from the form

        # Check if the username already exists
        user = users.query.filter_by(username=username).first()
        if user:
            return render_template("register.html", errors="Gebruiker al geregistreerd!")

        # Create a new user entry
        new_user = users(username=username, email=email, address=address)
        try:
            db.session.add(new_user)
            db.session.commit()

            # Store username in session and redirect to the dashboard
            session['username'] = username
            return redirect(url_for('main.dashboard'))
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
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')  # Render login page for GET requests


@main.route('/records', methods=['GET', 'POST'])
def records():
    if request.method == 'POST':
        data = request.json
        required_fields = ['albumname', 'artist', 'genre', 'size', 'condition', 'colour', 'price']

        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Field '{field}' is required"}), 400

        try:
            response = supabase.table('records').insert({
                'albumname': data['albumname'],
                'artist': data['artist'],
                'genre': data['genre'],
                'size': data['size'],
                'condition': data['condition'],
                'colour': data['colour'],
                'description': data.get('description', ''),
                'price': data['price'],
                'created_at': 'now()'
            }).execute()

            if response.status_code == 201:
                return jsonify({"message": "Record added successfully"}), 201
            else:
                return jsonify({"error": "Failed to add record"}), response.status_code

        except Exception as e:
            logging.error(f"Error adding record: {e}")
            return jsonify({"error": "Unable to add record"}), 500

    return render_template('records.html')

@main.route('/dashboard', methods=['GET'])
def dashboard():
    username = session.get('username')  # Retrieve the logged-in user's username
    if not username:
        return redirect(url_for('main.login'))  # Redirect to login if no user is logged in
    return render_template('dashboard_records.html')

@main.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('main.login'))  # Redirect to login page

