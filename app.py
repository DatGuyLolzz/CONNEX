from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import os
import uuid # For generating unique user IDs if not using real auth

app = Flask(__name__)
# IMPORTANT: Change this to a strong, random key in production!
# This secret key is crucial for the security of Flask sessions.
app.secret_key = 'your_super_secret_secret_key_for_sessions_12345' 

# MySQL DB configuration from environment variables or defaults
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Ilovemysql2025%')
DB_NAME = os.environ.get('DB_NAME', 'mydb')
DB_PORT = os.environ.get('DB_PORT', 3306) # Default MySQL port


# This function runs before every request to ensure a user_id exists in the session.
# This simulates a basic user identity for event sign-ups without full authentication.
@app.before_request
def make_session_permanent():
    # Make the session permanent (lasts for 31 days by default)
    session.permanent = True
    # If a user_id is not already in the session, generate a new unique one
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4()) # Generate a unique ID using UUID4

@app.route('/')
def home():
    """
    Renders the home page of the application.
    """
    return render_template('home.html')

# --- Flask Route to Display Event Details ---
@app.route('/eventdetails/<int:event_id>')
def event_details(event_id):
    """
    Connects to the MySQL database, fetches data for a specific event by ID,
    and renders it in an HTML template. It also checks if the current user
    has already signed up for this event.
    """
    db_connection = None
    cursor = None
    event = None # Initialize event to None to handle cases where it's not found
    
    # Flag to indicate if the current user has already signed up for this event
    has_signed_up = False
    current_user_id = session.get('user_id') # Get the unique ID for this session/user

    try:
        # Establish database connection
        db_connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        # Use a dictionary cursor to access columns by name (e.g., event['EventDescription'])
        cursor = db_connection.cursor(dictionary=True)  
        
        # Fetch the specific event by EventID from the 'event' table
        # Ensure all necessary columns (including Category and ImageFileName) are selected
        cursor.execute("SELECT EventID, EventDescription, Date, Time, Venue, Category, ImageFileName FROM event WHERE EventID = %s", (event_id,))
        event = cursor.fetchone() # Fetch only one row

        # If no event is found with the given ID, flash an error and redirect
        if not event:
            flash(f"No event found with ID {event_id}.", 'error')
            return redirect(url_for('usereventpage')) # Redirect to a generic events page or home

        # If a user_id exists, check if this user has signed up for this event
        if current_user_id:
            check_signup_query = "SELECT COUNT(*) FROM user_calendar_events WHERE event_id = %s AND user_id = %s"
            cursor.execute(check_signup_query, (event_id, current_user_id))
            # If count is greater than 0, the user has signed up
            if cursor.fetchone()['COUNT(*)'] > 0:
                has_signed_up = True

    except mysql.connector.Error as err:
        # Catch and print any database connection or query errors
        print(f"Error: {err}")
        flash(f"Database error: {err}", 'error') # Flash error message to the user
        return render_template('error.html', message=f"Database error: {err}")
    finally:
        # Ensure database cursor and connection are closed in all cases
        if cursor:
            cursor.close()
        if db_connection:
            db_connection.close()

    # Render the HTML template, passing the fetched event data and signup status
    return render_template('eventdetailpage.html', event=event, has_signed_up=has_signed_up)

# --- Flask Route to Handle Event Sign-up (POST request) ---
@app.route('/sign_up_for_event', methods=['POST'])
def sign_up_for_event():
    """
    Handles a user signing up for an event. It retrieves the event ID from
    the form submission and the user ID from the session, then inserts a
    record into the 'user_calendar_events' table.
    """
    # Get the event_id from the submitted form data
    event_id = request.form.get('event_id', type=int)
    # Get the unique user ID from the Flask session
    current_user_id = session.get('user_id') 
    
    # Basic validation for event_id
    if not event_id:
        flash("Invalid event ID provided for sign-up.", 'error')
        return redirect(url_for('usereventpage')) # Redirect if event ID is missing

    # Basic validation for user_id (should always exist due to @before_request)
    if not current_user_id:
        flash("Could not identify user. Please try again.", 'error')
        return redirect(url_for('event_details', event_id=event_id)) # Redirect back to event details

    db_connection = None
    cursor = None
    try:
        db_connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = db_connection.cursor(dictionary=True)

        # Check if the user has already signed up for this specific event to prevent duplicates
        check_signup_query = "SELECT COUNT(*) FROM user_calendar_events WHERE event_id = %s AND user_id = %s"
        cursor.execute(check_signup_query, (event_id, current_user_id))
        if cursor.fetchone()['COUNT(*)'] > 0:
            flash(f"You have already signed up for this event.", 'warning')
            return redirect(url_for('event_details', event_id=event_id)) # Redirect back with a warning

        # Insert the event into the user_calendar_events table with both event_id and user_id
        insert_query = "INSERT INTO user_calendar_events (event_id, user_id) VALUES (%s, %s)"
        cursor.execute(insert_query, (event_id, current_user_id))
        db_connection.commit() # Commit the changes to the database

        flash(f"Successfully signed up for the event!", 'success') # Flash a success message

    except mysql.connector.Error as err:
        # Handle database errors during insertion
        print(f"Error signing up for event: {err}")
        flash(f"Error signing up for event: {err}", 'error')
        db_connection.rollback() # Rollback any changes if an error occurs
    finally:
        # Ensure cursor and connection are closed
        if cursor:
            cursor.close()
        if db_connection:
            db_connection.close()
    
    # Redirect back to the event details page to show the flash message and updated buttons
    return redirect(url_for('event_details', event_id=event_id))

# --- Flask Route to Handle Removing an Event Sign-up (POST request) ---
@app.route('/remove_sign_up', methods=['POST'])
def remove_sign_up():
    """
    Handles removing a user's sign-up for an event. It deletes the
    corresponding record from the 'user_calendar_events' table.
    """
    event_id = request.form.get('event_id', type=int)
    current_user_id = session.get('user_id')

    if not event_id:
        flash("Invalid event ID provided for removal.", 'error')
        return redirect(url_for('usereventpage')) 

    if not current_user_id:
        flash("Could not identify user to remove sign-up. Please try again.", 'error')
        return redirect(url_for('event_details', event_id=event_id))

    db_connection = None
    cursor = None
    try:
        db_connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = db_connection.cursor(dictionary=True)

        # Delete the corresponding entry from user_calendar_events table
        # The deletion is based on both event_id and user_id to ensure correctness
        delete_query = "DELETE FROM user_calendar_events WHERE event_id = %s AND user_id = %s"
        cursor.execute(delete_query, (event_id, current_user_id))
        db_connection.commit() # Commit the deletion

        # Check if a row was actually deleted and provide appropriate feedback
        if cursor.rowcount > 0: 
            flash(f"Event sign-up removed successfully!", 'success')
        else:
            flash(f"No sign-up found for this event to remove.", 'warning')

    except mysql.connector.Error as err:
        print(f"Error removing event sign-up: {err}")
        flash(f"Error removing event sign-up: {err}", 'error')
        db_connection.rollback() # Rollback in case of database error
    finally:
        if cursor:
            cursor.close()
        if db_connection:
            db_connection.close()
    
    # Redirect back to the event details page to reflect the change
    return redirect(url_for('event_details', event_id=event_id))


@app.route('/calendar')
def calendar():
    """
    Renders the calendar page, displaying events the current user has signed up for.
    It fetches event details by joining 'user_calendar_events' with the 'event' table.
    """
    db_connection = None
    cursor = None
    signed_up_events = [] # Initialize an empty list for events
    current_user_id = session.get('user_id') # Get the current user's session ID

    # If no user ID is found (e.g., session cleared), inform the user
    if not current_user_id:
        flash("Please sign up for events to see them here.", 'info')
        return render_template('calendar.html', signed_up_events=[])

    try:
        db_connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        cursor = db_connection.cursor(dictionary=True)

        # SQL query to select all event details for events that the current user has signed up for.
        # It joins 'user_calendar_events' with 'event' table on EventID.
        query = """
            SELECT e.EventID, e.EventDescription, e.Date, e.Time, e.Venue, e.Category, e.ImageFileName
            FROM user_calendar_events uce
            JOIN event e ON uce.event_id = e.EventID
            WHERE uce.user_id = %s -- Filter by the current user's ID
            ORDER BY e.Date, e.Time -- Order events by date and time
        """
        cursor.execute(query, (current_user_id,)) # Execute the query with the user_id parameter
        signed_up_events = cursor.fetchall() # Fetch all matching events

    except mysql.connector.Error as err:
        print(f"Error fetching signed up events: {err}")
        flash(f"Error loading your calendar: {err}", 'error') # Flash error if fetching fails
    finally:
        if cursor:
            cursor.close()
        if db_connection:
            db_connection.close()
            
    # Render the calendar HTML template, passing the list of signed-up events and the user ID
    return render_template('calendar.html', signed_up_events=signed_up_events, user_id=current_user_id)


@app.route('/usereventpage')
def usereventpage():
    """
    Renders a user event page. (This seems to be your main events listing page).
    """
    return render_template('usereventpage.html')


if __name__ == '__main__':
    # Run the Flask application in debug mode for development.
    # Set debug=False in production.
    app.run(debug=True)
