import sqlite3

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from functools import wraps

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from database import (
    get_connection,
    init_db
)


app = Flask(__name__)

app.secret_key = "peerup-ssn-secure-key"

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

init_db()


# =========================================================
# CAMPUS LOCATIONS
# =========================================================

CAMPUS_LOCATIONS = [

    {
        "name": "Library",
        "lat": 12.751306605114745,
        "lng": 80.19652230137397,
        "category": "Academic"
    },

    {
        "name": "Gent's Hostel",
        "lat": 12.74997502785919,
        "lng": 80.19902748459153,
        "category": "Hostel"
    },

    {
        "name": "Ladies Hostel",
        "lat": 12.753394211161167,
        "lng": 80.19552988405933,
        "category": "Hostel"
    },

    {
        "name": "Rishabh's",
        "lat": 12.7512856970238,
        "lng": 80.19507884077208,
        "category": "Food"
    },

    {
        "name": "Main Canteen",
        "lat": 12.753330732065619,
        "lng": 80.1947923988624,
        "category": "Food"
    },

    {
        "name": "PR",
        "lat": 12.74931776428708,
        "lng": 80.19701556511771,
        "category": "Campus"
    },

    {
        "name": "Fresh Crush",
        "lat": 12.751961480421208,
        "lng": 80.19657526297159,
        "category": "Food"
    },

    {
        "name": "Clock Tower",
        "lat": 12.752789541732003,
        "lng": 80.19645867238447,
        "category": "Landmark"
    },

    {
        "name": "Central Perk",
        "lat": 12.752655930259024,
        "lng": 80.19211495319486,
        "category": "Food"
    },

    {
        "name": "IT Block",
        "lat": 12.751640596057428,
        "lng": 80.19687316256376,
        "category": "Academic"
    },

    {
        "name": "CSE Block",
        "lat": 12.751485741272214,
        "lng": 80.19732164874875,
        "category": "Academic"
    },

    {
        "name": "BME Block",
        "lat": 12.749241134424539,
        "lng": 80.19798455716962,
        "category": "Academic"
    },

    {
        "name": "Chemical Block",
        "lat": 12.749094260455218,
        "lng": 80.19728727572874,
        "category": "Academic"
    },

    {
        "name": "ECE Block",
        "lat": 12.750674747638348,
        "lng": 80.19599746872251,
        "category": "Academic"
    },

    {
        "name": "Civil Block",
        "lat": 12.749231555690123,
        "lng": 80.19592872266607,
        "category": "Academic"
    },

    {
        "name": "EEE Block",
        "lat": 12.749154925800815,
        "lng": 80.19673730724776,
        "category": "Academic"
    },

    {
        "name": "First Year Block",
        "lat": 12.751991323782102,
        "lng": 80.19702173532662,
        "category": "Academic"
    },

    {
        "name": "MECH Block",
        "lat": 12.751712435878236,
        "lng": 80.19437211546386,
        "category": "Academic"
    },

    {
        "name": "Fountain",
        "lat": 12.75165475325996,
        "lng": 80.1958520257006,
        "category": "Landmark"
    }

]


# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            return redirect(
                url_for("login")
            )

        return function(
            *args,
            **kwargs
        )

    return wrapper


# =========================================================
# LOGIN
# =========================================================

@app.route("/")
def login():

    if "user_id" in session:

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "login.html"
    )


@app.route(
    "/login",
    methods=["POST"]
)
def login_user():

    identity = request.form.get(
        "student_id",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )


    if not identity or not password:

        flash(
            "Enter your SSN email or Student ID and password.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    conn = get_connection()


    user = conn.execute("""
        SELECT *
        FROM users

        WHERE LOWER(student_id) = LOWER(?)
        OR LOWER(email) = LOWER(?)
    """, (
        identity,
        identity
    )).fetchone()


    conn.close()


    if (
        user
        and check_password_hash(
            user["password"],
            password
        )
    ):

        session.clear()

        session["user_id"] = user["id"]

        session["student"] = user["name"]

        session["email"] = user["email"]

        return redirect(
            url_for("dashboard")
        )


    flash(
        "We couldn't match those credentials. Check your details and try again.",
        "error"
    )

    return redirect(
        url_for("login")
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=[
        "GET",
        "POST"
    ]
)
def register():

    if "user_id" in session:

        return redirect(
            url_for("dashboard")
        )


    if request.method == "GET":

        return render_template(
            "register.html"
        )


    name = request.form.get(
        "name",
        ""
    ).strip()

    student_id = request.form.get(
        "student_id",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    department = request.form.get(
        "department",
        ""
    ).strip()

    year = request.form.get(
        "year",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not all([
        name,
        student_id,
        email,
        department,
        year,
        password,
        confirm_password
    ]):

        flash(
            "Please complete all fields.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    # For this PeerUp build, only SSN institutional email is accepted.
    if not email.endswith(
        "@ssn.edu.in"
    ):

        flash(
            "Use your SSN institutional email address to join PeerUp.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    if len(password) < 6:

        flash(
            "Your password must contain at least 6 characters.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    if password != confirm_password:

        flash(
            "The passwords do not match.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    # -----------------------------------------------------
    # CHECK EXISTING ACCOUNT
    # -----------------------------------------------------

    conn = get_connection()


    existing_user = conn.execute("""
        SELECT id
        FROM users

        WHERE LOWER(email) = LOWER(?)
        OR LOWER(student_id) = LOWER(?)
    """, (
        email,
        student_id
    )).fetchone()


    if existing_user:

        conn.close()

        flash(
            "An account already exists with that SSN email or Student ID.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    # -----------------------------------------------------
    # CREATE ACCOUNT
    # -----------------------------------------------------

    try:

        cursor = conn.execute("""
            INSERT INTO users
            (
                student_id,
                name,
                email,
                department,
                year,
                password
            )

            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            name,
            email,
            department,
            year,
            generate_password_hash(
                password
            )
        ))


        user_id = cursor.lastrowid


        conn.commit()


    except sqlite3.IntegrityError:

        conn.close()

        flash(
            "That account already exists.",
            "error"
        )

        return redirect(
            url_for("register")
        )


    conn.close()


    # -----------------------------------------------------
    # LOG USER IN IMMEDIATELY
    # -----------------------------------------------------

    session.clear()

    session["user_id"] = user_id

    session["student"] = name

    session["email"] = email


    return redirect(
        url_for("dashboard")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    conn = get_connection()


    mentors = conn.execute("""
        SELECT *
        FROM mentors

        ORDER BY rating DESC

        LIMIT 3
    """).fetchall()


    upcoming_count = conn.execute("""
        SELECT COUNT(*)

        FROM bookings

        WHERE learner_id = ?
        AND status != 'Cancelled'
    """, (
        session["user_id"],
    )).fetchone()[0]


    conn.close()


    return render_template(
        "dashboard.html",
        mentors=mentors,
        student=session["student"],
        upcoming_count=upcoming_count
    )


# =========================================================
# MENTORS
# =========================================================

@app.route("/mentors")
@login_required
def mentors():

    search = request.args.get(
        "search",
        ""
    ).strip()


    conn = get_connection()


    if search:

        term = f"%{search}%"

        mentor_list = conn.execute("""
            SELECT *

            FROM mentors

            WHERE name LIKE ?
            OR skills LIKE ?
            OR department LIKE ?
            OR location LIKE ?

            ORDER BY rating DESC
        """, (
            term,
            term,
            term,
            term
        )).fetchall()

    else:

        mentor_list = conn.execute("""
            SELECT *

            FROM mentors

            ORDER BY rating DESC
        """).fetchall()


    conn.close()


    return render_template(
        "mentors.html",
        mentors=mentor_list,
        search=search
    )


# =========================================================
# MENTOR PROFILE
# =========================================================

@app.route(
    "/mentor/<int:mentor_id>"
)
@login_required
def mentor_profile(
    mentor_id
):

    conn = get_connection()


    mentor = conn.execute("""
        SELECT *
        FROM mentors

        WHERE id = ?
    """, (
        mentor_id,
    )).fetchone()


    if mentor is None:

        conn.close()

        return "Mentor not found", 404


    reviews = conn.execute("""
        SELECT
            reviews.*,
            users.name AS reviewer_name

        FROM reviews

        JOIN users
        ON reviews.learner_id = users.id

        WHERE reviews.mentor_id = ?

        ORDER BY reviews.created_at DESC
    """, (
        mentor_id,
    )).fetchall()


    booking_exists = conn.execute("""
        SELECT id

        FROM bookings

        WHERE learner_id = ?
        AND mentor_id = ?
        AND status != 'Cancelled'

        LIMIT 1
    """, (
        session["user_id"],
        mentor_id
    )).fetchone()


    existing_review = conn.execute("""
        SELECT *

        FROM reviews

        WHERE learner_id = ?
        AND mentor_id = ?
    """, (
        session["user_id"],
        mentor_id
    )).fetchone()


    conn.close()


    return render_template(
        "mentor_profile.html",
        mentor=mentor,
        reviews=reviews,
        can_review=booking_exists is not None,
        existing_review=existing_review
    )


# =========================================================
# BOOK MENTOR
# =========================================================

@app.route(
    "/book/<int:mentor_id>",
    methods=["POST"]
)
@login_required
def book_mentor(
    mentor_id
):

    session_date = request.form.get(
        "session_date"
    )

    session_time = request.form.get(
        "session_time"
    )

    session_type = request.form.get(
        "session_type"
    )

    exchange_type = request.form.get(
        "exchange_type"
    )

    exchange_skill = request.form.get(
        "exchange_skill",
        ""
    ).strip()

    notes = request.form.get(
        "notes",
        ""
    ).strip()


    conn = get_connection()


    mentor = conn.execute("""
        SELECT *
        FROM mentors

        WHERE id = ?
    """, (
        mentor_id,
    )).fetchone()


    if mentor is None:

        conn.close()

        return "Mentor not found", 404


    if exchange_type == "Paid Session":

        payment_status = "Pending"

        booking_status = "Awaiting Payment"

    else:

        payment_status = "Not Required"

        booking_status = "Confirmed"


    cursor = conn.execute("""
        INSERT INTO bookings
        (
            learner_id,
            mentor_id,
            session_date,
            session_time,
            session_type,
            exchange_type,
            exchange_skill,
            notes,
            status,
            payment_status
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session["user_id"],
        mentor_id,
        session_date,
        session_time,
        session_type,
        exchange_type,
        exchange_skill,
        notes,
        booking_status,
        payment_status
    ))


    booking_id = cursor.lastrowid


    conn.commit()

    conn.close()


    if exchange_type == "Paid Session":

        return redirect(
            url_for(
                "payment",
                booking_id=booking_id
            )
        )


    return redirect(
        url_for("bookings")
    )


# =========================================================
# PAYMENT
# =========================================================

@app.route(
    "/payment/<int:booking_id>"
)
@login_required
def payment(
    booking_id
):

    conn = get_connection()


    booking = conn.execute("""
        SELECT
            bookings.*,
            mentors.name AS mentor_name,
            mentors.price AS price,
            mentors.skills AS skills

        FROM bookings

        JOIN mentors
        ON bookings.mentor_id = mentors.id

        WHERE bookings.id = ?
        AND bookings.learner_id = ?
    """, (
        booking_id,
        session["user_id"]
    )).fetchone()


    conn.close()


    if booking is None:

        return "Booking not found", 404


    return render_template(
        "payment.html",
        booking=booking
    )


@app.route(
    "/payment/<int:booking_id>/confirm",
    methods=["POST"]
)
@login_required
def confirm_payment(
    booking_id
):

    conn = get_connection()


    booking = conn.execute("""
        SELECT id

        FROM bookings

        WHERE id = ?
        AND learner_id = ?
    """, (
        booking_id,
        session["user_id"]
    )).fetchone()


    if booking is None:

        conn.close()

        return "Booking not found", 404


    conn.execute("""
        UPDATE bookings

        SET
            payment_status = 'Paid',
            status = 'Confirmed'

        WHERE id = ?
    """, (
        booking_id,
    ))


    conn.commit()

    conn.close()


    return redirect(
        url_for("bookings")
    )


# =========================================================
# MY SESSIONS
# =========================================================

@app.route("/bookings")
@login_required
def bookings():

    conn = get_connection()


    booking_list = conn.execute("""
        SELECT
            bookings.*,
            mentors.name AS mentor_name,
            mentors.skills,
            mentors.location,
            mentors.price

        FROM bookings

        JOIN mentors
        ON bookings.mentor_id = mentors.id

        WHERE bookings.learner_id = ?

        ORDER BY
            bookings.session_date,
            bookings.session_time
    """, (
        session["user_id"],
    )).fetchall()


    conn.close()


    return render_template(
        "bookings.html",
        bookings=booking_list
    )


@app.route(
    "/booking/<int:booking_id>/cancel",
    methods=["POST"]
)
@login_required
def cancel_booking(
    booking_id
):

    conn = get_connection()


    conn.execute("""
        UPDATE bookings

        SET status = 'Cancelled'

        WHERE id = ?
        AND learner_id = ?
    """, (
        booking_id,
        session["user_id"]
    ))


    conn.commit()

    conn.close()


    return redirect(
        url_for("bookings")
    )


# =========================================================
# REVIEWS
# =========================================================

@app.route(
    "/mentor/<int:mentor_id>/review",
    methods=["POST"]
)
@login_required
def submit_review(
    mentor_id
):

    try:

        rating = int(
            request.form.get(
                "rating",
                "5"
            )
        )

    except ValueError:

        rating = 5


    rating = max(
        1,
        min(
            rating,
            5
        )
    )


    comment = request.form.get(
        "comment",
        ""
    ).strip()


    conn = get_connection()


    valid_booking = conn.execute("""
        SELECT id

        FROM bookings

        WHERE learner_id = ?
        AND mentor_id = ?
        AND status != 'Cancelled'

        LIMIT 1
    """, (
        session["user_id"],
        mentor_id
    )).fetchone()


    if valid_booking is None:

        conn.close()

        return redirect(
            url_for(
                "mentor_profile",
                mentor_id=mentor_id
            )
        )


    conn.execute("""
        INSERT INTO reviews
        (
            learner_id,
            mentor_id,
            rating,
            comment
        )

        VALUES (?, ?, ?, ?)

        ON CONFLICT(
            learner_id,
            mentor_id
        )

        DO UPDATE SET

            rating = excluded.rating,

            comment = excluded.comment,

            created_at = CURRENT_TIMESTAMP
    """, (
        session["user_id"],
        mentor_id,
        rating,
        comment
    ))


    average = conn.execute("""
        SELECT AVG(rating)

        FROM reviews

        WHERE mentor_id = ?
    """, (
        mentor_id,
    )).fetchone()[0]


    if average is not None:

        conn.execute("""
            UPDATE mentors

            SET rating = ?

            WHERE id = ?
        """, (
            round(
                average,
                1
            ),
            mentor_id
        ))


    conn.commit()

    conn.close()


    return redirect(
        url_for(
            "mentor_profile",
            mentor_id=mentor_id
        )
    )


# =========================================================
# MESSAGES
# =========================================================

@app.route("/messages")
@login_required
def messages():

    mentor_id = request.args.get(
        "mentor_id",
        type=int
    )


    conn = get_connection()


    mentor_list = conn.execute("""
        SELECT *

        FROM mentors

        ORDER BY name
    """).fetchall()


    selected_mentor = None

    message_list = []


    if mentor_list:

        if mentor_id is None:

            mentor_id = mentor_list[0]["id"]


        selected_mentor = conn.execute("""
            SELECT *

            FROM mentors

            WHERE id = ?
        """, (
            mentor_id,
        )).fetchone()


        if selected_mentor:

            message_list = conn.execute("""
                SELECT *

                FROM messages

                WHERE learner_id = ?
                AND mentor_id = ?

                ORDER BY id ASC
            """, (
                session["user_id"],
                mentor_id
            )).fetchall()


    conn.close()


    return render_template(
        "messages.html",
        mentors=mentor_list,
        selected_mentor=selected_mentor,
        messages=message_list
    )


@app.route(
    "/messages/send/<int:mentor_id>",
    methods=["POST"]
)
@login_required
def send_message(
    mentor_id
):

    content = request.form.get(
        "content",
        ""
    ).strip()


    if content:

        conn = get_connection()


        conn.execute("""
            INSERT INTO messages
            (
                learner_id,
                mentor_id,
                sender_role,
                content
            )

            VALUES (?, ?, 'learner', ?)
        """, (
            session["user_id"],
            mentor_id,
            content
        ))


        conn.commit()

        conn.close()


    return redirect(
        url_for(
            "messages",
            mentor_id=mentor_id
        )
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
@login_required
def profile():

    conn = get_connection()


    user = conn.execute("""
        SELECT *

        FROM users

        WHERE id = ?
    """, (
        session["user_id"],
    )).fetchone()


    mentor = conn.execute("""
        SELECT *

        FROM mentors

        WHERE user_id = ?

        LIMIT 1
    """, (
        session["user_id"],
    )).fetchone()


    booking_count = conn.execute("""
        SELECT COUNT(*)

        FROM bookings

        WHERE learner_id = ?
        AND status != 'Cancelled'
    """, (
        session["user_id"],
    )).fetchone()[0]


    review_count = conn.execute("""
        SELECT COUNT(*)

        FROM reviews

        WHERE learner_id = ?
    """, (
        session["user_id"],
    )).fetchone()[0]


    conn.close()


    return render_template(
        "profile.html",
        user=user,
        mentor=mentor,
        booking_count=booking_count,
        review_count=review_count
    )


# =========================================================
# BECOME A MENTOR
# =========================================================

@app.route(
    "/become-mentor",
    methods=[
        "GET",
        "POST"
    ]
)
@login_required
def become_mentor():

    conn = get_connection()


    user = conn.execute("""
        SELECT *

        FROM users

        WHERE id = ?
    """, (
        session["user_id"],
    )).fetchone()


    existing_mentor = conn.execute("""
        SELECT *

        FROM mentors

        WHERE user_id = ?

        LIMIT 1
    """, (
        session["user_id"],
    )).fetchone()


    if request.method == "POST":

        skills = request.form.get(
            "skills",
            ""
        ).strip()

        bio = request.form.get(
            "bio",
            ""
        ).strip()

        location = request.form.get(
            "location",
            "Library"
        )

        availability = request.form.get(
            "availability",
            "Available This Week"
        )

        try:

            price = int(
                request.form.get(
                    "price",
                    "100"
                )
            )

        except ValueError:

            price = 100


        price = max(
            0,
            price
        )


        if existing_mentor:

            conn.execute("""
                UPDATE mentors

                SET
                    skills = ?,
                    bio = ?,
                    location = ?,
                    availability = ?,
                    price = ?

                WHERE user_id = ?
            """, (
                skills,
                bio,
                location,
                availability,
                price,
                session["user_id"]
            ))

        else:

            conn.execute("""
                INSERT INTO mentors
                (
                    user_id,
                    name,
                    department,
                    year,
                    skills,
                    bio,
                    rating,
                    sessions,
                    location,
                    availability,
                    price
                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session["user_id"],
                user["name"],
                user["department"],
                user["year"],
                skills,
                bio,
                5.0,
                0,
                location,
                availability,
                price
            ))


        conn.commit()

        conn.close()


        return redirect(
            url_for("profile")
        )


    conn.close()


    location_names = [
        location["name"]
        for location in CAMPUS_LOCATIONS
    ]


    return render_template(
        "become_mentor.html",
        user=user,
        mentor=existing_mentor,
        locations=location_names
    )


# =========================================================
# CAMPUS MAP
# =========================================================

@app.route("/map")
@login_required
def campus_map():

    conn = get_connection()


    mentor_list = conn.execute("""
        SELECT
            id,
            name,
            department,
            skills,
            rating,
            location

        FROM mentors

        ORDER BY rating DESC
    """).fetchall()


    conn.close()


    mentors_data = [

        dict(mentor)

        for mentor in mentor_list

    ]


    return render_template(
        "campus_map.html",
        locations=CAMPUS_LOCATIONS,
        mentors=mentors_data
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )