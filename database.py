from pathlib import Path
import sqlite3

from werkzeug.security import generate_password_hash


# =========================================================
# DATABASE LOCATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE = BASE_DIR / "peerup.db"


def get_connection():

    conn = sqlite3.connect(
        str(DATABASE)
    )

    conn.row_factory = sqlite3.Row

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conn


def column_exists(
    conn,
    table_name,
    column_name
):

    columns = conn.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return any(
        column["name"] == column_name
        for column in columns
    )


def add_column_if_missing(
    conn,
    table_name,
    column_name,
    column_definition
):

    if not column_exists(
        conn,
        table_name,
        column_name
    ):

        conn.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_definition}
            """
        )


def init_db():

    conn = get_connection()


    # =====================================================
    # USERS
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id TEXT UNIQUE NOT NULL,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            department TEXT,

            year TEXT,

            password TEXT NOT NULL
        )
    """)


    # =====================================================
    # MENTORS
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS mentors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            name TEXT NOT NULL,

            department TEXT NOT NULL,

            year TEXT NOT NULL,

            skills TEXT NOT NULL,

            bio TEXT,

            rating REAL DEFAULT 0,

            sessions INTEGER DEFAULT 0,

            location TEXT,

            availability TEXT,

            price INTEGER DEFAULT 0,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
        )
    """)


    add_column_if_missing(
        conn,
        "mentors",
        "user_id",
        "user_id INTEGER"
    )


    # =====================================================
    # BOOKINGS
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            learner_id INTEGER NOT NULL,

            mentor_id INTEGER NOT NULL,

            session_date TEXT NOT NULL,

            session_time TEXT NOT NULL,

            session_type TEXT NOT NULL,

            exchange_type TEXT NOT NULL,

            exchange_skill TEXT,

            notes TEXT,

            status TEXT DEFAULT 'Confirmed',

            payment_status TEXT DEFAULT 'Not Required',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (learner_id)
            REFERENCES users(id),

            FOREIGN KEY (mentor_id)
            REFERENCES mentors(id)
        )
    """)


    add_column_if_missing(
        conn,
        "bookings",
        "exchange_skill",
        "exchange_skill TEXT"
    )


    add_column_if_missing(
        conn,
        "bookings",
        "payment_status",
        "payment_status TEXT DEFAULT 'Not Required'"
    )


    # =====================================================
    # MESSAGES
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            learner_id INTEGER NOT NULL,

            mentor_id INTEGER NOT NULL,

            sender_role TEXT NOT NULL,

            content TEXT NOT NULL,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (learner_id)
            REFERENCES users(id),

            FOREIGN KEY (mentor_id)
            REFERENCES mentors(id)
        )
    """)


    # =====================================================
    # REVIEWS
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            learner_id INTEGER NOT NULL,

            mentor_id INTEGER NOT NULL,

            rating INTEGER NOT NULL,

            comment TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (learner_id)
            REFERENCES users(id),

            FOREIGN KEY (mentor_id)
            REFERENCES mentors(id),

            UNIQUE (
                learner_id,
                mentor_id
            )
        )
    """)


    # =====================================================
    # DEFAULT USERS
    # =====================================================

    default_users = [

        (
            "312223500001",
            "PeerUp Student",
            "student@ssn.edu.in",
            "Biomedical Engineering",
            "2nd Year",
            generate_password_hash(
                "123456"
            )
        ),

        (
            "312223500002",
            "Aditya Raj",
            "aditya@ssn.edu.in",
            "CSE",
            "3rd Year",
            generate_password_hash(
                "123456"
            )
        ),

        (
            "312223500003",
            "Sneha Iyer",
            "sneha@ssn.edu.in",
            "ECE",
            "2nd Year",
            generate_password_hash(
                "123456"
            )
        )

    ]


    for user in default_users:

        conn.execute("""
            INSERT OR IGNORE INTO users
            (
                student_id,
                name,
                email,
                department,
                year,
                password
            )

            VALUES (?, ?, ?, ?, ?, ?)
        """, user)


    # =====================================================
    # DEFAULT MENTORS
    # =====================================================

    mentor_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM mentors
        """
    ).fetchone()[0]


    if mentor_count == 0:

        mentors = [

            (
                "Arjun Kumar",
                "CSE",
                "3rd Year",
                "Python, Machine Learning, Data Science",
                "I enjoy helping students understand Python and machine learning through practical examples and small projects.",
                4.9,
                24,
                "IT Block",
                "Available Today",
                150
            ),

            (
                "Diya Sharma",
                "ECE",
                "2nd Year",
                "Figma, UI/UX, Canva",
                "UI/UX enthusiast helping students turn ideas into clean interfaces and polished prototypes.",
                4.8,
                18,
                "ECE Block",
                "Available Tomorrow",
                120
            ),

            (
                "Rahul Menon",
                "MECH",
                "4th Year",
                "Guitar, Music Theory, Chords",
                "Guitar mentor for beginners and intermediate players.",
                5.0,
                31,
                "Central Perk",
                "Available Today",
                100
            ),

            (
                "Nisha Ravi",
                "BME",
                "3rd Year",
                "MATLAB, Signals, Biomedical Instrumentation",
                "I help students with MATLAB basics, signal processing and biomedical instrumentation concepts.",
                4.7,
                16,
                "BME Block",
                "Available This Week",
                140
            ),

            (
                "Karthik S",
                "EEE",
                "4th Year",
                "Circuits, Arduino, Embedded Systems",
                "Interested in electronics and embedded systems with hands-on experience in Arduino and microcontrollers.",
                4.9,
                27,
                "EEE Block",
                "Available Today",
                160
            ),

            (
                "Meera Iyer",
                "CSE",
                "3rd Year",
                "C++, DSA, Competitive Programming",
                "I simplify data structures and C++ concepts using visual explanations and practice problems.",
                4.8,
                22,
                "Library",
                "Available Tomorrow",
                150
            )

        ]


        conn.executemany("""
            INSERT INTO mentors
            (
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

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, mentors)


    # =====================================================
    # SAMPLE REVIEWS
    # =====================================================

    review_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM reviews
        """
    ).fetchone()[0]


    if review_count == 0:

        aditya = conn.execute("""
            SELECT id
            FROM users
            WHERE email = 'aditya@ssn.edu.in'
        """).fetchone()


        sneha = conn.execute("""
            SELECT id
            FROM users
            WHERE email = 'sneha@ssn.edu.in'
        """).fetchone()


        if aditya and sneha:

            reviews = [

                (
                    aditya["id"],
                    1,
                    5,
                    "Arjun explains concepts very clearly and gives practical examples."
                ),

                (
                    sneha["id"],
                    1,
                    5,
                    "Really helpful Python session. Would definitely book again."
                ),

                (
                    aditya["id"],
                    2,
                    5,
                    "Diya helped me clean up my Figma prototype quickly."
                ),

                (
                    sneha["id"],
                    3,
                    5,
                    "Very patient and beginner friendly guitar session."
                )

            ]


            conn.executemany("""
                INSERT OR IGNORE INTO reviews
                (
                    learner_id,
                    mentor_id,
                    rating,
                    comment
                )

                VALUES (?, ?, ?, ?)
            """, reviews)


    # =====================================================
    # SAMPLE MESSAGES
    # =====================================================

    main_user = conn.execute("""
        SELECT id
        FROM users
        WHERE email = 'student@ssn.edu.in'
    """).fetchone()


    message_count = conn.execute(
        """
        SELECT COUNT(*)
        FROM messages
        """
    ).fetchone()[0]


    if (
        main_user
        and message_count == 0
    ):

        messages = [

            (
                main_user["id"],
                1,
                "mentor",
                "Hey! Happy to help with Python. What topic are you currently working on?"
            ),

            (
                main_user["id"],
                2,
                "mentor",
                "Hi! Feel free to send your Figma or UI/UX questions here."
            )

        ]


        conn.executemany("""
            INSERT INTO messages
            (
                learner_id,
                mentor_id,
                sender_role,
                content
            )

            VALUES (?, ?, ?, ?)
        """, messages)


    conn.commit()

    conn.close()


    print(
        f"PeerUp database: {DATABASE}"
    )