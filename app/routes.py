from flask import Flask, Blueprint, request, jsonify, render_template, session, redirect, url_for
from .models import db, users, records
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

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        address = data.get('address')

        if not all([username, email, address]):
            return jsonify({"error": "All fields are required"}), 400

        try:
            response = supabase.table('users').insert({
                'username': username,
                'email': email,
                'address': address,
                'created_at': 'now()'
            }).execute()

            if response.data:
                return jsonify({"message": "User registered successfully"}), 201
            return jsonify({"error": "Failed to register user"}), 500
        except Exception as e:
            logging.error(f"Error registering user: {e}")
            return jsonify({"error": "Server error"}), 500

    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')

        if not username:
            return jsonify({"error": "Username is required"}), 400

        try:
            response = supabase.table('users').select('*').eq('username', username).execute()

            if response.data:
                session['username'] = username
                return jsonify({"message": "Login successful"}), 200

            return jsonify({"error": "Invalid username"}), 401
        except Exception as e:
            logging.error(f"Error during login: {e}")
            return jsonify({"error": "Server error"}), 500

    return render_template('login.html')


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
    return render_template('dashboard_records.html')
