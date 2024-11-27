from flask import Blueprint, request, redirect, url_for, render_template, session, jsonify
from .models import db, Users, Libraries, Buyers, Records, Sellers, LibraryRecords, Transactions, Reviews

main = Blueprint('main', __name__)  

@main.route('/')
def index():
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
        if user:
            records = Records.query.filter_by(ownerid=user.userid).all()  
            return render_template('start_records.html', username=user.username, listings=records)
    return render_template('start_records.html', username=None)

@main.route('/start_listing')
def start_listing():
    if 'user_id' in session:
        user = Users.query.get(session['user_id'])
        if user:  
            return render_template('start_records.html', username=user.username)
    else:
        return render_template('start_records.html', username=None)

#register
@main.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template("start_records.html", errors="Gebruiker al geregistreerd!")
        else:
            new_user = Users(username=username, email = email)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect(url_for('main.dashboard'))
    return render_template('register.html')
#login
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        user = Users.query.filter_by(username=username, email=email).first()
        if user:
            session['username'] = username
            return redirect(url_for('main.dashboard'))
        else:
            return render_template('start_records.html', error ="Ongeldige Gebruikersnaam")
    return render_template('login.html')
@main.route('/dashboard')
def dashboard():
    username = session.get('username')
    return render_template('dashboard_records.html', username = username)

@main.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.index'))

@main.route('/get_records', methods=['GET'])
def get_records():
    records_list = Records.query.all()  # Fetch all records
    listings_data = [
        {
            "albumname": record.albumname,
            "artist": record.artist,
            "genre": record.genre,
            "size": record.size,
            "condition": record.condition,
            "color": record.color,
            "description": record.description,
            "price": record.price,
        }
        for record in records_list
    ]
    return jsonify(records_list)

@main.route('/verkopen', methods=['GET','POST'])
def verkopen():
    if request.method == 'POST':
        data = request.json

        # Validate the input data
        required_fields = ["recordID", "minPrice", "condition", "color", "size"]
        for field in required_fields:
            if field not in data:
                return jsonify({"Fout": f"Veld '{field}' verplicht in te vullen."}), 400

        # Add the new listing
        new_listing = {
            "recordID": data["recordID"],
            "minPrice": data["minPrice"],
            "condition": data["condition"],
            "color": data["color"],
            "size": data["size"]
        }
        listings.append(new_listing)

        return jsonify({"message": "Plaat succesvol aangeboden!"}), 201
    return render_template('verkopen.html')


@main.route('/bieden', methods=['GET', 'POST'])
def transactions():
    if request.method == 'POST':
        bid = request.form['bid']
        # Verwerk het bod hier (bijvoorbeeld opslaan in de database)
        return render_template('transactions.html', message=f"Je bod van {bid} is succesvol geplaatst!")
    return render_template('transactions.html')

