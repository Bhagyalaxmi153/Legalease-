from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta



app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Configure SMTP for email sending
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
EMAIL_SENDER = "roopachinthala08@gmail.com"
EMAIL_PASSWORD = "hdel lteg vgds twbv"

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="roopa",
        database="maindb"
    )





# Function to send OTP email
def send_otp_email(email, otp):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = email
        msg['Subject'] = "Your OTP Code for Registration"

        body = f"Your OTP code is {otp}. This OTP is valid for 5 minutes."
        msg.attach(MIMEText(body, 'plain'))

        # Using SSL connection
        server = smtplib.SMTP_SSL(SMTP_SERVER, 465)  # Change to SSL and port 465
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, email, msg.as_string())
        server.quit()
        print("OTP sent successfully.")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication error: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

# Function to generate OTP
def generate_otp():
    return str(random.randint(100000, 999999))  # Generates a 6-digit OTP

# Route to send OTP
@app.route('/send_otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({"message": "Email is required!"}), 400

        otp = generate_otp()  # Generate OTP
        session['otp'] = otp  # Store OTP in session
        session['email'] = email  # Store email in session for verification

        success = send_otp_email(email, otp)

        if success:
            return jsonify({"message": "OTP sent successfully!"}), 200
        else:
            return jsonify({"message": "Failed to send OTP"}), 500
    except Exception as e:
        print(f"Error in sending OTP: {e}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Route to verify OTP
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    user_otp = data['otp']
    stored_otp = session.get('otp')

    if user_otp == stored_otp:
        session.pop('otp')  # Remove OTP from session after verification
        session['emailVerified'] = 'true'  # Mark email as verified

        return jsonify({"message": "OTP verified successfully!", "status": "success"}), 200
    else:
        return jsonify({"message": "Invalid OTP, try again", "status": "error"}), 400


# Route to serve the UserRegistration.html page
@app.route('/UserRegistration.html')
def user_registration():
    return render_template('UserRegistration.html')

# Route to serve the LspRegistration.html page
@app.route('/LspRegistration.html')
def lsp_registration():
    return render_template('LspRegistration.html')

# Route to handle client registration form submission
@app.route('/register/client', methods=['POST'])
def register_client():
    if 'email' not in session or session.get('emailVerified') != 'true':
        return jsonify({"message": "Email verification required!"}), 400

    fields = {
        'fullname': request.form['fullname'],
        'username': request.form['username'],
        'email': session.get('email'),
        'password': request.form['password'],
        'confirm_password': request.form['confirm_password'],
        'phone_number': request.form['phone_number'],
        'state': request.form['state'],
        'city': request.form['city'],
    }

    if fields['password'] != fields['confirm_password']:
        return jsonify({"message": "Password and Confirm Password do not match!"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        values = (
            fields['fullname'],
            fields['username'],
            fields['email'],
            fields['password'],
            fields['phone_number'],
            fields['state'],
            fields['city']
        )

        cursor.execute(''' 
            INSERT INTO clients (full_name, username, email, password, phone_number, state, city)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', values)
        conn.commit()

        # Redirect to login page after successful registration
        return redirect(url_for('login'))

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": f"Error: {err}"}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Route to handle LSP registration form submission
# Route to handle OTP sending for LSP registration
@app.route('/send_otp_lsp', methods=['POST'])
def send_otp_lsp():
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({"message": "Email is required!"}), 400

        otp = generate_otp()  # Generate OTP
        session['otp'] = otp  # Store OTP in session
        session['email'] = email  # Store email in session for verification

        success = send_otp_email(email, otp)

        if success:
            return jsonify({"message": "OTP sent successfully!"}), 200
        else:
            return jsonify({"message": "Failed to send OTP"}), 500
    except Exception as e:
        print(f"Error in sending OTP: {e}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Route to handle OTP verification for LSP registration
@app.route('/verify_otp_lsp', methods=['POST'])
def verify_otp_lsp():
    data = request.get_json()
    user_otp = data['otp']
    stored_otp = session.get('otp')

    if user_otp == stored_otp:
        session.pop('otp')  # Remove OTP from session after verification
        session['emailVerified'] = 'true'  # Mark email as verified

        return jsonify({"message": "OTP verified successfully!", "status": "success"}), 200
    else:
        return jsonify({"message": "Invalid OTP, try again", "status": "error"}), 400

# Route to handle LSP registration form submission
# Route to handle LSP registration form submission
@app.route('/register/lsp', methods=['POST'])
def register_lsp():
    if 'email' not in session or session.get('emailVerified') != 'true':
        print("Email verification required!")
        return jsonify({"message": "Email verification required!"}), 400

    # Log all input fields for debugging
    full_name = request.form['fullname']
    username = request.form['username']
    email = session.get('email')  # Use verified email from session
    password = request.form['password']
    phone_number = request.form['phone_number']
    bar_association_number = request.form['bar_association_number']
    practice_area = request.form['practice_area']
    language_comfortable = request.form['language_comfortable']
    profile_description = request.form['profile_description']
    state = request.form['state']
    city = request.form['city']
    consultation_type = request.form['consultation_type']
    linkedin_link = request.form.get('linkedin_link', None)

    # New fields
    google_meet_link = request.form.get('google_meet_link', None)
    location = request.form['location']
    court_jurisdiction = request.form['court_jurisdiction']
    cases_solved = request.form['cases_solved']
    years_experience = request.form['years_experience']

    print(f"Received data: {full_name}, {username}, {email}, {phone_number}, {bar_association_number}, {practice_area}, {language_comfortable}, {profile_description}, {state}, {city}, {consultation_type}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the bar association number exists in the LegalServiceProviders table
        cursor.execute("SELECT EnrollmentNo FROM LegalServiceProviders WHERE EnrollmentNo = %s", (bar_association_number,))
        bar_association = cursor.fetchone()

        if not bar_association:
            # Bar Association number doesn't exist, show error message
            return jsonify({"message": "Authentication required. Please contact us to request access with your bar association,enrolment number and full name"}), 400

        # Proceed with checking if the email is already registered
        cursor.execute("SELECT id FROM lsps WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            print(f"Email already registered: {email}")
            return jsonify({"message": "Email already registered!"}), 400

        # Insert the new LSP record into the database
        query = """
        INSERT INTO lsps (
            full_name, username, email, password, phone_number, bar_association_number, practice_area,
            language_comfortable, profile_description, state, city, consultation_type, linkedin_link,
            google_meet_link, location, court_jurisdiction, cases_solved, years_experience
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            full_name, username, email, password, phone_number, bar_association_number,
            practice_area, language_comfortable, profile_description, state, city, consultation_type,
            linkedin_link, google_meet_link, location, court_jurisdiction, cases_solved, years_experience
        )

        cursor.execute(query, values)
        conn.commit()
        print("LSP registration successful")
        return jsonify({"message": "LSP registered successfully!"}), 201

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        conn.rollback()
        return jsonify({"error": str(err)}), 500

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()




# Route to serve the homepage (or login page)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':  
        return render_template('login.html')

    email = request.form.get('email')
    password = request.form.get('password')
    user_type = request.form.get('user_type')  

    if not user_type:
        return jsonify({"message": "User type is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    table = "clients" if user_type == 'client' else "lsps"
    cursor.execute(f"SELECT * FROM {table} WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()

    if user:
        session['logged_in'] = True
        session['username'] = user['username']
        session['email'] = user['email']
        session['user_type'] = user_type  
        session['user_id'] = user['id']  # ✅ Store user_id for both clients & lsps

        if user_type == 'lsp':
            session['lsp_id'] = user['id']
            session['full_name'] = user['full_name']

        return jsonify({
            "status": "success",
            "redirect_url": url_for('client_dashboard' if user_type == 'client' else 'lsp_dashboard')
        })

    return jsonify({"message": "Invalid email or password", "status": "error"}), 401



@app.route('/check_login')
def check_login():
    # Ensure user is logged in
    if not session.get('logged_in') or 'email' not in session:
        return jsonify({"logged_in": False})

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Determine the table based on user type
        user_type = session.get('user_type', 'client')  # Default to 'client'
        table = "clients" if user_type == 'client' else "lsps"

        # Fetch user details (username, email, user_type) from database
        cursor.execute(f"SELECT username, email FROM {table} WHERE email = %s", (session['email'],))
        user = cursor.fetchone()

        if user:
            return jsonify({
                "logged_in": True,
                "username": user['username'],  # Directly from DB
                "email": user['email'],       # Directly from DB
                "user_type": user_type        # From session
            })
        else:
            return jsonify({"logged_in": False})  # User not found

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"logged_in": False, "error": "Database error"}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()




@app.route('/logout', methods=['GET'])
def logout():
    session.clear()  # ✅ Clear session on logout
    return redirect(url_for('login'))







# Route for client dashboard (if needed)
@app.route('/client_dashboard')
def client_dashboard():
    return render_template('index.html')

# Route for LSP dashboard (if needed)
@app.route('/lsp_dashboard')
def lsp_dashboard():
    return render_template('index.html')


from datetime import datetime
@app.route('/manage_slots')
def manage_slots():
    return render_template('manage_slots.html')




from datetime import datetime

from datetime import datetime, timedelta

from datetime import datetime, timedelta

@app.route('/add_slots', methods=['POST'])
def add_slots():
    if 'lsp_id' not in session:
        return jsonify({"message": "Unauthorized. Please log in again."}), 401

    lsp_id = session['lsp_id']
    data = request.get_json()
    slots = data.get('slots')

    if not slots:
        return jsonify({"message": "Slots data is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    current_time = datetime.now()  # Get the current time

    # Define the date range for allowed slot dates
    allowed_start_date = current_time.date()  # today's date
    allowed_end_date = allowed_start_date + timedelta(days=7)  # 7 days from today

    for slot in slots:
        slot_date = slot['date']
        start_time = slot['startTime']
        end_time = slot['endTime']
        fare = float(slot['fare'])

        # Convert the slot_date to a datetime object (only date part)
        slot_date_obj = datetime.strptime(slot_date, "%Y-%m-%d").date()

        # Ensure the slot date is within the valid range (today to 7 days from today)
        if slot_date_obj < allowed_start_date or slot_date_obj > allowed_end_date:
            return jsonify({"message": f"Please select a date between {allowed_start_date} and {allowed_end_date}."}), 400

        # Combine the date and start_time into a full datetime object for comparison
        slot_start_datetime = datetime.strptime(f"{slot_date} {start_time}", "%Y-%m-%d %H:%M")

        # Check if the slot's start time has already passed
        if slot_start_datetime < current_time:
            return jsonify({"message": "Cannot add a slot with a start time in the past."}), 400

        # ✅ Check for overlapping slots
        cursor.execute(''' 
            SELECT COUNT(*) FROM slots 
            WHERE lsp_id = %s 
            AND slot_date = %s 
            AND (
                (start_time < %s AND end_time > %s) OR  -- New slot starts within an existing slot
                (start_time >= %s AND start_time < %s)  -- New slot starts inside an existing slot
            )
        ''', (lsp_id, slot_date, end_time, start_time, start_time, end_time))

        (conflict_count,) = cursor.fetchone()

        if conflict_count > 0:
            return jsonify({"message": "Slot conflicts with an existing one"}), 400

        # ✅ Insert the slot if there's no conflict
        cursor.execute(''' 
            INSERT INTO slots (lsp_id, slot_date, start_time, end_time, fare, status) 
            VALUES (%s, %s, %s, %s, %s, %s) 
        ''', (lsp_id, slot_date, start_time, end_time, fare, 'Available'))

    conn.commit()
    return jsonify({"message": "Slots added successfully"}), 201











@app.route('/find_lsp', methods=['GET']) 
def find_lsp():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetching query parameters
    practice_area = request.args.get('practice_area', '')
    language_comfortable = request.args.get('language_comfortable', '')
    consultation_type = request.args.get('consultation_type', '')
    city = request.args.get('city', '')
    min_cases_solved = request.args.get('min_cases_solved', '')
    min_experience = request.args.get('min_experience', '')

    # Base query
    query = "SELECT * FROM lsps WHERE 1=1"
    params = []

    # Adding filters
    if practice_area:
        query += " AND practice_area LIKE %s"
        params.append(f"%{practice_area}%")

    if language_comfortable:
        query += " AND language_comfortable LIKE %s"
        params.append(f"%{language_comfortable}%")

    if consultation_type:
        query += " AND consultation_type = %s"
        params.append(consultation_type)

    if city:
        query += " AND city = %s"
        params.append(city)

    if min_cases_solved:
        query += " AND cases_solved >= %s"
        params.append(min_cases_solved)

    if min_experience:
        query += " AND years_experience >= %s"
        params.append(min_experience)

    # Executing query
    cursor.execute(query, tuple(params))
    lsps = cursor.fetchall()

    conn.close()

    if not lsps:
        return "No LSPs found", 404

    return render_template('find_lsp.html', lsps=lsps)




@app.route('/filter_lsps', methods=['GET'])
def filter_lsps():
    city = request.args.get('city', '')
    practice_area = request.args.get('practice_area', '')
    consultation_type = request.args.get('consultation_type', '')
    min_cases_solved = request.args.get('min_cases_solved', '')
    min_experience = request.args.get('min_experience', '')
    language_comfortable = request.args.get('language_comfortable', '')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Base query
    query = "SELECT * FROM lsps WHERE 1=1"
    params = []

    # Apply filters
    if city:
        query += " AND city LIKE %s"
        params.append(f"%{city}%")
    
    if practice_area:
        query += " AND practice_area LIKE %s"
        params.append(f"%{practice_area}%")
    
    if consultation_type:
        query += " AND consultation_type = %s"
        params.append(consultation_type)

    if min_cases_solved:
        query += " AND cases_solved >= %s"
        params.append(min_cases_solved)

    if min_experience:
        query += " AND years_experience >= %s"
        params.append(min_experience)

    if language_comfortable:
        query += " AND language_comfortable LIKE %s"
        params.append(f"%{language_comfortable}%")

    cursor.execute(query, tuple(params))
    lsps = cursor.fetchall()
    conn.close()

    return render_template('lsp_cards.html', lsps=lsps)




@app.route('/set_lsp_id/<int:lsp_id>')
def set_lsp_id(lsp_id):
    """ Store the selected LSP ID in the session. """
    session['lsp_id'] = lsp_id
    print(f"LSP ID set to {lsp_id}")  # Debugging line
    return '', 204  # No content response


@app.route('/get_reviews', methods=['GET'])
def get_reviews():
    """ Fetch reviews for the LSP ID stored in the session. """
    lsp_id = session.get('lsp_id')  # Retrieve LSP ID from session
    
    if not lsp_id:
        print("No LSP ID set in session")  # Debugging line
        return jsonify({"error": "LSP ID not set in session"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Query to fetch reviews for the lsp_id
    cursor.execute("SELECT * FROM reviews WHERE lsp_id = %s", (lsp_id,))
    reviews = cursor.fetchall()

    print(f"Fetched reviews: {reviews}")  # Debugging line to check if reviews are fetched

    conn.close()

    # Check if no reviews are found
    if not reviews:
        return jsonify({"message": "No reviews available yet"}), 200  # Return a message if no reviews

    return jsonify(reviews)  # Return the reviews if available













@app.route('/lsps')
def lsps():
    print("Session Data:", session)  # Debugging: Print session data
    
    if not session.get('logged_in'):  # ✅ Check if user is logged in
        return redirect(url_for('login'))  

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, full_name, practice_area, consultation_type FROM lsps")
    lsps_data = cursor.fetchall()
    conn.close()
    return render_template('lsps.html', lsps=lsps_data)


# API route to get available slots for an LSP
from datetime import datetime, timedelta



@app.route('/get_slots', methods=['GET'])
def get_slots():
    lsp_id = request.args.get('lsp_id')
    if not lsp_id:
        return jsonify([])

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get the current time
    current_time = datetime.now()

    # Query for available slots that are not passed
    cursor.execute("""
        SELECT * FROM slots
        WHERE lsp_id = %s
        AND status = 'Available'
        AND CONCAT(slot_date, ' ', start_time) > %s
    """, (lsp_id, current_time))

    slots = cursor.fetchall()

    # Convert timedelta to string format (HH:MM:SS) if necessary
    for slot in slots:
        if isinstance(slot['start_time'], timedelta):
            slot['start_time'] = str(slot['start_time'])
        if isinstance(slot['end_time'], timedelta):
            slot['end_time'] = str(slot['end_time'])

    conn.close()
    return jsonify(slots)









import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
def send_booking_email(client_email, client_name, lsp_email, lsp_name, lsp_state, lsp_city, lsp_location, google_meet_link, slot_date, start_time, end_time, fare):
    try:
        EMAIL_SENDER = "roopachinthala08@gmail.com"
        EMAIL_PASSWORD = "hdel lteg vgds twbv"  # Use an App Password for security
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587  # Use TLS

        subject = "LegalEase - Appointment Confirmation"
        
        # Email for Client
        body_client = f"""
        Dear {client_name},

        Your appointment has been successfully booked.

        **Appointment Details:**
        - Legal Service Provider: {lsp_name}
        - Contact Email: {lsp_email}
        - Address: {lsp_location}, {lsp_city}, {lsp_state}
        - Date: {slot_date}
        - Time: {start_time} - {end_time}
        - Fee: ₹{fare}

        - Google Meet Link: {google_meet_link}

        Please ensure that you are available at the scheduled time. 
        If you are consulting an LSP in online mode, make sure you join the meeting using the provided link.

        Best regards,  
        LegalEase Team
        """

        # Email for LSP
        body_lsp = f"""
        Dear {lsp_name},

        A new appointment has been booked with you.

        **Appointment Details:**
        - Client: {client_name}
        - Client Contact: {client_email}
        - Address: {lsp_location}, {lsp_city}, {lsp_state}
        - Date: {slot_date}
        - Time: {start_time} - {end_time}
        - Fee: ₹{fare}

        Please be prepared to provide the necessary legal consultation.

        Best regards,  
        LegalEase Team
        """

        print(f"Sending email to Client: {client_email}")
        print(f"Sending email to LSP: {lsp_email}")

        # Prepare email for client
        msg_client = MIMEMultipart()
        msg_client['From'] = EMAIL_SENDER
        msg_client['To'] = client_email
        msg_client['Subject'] = subject
        msg_client.attach(MIMEText(body_client, 'plain'))

        # Prepare email for LSP
        msg_lsp = MIMEMultipart()
        msg_lsp['From'] = EMAIL_SENDER
        msg_lsp['To'] = lsp_email
        msg_lsp['Subject'] = subject
        msg_lsp.attach(MIMEText(body_lsp, 'plain'))

        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Upgrade connection to secure TLS
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)

        # Send both emails
        server.sendmail(EMAIL_SENDER, client_email, msg_client.as_string())
        server.sendmail(EMAIL_SENDER, lsp_email, msg_lsp.as_string())

        server.quit()
        print("Emails sent successfully!")
        return True

    except Exception as e:
        print(f"Error sending booking confirmation email: {e}")
        return False







@app.route('/confirm_booking', methods=['GET', 'POST'])
def confirm_booking():
    if request.method == 'GET':
        slot_id = request.args.get('slot_id')

        if not slot_id:
            return render_template('message.html', status="error", message="Slot ID is required"), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Fetch slot details, including lsp_id
            cursor.execute("SELECT * FROM slots WHERE id = %s", (slot_id,))
            slot = cursor.fetchone()

            if not slot:
                return render_template('message.html', status="error", message="Slot not found"), 404

            return render_template(
                'confirm_booking.html',
                slot_id=slot['id'],
                lsp_id=slot['lsp_id'],
                slot_date=slot['slot_date'],
                start_time=slot['start_time'],
                end_time=slot['end_time'],
                fare=slot['fare']
            )

        finally:
            conn.close()  # Ensure connection is closed

    elif request.method == 'POST':
        if 'user_id' not in session or session.get('user_type') != 'client':
            return render_template('message.html', status="error", message="Unauthorized. Please log in as a client."), 401

        client_id = session['user_id']
        slot_id = request.form.get('slot_id')

        if not slot_id:
            return render_template('message.html', status="error", message="Slot ID is required"), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Start a transaction
            conn.start_transaction()

            # Check if slot is available
            cursor.execute("SELECT * FROM slots WHERE id = %s AND status = 'Available' FOR UPDATE", (slot_id,))
            slot = cursor.fetchone()

            if not slot:
                conn.rollback()
                return render_template('message.html', status="error", message="Slot not available or already booked"), 400

            lsp_id = slot['lsp_id']
            slot_date = slot['slot_date']
            start_time = slot['start_time']
            end_time = slot['end_time']
            fare = slot['fare']

            # Fetch LSP details (name, email, state, city, location, and google_meet_link)
            cursor.execute("""
                SELECT full_name, email, state, city, location, google_meet_link 
                FROM lsps 
                WHERE id = %s
            """, (lsp_id,))
            lsp = cursor.fetchone()
            lsp_name = lsp['full_name']
            lsp_email = lsp['email']
            lsp_state = lsp['state']
            lsp_city = lsp['city']
            lsp_location = lsp['location']
            google_meet_link = lsp['google_meet_link']

            # Fetch client details (name and email)
            cursor.execute("SELECT full_name, email FROM clients WHERE id = %s", (client_id,))
            client = cursor.fetchone()
            client_name = client['full_name']
            client_email = client['email']

            # Insert booking
            cursor.execute(''' 
                INSERT INTO bookings (client_id, lsp_id, slot_id, status) 
                VALUES (%s, %s, %s, 'Confirmed') 
            ''', (client_id, lsp_id, slot_id))

            # Mark slot as booked
            cursor.execute("UPDATE slots SET status = 'Booked' WHERE id = %s", (slot_id,))

            conn.commit()  # Commit transaction

            # Call the function to send booking confirmation emails
            send_booking_email(
                client_email, client_name, lsp_email, lsp_name, 
                lsp_state, lsp_city, lsp_location, google_meet_link, 
                slot_date, start_time, end_time, fare
            )

            return render_template('message.html', status="success", message="✅ Your booking has been successfully confirmed!")

        except Exception as e:
            conn.rollback()
            return render_template('message.html', status="error", message=f"An error occurred: {str(e)}"), 500

        finally:
            conn.close()  # Ensure connection is closed







@app.route('/book_slot/<int:slot_id>', methods=['POST'])
def book_slot(slot_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the slot is still available
    cursor.execute("SELECT * FROM slots WHERE id = %s AND status = 'Available'", (slot_id,))
    slot = cursor.fetchone()

    if not slot:
        conn.close()
        return "Slot is no longer available", 400

    # Update slot status and assign user
    cursor.execute("""
        UPDATE slots SET status = 'Booked', booked_by = %s WHERE id = %s
    """, (user_id, slot_id))
    conn.commit()
    conn.close()

    return redirect(url_for('booking_success'))


@app.route('/')
def index():
    return render_template('index.html')  # Ensure index.html exists


def get_lsp_bookings(lsp_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    query = """
    SELECT s.id AS slot_id, s.slot_date, s.start_time, s.end_time, s.status AS slot_status, 
           b.id AS booking_id, b.booking_date, b.status AS booking_status, 
           c.full_name AS client_name, c.email AS client_email, c.phone_number AS client_phone
    FROM slots s
    LEFT JOIN bookings b ON s.id = b.slot_id  -- Use LEFT JOIN to include unbooked slots as well
    LEFT JOIN clients c ON b.client_id = c.id  -- Join clients to show their details if the slot is booked
    WHERE s.lsp_id = %s  -- Ensure the query fetches only the slots for the LSP
    ORDER BY s.slot_date DESC, s.start_time DESC
    """
    
    cursor.execute(query, (lsp_id,))
    bookings = cursor.fetchall()
    
    cursor.close()
    connection.close()

    return bookings



from datetime import datetime

@app.route('/lsp/my_bookings', methods=['GET'])
def lsp_my_bookings():
    if 'lsp_id' not in session:
        return redirect(url_for('login'))
    
    lsp_id = session['lsp_id']
    bookings = get_lsp_bookings(lsp_id)

    # Get filters from the request
    time_filter = request.args.get('time_filter')
    booking_status = request.args.get('booking_status')
    slot_status = request.args.get('slot_status')

    # Filter bookings
    now = datetime.now()

    def is_time_passed(booking):
        dt_str = f"{booking['slot_date']} {booking['start_time']}"
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        return dt < now

    filtered = []
    for booking in bookings:
        # Slot time
        if time_filter == 'passed' and not is_time_passed(booking):
            continue
        if time_filter == 'upcoming' and is_time_passed(booking):
            continue

        # Booking status
        b_status = booking['booking_status'] or 'No Booking'
        if booking_status != 'all' and b_status != booking_status:
            continue

        # Slot status
        s_status = booking['slot_status']
        if slot_status != 'all' and s_status != slot_status:
            continue

        filtered.append(booking)

    return render_template('lsp_my_bookings.html', bookings=filtered)





@app.route('/lsp/cancel_slot/<int:slot_id>', methods=['POST'])
def cancel_slot(slot_id):
    if 'lsp_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if LSP is not logged in
    
    lsp_id = session['lsp_id']
    
    # Establish database connection
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Query to delete the slot
    query = """
    DELETE FROM slots
    WHERE id = %s AND lsp_id = %s AND status = 'Available'
    """
    
    cursor.execute(query, (slot_id, lsp_id))
    connection.commit()
    
    cursor.close()
    connection.close()

    # Redirect back to the LSP's bookings page after cancellation
    return redirect(url_for('lsp_my_bookings'))






@app.route('/contact_us', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        client_name = request.form.get('name')
        client_email = request.form.get('email')
        message_content = request.form.get('message')

        if not client_name or not client_email or not message_content:
            return render_template('message.html', status="error", message="All fields are required."), 400

        # Send email
        email_sent = send_contact_email(client_email, client_name, message_content)
        
        if email_sent:
            return render_template('message.html', status="success", message="✅ Your message has been successfully sent!")
        else:
            return render_template('message.html', status="error", message="An error occurred while sending your message. Please try again later."), 500

    return render_template('contact.html')



import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_contact_email(client_email, client_name, message_content): 
    try:
        EMAIL_SENDER = "roopachinthala08@gmail.com"  # Admin's email
        EMAIL_PASSWORD = "hdel lteg vgds twbv"  # Use an App Password for security
        SMTP_SERVER = "smtp.gmail.com"
        SMTP_PORT = 587  # Use TLS

        subject = "LegalEase - Contact Us Form Submission"
        
        # Email for Admin
        body_admin = f"""
        A new message has been received from the Contact Us form.

        **Message Details:**
        - Name: {client_name}
        - Email: {client_email}
        - Message: {message_content}

        Please respond to the query accordingly.

        Best regards,  
        LegalEase Team
        """

        # Email for Client (optional)
        body_client = f"""
        Dear {client_name},

        Thank you for reaching out to LegalEase. Your message has been received.

        **Message Summary:**
        - Your Message: {message_content}

        Our team will get back to you as soon as possible.

        Best regards,  
        LegalEase Team
        """

        # Prepare email for Admin
        msg_admin = MIMEMultipart()
        msg_admin['From'] = EMAIL_SENDER
        msg_admin['To'] = "roopachinthala08@gmail.com"  # Send email to admin
        msg_admin['Subject'] = subject
        msg_admin.attach(MIMEText(body_admin, 'plain'))

        # Prepare email for Client (Optional)
        msg_client = MIMEMultipart()
        msg_client['From'] = EMAIL_SENDER
        msg_client['To'] = client_email
        msg_client['Subject'] = subject
        msg_client.attach(MIMEText(body_client, 'plain'))

        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)  # Debugging output
        server.starttls()  # Upgrade connection to secure TLS
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)  # Login using admin's credentials

        # Send both emails
        server.sendmail(EMAIL_SENDER, "roopachinthala08@gmail.com", msg_admin.as_string())  # Send to Admin
        server.sendmail(EMAIL_SENDER, client_email, msg_client.as_string())  # Send to Client

        server.quit()
        print("Emails sent successfully!")
        return True

    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return False








from flask import render_template

@app.route('/check_reviews', methods=['GET'])
def check_reviews():
    if 'lsp_id' not in session:
        return jsonify({"error": "LSP ID is required. Please log in first."}), 400
    
    lsp_id = session['lsp_id']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT r.id, r.review_text, r.created_at, c.full_name AS client_name
        FROM reviews r
        JOIN bookings b ON r.booking_id = b.id
        JOIN clients c ON b.client_id = c.id
        WHERE r.lsp_id = %s
        ORDER BY r.created_at DESC
        """
        cursor.execute(query, (lsp_id,))
        reviews = cursor.fetchall()

        cursor.close()
        conn.close()

        if not reviews:
            return render_template('check_reviews.html', reviews=[], error="No reviews found for this LSP.")

        return render_template('check_reviews.html', reviews=reviews)
    except Exception as e:
        print(f"Error: {str(e)}")
        return render_template('check_reviews.html', reviews=[], error="An error occurred while fetching reviews.")


@app.route('/submit_review', methods=['POST'])
def submit_review():
    if 'user_id' not in session or session.get('user_type') != 'client':
        return jsonify({"message": "Unauthorized access"}), 403

    data = request.get_json()
    booking_id = data.get('booking_id')
    review_text = data.get('review')

    if not booking_id or not review_text:
        return jsonify({"message": "Booking ID and review text are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if the booking exists
        cursor.execute("SELECT status, slot_id FROM bookings WHERE id = %s", (booking_id,))
        booking = cursor.fetchone()

        if not booking:
            return jsonify({"message": "Booking not found"}), 404

        # Access the tuple by index (status is at index 0, slot_id at index 1)
        status = booking[0]
        slot_id = booking[1]

        # Allow reviews only for completed or confirmed bookings
        if status not in ['Completed', 'Confirmed']:
            return jsonify({"message": "Review only submitted for confirmed or completed bookings."}), 400

        # Check if a review already exists for this booking
        cursor.execute("SELECT COUNT(*) FROM reviews WHERE booking_id = %s", (booking_id,))
        existing_review = cursor.fetchone()

        if existing_review[0] > 0:
            return jsonify({"message": "Review already submitted for this booking."}), 400

        # Get lsp_id associated with the booking
        cursor.execute("SELECT lsp_id FROM slots WHERE id = %s", (slot_id,))
        lsp = cursor.fetchone()

        if not lsp:
            return jsonify({"message": "LSP not found for this booking"}), 404

        # Access the lsp_id (it should be the first element of the tuple)
        lsp_id = lsp[0]

        # Insert review into the reviews table
        cursor.execute("INSERT INTO reviews (booking_id, lsp_id, review_text) VALUES (%s, %s, %s)", 
                       (booking_id, lsp_id, review_text))
        conn.commit()

        return jsonify({"message": "Review submitted successfully"}), 200

    except Exception as e:
        # Log the exception to debug
        print(f"Error during review submission: {str(e)}")
        conn.rollback()
        return jsonify({"message": "Error submitting review", "error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()










@app.route('/my_bookings')
def my_bookings():
    if 'user_id' not in session or session.get('user_type') != 'client':
        return redirect(url_for('login'))

    client_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT b.id AS booking_id, 
               l.full_name AS lsp_name, 
               s.slot_date, 
               s.start_time, 
               s.end_time, 
               s.fare, 
               b.status
        FROM bookings b
        JOIN slots s ON b.slot_id = s.id
        JOIN lsps l ON s.lsp_id = l.id
        WHERE b.client_id = %s
        ORDER BY s.slot_date DESC
    """
    
    cursor.execute(query, (client_id,))
    bookings = cursor.fetchall()
    
    conn.close()

    return render_template('my_bookings.html', bookings=bookings)





@app.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    if 'user_id' not in session or session.get('user_type') != 'client':
        return jsonify({"message": "Unauthorized access"}), 403

    data = request.get_json()
    print("Received Data:", data)  # Debugging line to check received JSON

    booking_id = data.get('booking_id')

    if not booking_id:
        return jsonify({"message": "Booking ID is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT slot_id FROM bookings WHERE id = %s", (booking_id,))
        slot = cursor.fetchone()

        if not slot:
            return jsonify({"message": "Booking not found or already cancelled"}), 404

        slot_id = slot[0]

        cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE id = %s", (booking_id,))
        cursor.execute("UPDATE slots SET status = 'Available' WHERE id = %s", (slot_id,))

        conn.commit()
        return jsonify({"message": "Booking cancelled successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"message": "Error cancelling booking", "error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()




# Route to serve the profile editing page
@app.route('/edit_profile', methods=['GET'])
def edit_profile():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    user_type = session.get('user_type')
    user_id = session.get('user_id')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if user_type == 'client':
            cursor.execute("SELECT full_name, username, phone_number, state, city FROM clients WHERE id = %s", (user_id,))
        elif user_type == 'lsp':
            cursor.execute("""
                SELECT full_name, username, phone_number, state, city, 
                       language_comfortable, profile_description, consultation_type, linkedin_link
                FROM lsps WHERE id = %s
            """, (user_id,))
        else:
            return jsonify({"message": "Unauthorized access!"}), 403

        user_data = cursor.fetchone()

        if not user_data:
            return jsonify({"message": "User not found!"}), 404

        return render_template('edit_profile.html', user_data=user_data, user_type=user_type)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": f"Error: {err}"}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


@app.route('/edit_profile', methods=['POST'])
def edit_profile_post():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))

    user_type = session.get('user_type')
    user_id = session.get('user_id')

    fullname = request.form.get('fullname')
    username = request.form.get('username')
    phone_number = request.form.get('phone_number')
    state = request.form.get('state')
    city = request.form.get('city')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if user_type == 'client':
            cursor.execute('''UPDATE clients SET full_name = %s, username = %s, phone_number = %s, state = %s, city = %s WHERE id = %s''', (fullname, username, phone_number, state, city, user_id))
            conn.commit()
            return redirect(url_for('client_dashboard'))  # Redirect clients to 'client_dashboard'

        elif user_type == 'lsp':
            language_comfortable = request.form.get('language_comfortable')
            profile_description = request.form.get('profile_description')
            consultation_type = request.form.get('consultation_type')
            linkedin_link = request.form.get('linkedin_link')
            cursor.execute('''UPDATE lsps SET full_name = %s, username = %s, phone_number = %s, state = %s, city = %s,
                      language_comfortable = %s, profile_description = %s, consultation_type = %s, linkedin_link = %s WHERE id = %s''',
                   (fullname, username, phone_number, state, city, language_comfortable, profile_description, consultation_type, linkedin_link, user_id))
            conn.commit()
            return redirect(url_for('lsp_dashboard'))  # Redirect LSPs to 'lsp_dashboard'


        else:
            return jsonify({"message": "Unauthorized access!"}), 403

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({"message": f"Error: {err}"}), 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()










if __name__ == '__main__':
    app.run(debug=True)
