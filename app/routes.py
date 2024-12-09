from flask import Flask, Blueprint, request, jsonify, render_template, session, redirect, url_for, flash, current_app
from .models import db, users, records, libraries, libraryrecords, reviews, transactions, favorites
from sqlalchemy import func
from . import supabase
import logging
from werkzeug.utils import secure_filename
import uuid
import os


main = Blueprint('main', __name__)

def generate_unique_filename(filename):
    extension = os.path.splitext(filename)[1]
    unique_name = str(uuid.uuid4()) + extension  # Voeg een unieke UUID toe
    return unique_name

@main.route('/')
def index():
    return render_template('overview_records.html')

@main.route('/overview_records', methods=['GET'])
def overview_records():
    return render_template('overview_records.html')

@main.route('/to_login')
def to_login():
    return render_template('login.html')

@main.route('/to_register')
def to_register():
    return render_template('register.html')


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
        address = request.form.get('address')
        telefoonnummer = request.form.get('telefoonnummer')

        errors = []

        # Controleer of de gebruikersnaam al bestaat
        if users.query.filter_by(username=username).first():
            errors.append("Username already exists, please choose another option.")

        # Controleer of het e-mailadres al bestaat
        if users.query.filter_by(email=email).first():
            errors.append("There is already an existing account for this email address.")

        # Als er fouten zijn, toon ze
        if errors:
            return render_template("register.html", errors=errors)

        # Maak een nieuwe gebruiker aan
        new_user = users(username=username, email=email, address=address, telefoonnummer=telefoonnummer)
        try:
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username  # Sla de gebruikersnaam op in de sessie

            flash("Welcome! You've registered your Spinnback account. You can now login with your username.", "success")
            return redirect(url_for('main.login'))  # Verwijs naar de loginpagina
        except Exception as e:
            return render_template("register.html", errors=[f"Fout bij registratie: {str(e)}"])

    return render_template("register.html")


    
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')  # Haal de gebruikersnaam uit het formulier

        # Controleer of de gebruikersnaam bestaat in de database
        user = users.query.filter_by(username=username).first()
        if not user:
            # Stuur door naar de registratiepagina met een foutmelding
            return render_template("register.html", errors="Username not found. Register your account first please.")  # Foutmelding als gebruiker niet bestaat

        # Sla de gebruikersnaam en userid op in de sessie en stuur door naar het dashboard
        session['username'] = username
        session['userid'] = user.userid
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')  # Render de loginpagina voor GET verzoeken


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

        # Verwerk de afbeelding
        image = request.files.get('image')
        if image:
            print(f"Bestand ontvangen: {image.filename}")  # Log om te controleren
        else:
            print("Geen bestand ontvangen")
        image_url = None
        if image:
            # Maak een veilige bestandsnaam
            filename = f"{uuid.uuid4().hex}_{secure_filename(image.filename)}"
            # Upload het bestand naar Supabase
            bucket = supabase.storage.from_('images')
            file_path = f"records/{filename}"
            file_content = image.read()
            upload_response = bucket.upload(file_path, file_content)
            image_url = f"https://ydlbtcbabebtcajmvoyl.supabase.co/storage/v1/object/public/images/{file_path}"



        # Maak een nieuw record aan
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
            ownerid=ownerid,
            image=image_url  # Bewaar de URL van de afbeelding
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
    # Fetch the record
    record = records.query.get(recordid)
    if not record:
        return "Record not found", 404

    # Fetch the seller (user) details based on the ownerid
    seller = users.query.get(record.ownerid)
    if not seller:
        return "Seller not found", 404

    # Pass the seller's username to the template
    return render_template('koop_1plaat.html', record=record, seller_username=seller.username)

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

        # Check of de koper de eigenaar van het record is
        if record.ownerid == buyer_id:
            logging.error("Je kunt je eigen plaat niet kopen.")
            return "Je kunt je eigen plaat niet kopen", 400

        owner = record.ownerid

        # Maak de transactie
        new_transaction = transactions(sellerid=owner, buyerid=buyer_id, recordid=recordid)
        db.session.add(new_transaction)

        # Update de record
        record.ownerid = buyer_id  # Verander de eigenaar
        record.Sellyesorno = False  # Stel Sellyesorno in op False
        record.price = None  # Verwijder de prijs
        db.session.commit()

        logging.info(f"Transactie succesvol toegevoegd voor record {recordid} door gebruiker {buyer_id}.")

        # Redirect naar de edit_after_purchase pagina
        return render_template('edit_after_purchase.html', record=record)


    except Exception as e:
        logging.error(f"Fout bij transactie: {e}")
        return "Er is een fout opgetreden", 500


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

    # Haal de afbeeldings-URL van elke record (indien beschikbaar)
    for record in records:
        record['image_url'] = record.get('image', None)  # Voeg de afbeelding toe als het bestaat

    return render_template('my_library.html', records=records)


@main.route('/library/search', methods=['GET'])
def search_library():
    username_query = request.args.get('username', '')

    try:
        # Zoek gebruikers op met een gedeeltelijke overeenkomst
        users_response = supabase.table('users').select('username').ilike('username', f'%{username_query}%').execute()

        if not users_response.data:
            return render_template('library.html', users=[])

        users = [{'username': user['username']} for user in users_response.data]

        return render_template('library.html', users=users)

    except Exception as e:
        logging.error(f"Error fetching user libraries: {e}")
        return render_template('library.html', users=[], error="An error occurred while searching.")


@main.route('/library/<username>', methods=['GET'])
def user_library(username):
    try:
        # Zoek de gebruiker op basis van de opgegeven gebruikersnaam
        user_response = supabase.table('users').select('userid').eq('username', username).single().execute()

        if not user_response.data:
            return render_template('library.html', library_records=[], username=None, error="User not found.")

        # Haal de userid van de gevonden gebruiker op
        user_id = user_response.data['userid']

        # Zoek records die aan deze gebruiker toebehoren
        records_response = supabase.table('records').select('*').eq('ownerid', user_id).execute()
        library_records = records_response.data if records_response.data else []

    except Exception as e:
        logging.error(f"Error fetching library for user {username}: {e}")
        return render_template('library.html', library_records=[], username=None, error="An error occurred.")

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
            image_url = record.image if record.image else None
            purchases_data.append({
                "transaction_id": transaction.transactionid,
                "record_id": record.recordid,
                "album_name": record.albumname,
                "artist": record.artist,
                "condition": record.condition,
                "price": record.price,
                "date": transaction.created_at,  # Dit moet mogelijk aangepast worden naar een datumveld in "transactions"
                "image_url": image_url
            })

    # Render de HTML-template met de verzamelde gegevens
    return render_template('my_purchases.html', purchases=purchases_data)

@main.route('/my_purchases')
def return_my_purchases():
    # code voor de pagina my_purchases
    return render_template('my_purchases.html')



@main.route('/my_sold_records', methods=['GET'])
def my_sold_records():
    # Haal de ingelogde gebruiker op uit de sessie
    logged_in_user_id = session.get('userid')

    if not logged_in_user_id:
        return "User not logged in", 401  # Geef een foutmelding als de gebruiker niet is ingelogd

    # Query alle transacties waarbij de gebruiker de verkoper is
    sold_transactions = transactions.query.filter_by(sellerid=logged_in_user_id).all()

    # Controleer of er transacties zijn gevonden
    if not sold_transactions:
        return render_template('my_sold_records.html', sold_records=[])

    # Haal de bijbehorende records op voor elke transactie
    sold_records_data = []
    for transaction in sold_transactions:
        record = records.query.get(transaction.recordid)  # Haal het record op met de ID
        if record:
            image_url = record.image if record.image else None  # Haal afbeelding op als deze bestaat
            sold_records_data.append({
                "transaction_id": transaction.transactionid,
                "record_id": record.recordid,
                "album_name": record.albumname,
                "artist": record.artist,
                "condition": record.condition,
                "price": record.price,
                "date_sold": transaction.created_at,  # Datum van de transactie
                "image_url": image_url  # Voeg de afbeelding toe
            })

    # Render de HTML-template met de verzamelde gegevens
    return render_template('my_sold_records.html', sold_records=sold_records_data)



@main.route('/my_sold_records')
def return_my_sold_records():
    # code voor de pagina my__sold_records
    return render_template('my_sold_records.html')


@main.route('/write_review/<int:transaction_id>')
def write_review(transaction_id):
    # Controleer of er al een review is voor deze transaction_id
    existing_review = reviews.query.filter_by(transactionid=transaction_id).first()

    if existing_review:
        # Er is al een review, toon een melding en redirect naar 'my_purchases'
        flash('A review has already been written for this purchase.', 'error')
        return redirect(url_for('main.return_my_purchases'))
    
    # Als er geen review is, toon dan de schrijf-review pagina
    return render_template('write_review.html', transaction_id=transaction_id)

@main.route('/submit_review', methods=['POST'])
def submit_review():
    # Haal de gegevens van het formulier op
    transaction_id = request.form.get('transaction_id')
    review_score = request.form.get('review_score')
    reasoning = request.form.get('reasoning')

    # Voeg de review toe aan de database
    new_review = reviews(
        transactionid=transaction_id,
        reviewscore=review_score,
        reasoning=reasoning
    )
    db.session.add(new_review)
    db.session.commit()

    # Flash message voor succesvolle inzending
    flash('Review successfully submitted!', 'success')

    # Redirect naar een bevestigingspagina of terug naar de aankopen
    return redirect(url_for('main.return_my_purchases'))



@main.route('/review/<int:transaction_id>')
def watch_review(transaction_id):
    # Controleer of er al een review is voor deze transaction_id
    existing_review = reviews.query.filter_by(transactionid=transaction_id).first()

    if not existing_review:
        # Er is geen review
        flash('There is no review (yet) for this transaction', 'warning')
        return redirect(url_for('main.return_my_sold_records'))
    
    transaction = transactions.query.filter_by(transactionid=transaction_id).first()
    
    # Haal de review voor de transactie op
    review = reviews.query.filter_by(transactionid=transaction_id).first()
    
    if not review:
        return "Review not found for this transaction", 404

    # Geef de transactie- en reviewinformatie door aan de template
    return render_template('watch_review.html', transaction=transaction, review=review)


@main.route('/my_rating')
def my_rating():
    # Ensure the user is logged in
    # Haal de ingelogde gebruiker op uit de sessie
    logged_in_user_id = session.get('userid')

    if not logged_in_user_id:
        return "User not logged in", 401  # Geef een foutmelding als de gebruiker niet is ingelogd

    # Query to find all reviews where the sellerid matches the logged-in user's userid
    user_reviews = db.session.query(reviews).join(transactions).filter(transactions.sellerid == logged_in_user_id).all()

    # Calculate the average review score
    average_score = db.session.query(func.avg(reviews.reviewscore)).join(transactions).filter(transactions.sellerid == logged_in_user_id).scalar()

    return render_template('my_rating.html', reviews=user_reviews, average_score=average_score)

if __name__ == '__main__':
    main.run(debug=True)

@main.route('/view_seller_rating/<int:seller_id>')
def view_seller_rating(seller_id):
    # Get the `recordid` from the query parameter
    recordid = request.args.get('recordid')

    # Query to find all reviews for the given seller
    seller_reviews = (
        db.session.query(reviews)
        .join(transactions)
        .filter(transactions.sellerid == seller_id)
        .all()
    )

    # Calculate the average review score for the seller
    average_score = (
        db.session.query(func.avg(reviews.reviewscore))
        .join(transactions)
        .filter(transactions.sellerid == seller_id)
        .scalar()
    )

    return render_template(
        'view_seller_rating.html',
        reviews=seller_reviews,
        average_score=average_score,
        recordid=recordid,  # Pass the recordid to the template
    )

@main.route('/edit_1plaat/<int:record_id>', methods=['GET', 'POST'])
def edit_1plaat(record_id):
    # Ensure user is logged in
    ownerid = session.get('userid')
    if not ownerid:
        return "User not logged in", 401

    # Fetch the record
    record = records.query.filter_by(recordid=record_id, ownerid=ownerid).first()
    if not record:
        return "Record not found or access denied", 404

    if request.method == 'POST':
        # Update the record with form data
        record.albumname = request.form.get('albumname', record.albumname)
        record.artist = request.form.get('artist', record.artist)
        record.genre = request.form.get('genre', record.genre)
        record.size = request.form.get('size', record.size)
        record.condition = request.form.get('condition', record.condition)
        record.colour = request.form.get('colour', record.colour)
        record.Sellyesorno = request.form.get('Sellyesorno').lower() == 'true'
        record.price = request.form.get('price', type=float) if record.Sellyesorno else None
        record.description = request.form.get('description', record.description)

        try:
            db.session.commit()
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            logging.error(f"Error updating record: {e}")
            return "Error updating record", 500

    # Render the edit form with pre-filled data
    return render_template('edit_1plaat.html', record=record)


@main.route('/edit_after_purchase/<int:recordid>', methods=['GET', 'POST'])
def edit_after_purchase(recordid):
    record = records.query.get(recordid)
    if not record:
        return "Record not found", 404

    # Verkrijg de beslissing van de gebruiker
    decision = request.form.get('decision')
    
    # Als de gebruiker heeft gekozen om te verkopen
    if decision == 'sell':
        price = request.form.get('price')
        if price:
            price = float(price)
            record.Sellyesorno = True
            record.price = price
        else:
            return "Price is required when selling.", 400
    
    # Als de gebruiker heeft gekozen om het record te bewaren, doe dan niets
    elif decision == 'keep':
        pass

    # Sla de wijzigingen op
    db.session.commit()

    # Correcte redirect naar dashboard of een andere bestemming
    return redirect(url_for('main.dashboard'))  # Of andere bestemming




@main.route('/get_recommendations', methods=['GET'])
def get_recommendations():
    try:
        # Haal de ingelogde gebruiker op
        userid = session.get('userid')
        if not userid:
            return jsonify({"error": "User not logged in"}), 401

        # Haal eerdere aankopen van de gebruiker op
        user_transactions = transactions.query.filter_by(buyerid=userid).all()
        if not user_transactions:
            return jsonify({"message": "No purchases found"}), 404

        # Verzamel genres, conditions en prijzen van eerdere aankopen
        purchased_records = [records.query.get(transaction.recordid) for transaction in user_transactions if records.query.get(transaction.recordid)]
        genres = set(record.genre for record in purchased_records)
        conditions = set(record.condition for record in purchased_records)
        prices = [record.price for record in purchased_records if record.price]

        if not prices:
            return jsonify({"message": "No price data available for recommendations"}), 404

        avg_price = sum(prices) / len(prices)
        price_range = (max(prices) - min(prices)) * 0.5  # 50% van het prijsbereik

        # Haal beschikbare records op
        available_records = records.query.filter(records.Sellyesorno == True, records.ownerid != userid).all()

        # Filter op aanbevelingen (met dynamische prijsrange)
        recommendations = [
            record for record in available_records
            if (record.genre in genres or  # Match op genre
                record.condition in conditions) and  # Of match op conditie
               abs(record.price - avg_price) <= price_range  # Dynamische prijstolerantie
        ]

        # Sorteer aanbevelingen op overeenkomsten met genres en condities
        recommendations.sort(
            key=lambda record: (
                (record.genre in genres) +  # Meer punten voor overeenkomend genre
                (record.condition in conditions)  # Meer punten voor overeenkomende conditie
            ),
            reverse=True
        )

        # Beperk tot 3 aanbevelingen
        recommendations = recommendations[:3]

        # Formatteer als JSON
        return jsonify([
            {
                "recordid": record.recordid,
                "albumname": record.albumname,
                "artist": record.artist,
                "size" : record.size,
                "genre": record.genre,
                "condition": record.condition,
                "price": record.price
            }
            for record in recommendations
        ]), 200

    except Exception as e:
        logging.error(f"Error fetching recommendations: {e}")
        return jsonify({"error": "Unable to fetch recommendations"}), 500

@main.route('/update_favorite_status', methods=['POST'])
def update_favorite_status():
    if 'userid' not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    userid = session['userid']
    recordid = data.get('recordid')
    is_favorite = data.get('isFavorite')

    if not recordid:
        return jsonify({"error": "Record ID is required"}), 400

    try:
        # Controleer of de favoriet al bestaat
        favorite = favorites.query.filter_by(userid=userid, recordid=recordid).first()

        if is_favorite:
            # Voeg toe als het nog niet bestaat
            if not favorite:
                new_favorite = favorites(userid=userid, recordid=recordid)
                db.session.add(new_favorite)
        else:
            # Verwijder als het bestaat
            if favorite:
                db.session.delete(favorite)

        db.session.commit()
        return jsonify({"success": True}), 200
    except Exception as e:
        logging.error(f"Error updating favorite status: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    
@main.route('/my_favorites', methods=['GET'])
def my_favorites():
    if 'userid' not in session:
        return redirect(url_for('login'))  # Redirect als de gebruiker niet is ingelogd

    userid = session['userid']

    try:
        # Haal de favorietenrecords op met een join tussen favorites en records
        query = (
            supabase
            .from_('favorites')
            .select('recordid, records(*)')
            .eq('userid', userid)
            .execute()
        )

        # Haal de records op uit de response
        favorite_records = []
        for item in query.data:
            if item.get('records'):
                favorite_records.append(item['records'])

        return render_template('my_favorites.html', records=favorite_records)

    except Exception as e:
        print(f"Error fetching favorites: {e}")
        return render_template('my_favorites.html', records=[], error="Error fetching favorites")

@main.route('/get_favorites', methods=['GET'])
def get_favorites():
    if 'userid' not in session:
        return jsonify({"error": "User not logged in"}), 401

    userid = session['userid']

    try:
        # Haal de favorieten op voor de ingelogde gebruiker
        favorites_list = favorites.query.filter_by(userid=userid).all()
        favorite_record_ids = [favorite.recordid for favorite in favorites_list]

        return jsonify(favorite_record_ids), 200
    except Exception as e:
        logging.error(f"Error fetching favorites: {e}")
        return jsonify({"error": "Internal Server Error"}), 500