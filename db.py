"""

db.py — Database layer for the Volunteer Registration System (MySQL version).

Handles connection, validated inserts, and read queries against a MySQL
server. The table itself is created by schema.sql (run that once first).
Uses parameterized queries throughout to prevent SQL injection.

Connection settings are read from environment variables so credentials
never sit in the code. Copy .env.example to .env and fill in your values,
or set the environment variables directly.
"""

import os
import re
from datetime import datetime
from contextlib import contextmanager
import streamlit as st
import mysql.connector
from mysql.connector import errorcode

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env is optional; env vars can also be set directly

if hasattr(st, "secrets") and "DB_HOST" in st.secrets:
    DB_CONFIG = {
        "host": st.secrets["DB_HOST"],
        "port": int(st.secrets["DB_PORT"]),
        "user": st.secrets["DB_USER"],
        "password": st.secrets["DB_PASSWORD"],
        "database": st.secrets["DB_NAME"],
        "ssl_disabled": False,
    }
else:
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "volunteer_db"),
        "ssl_disabled": False,
    }

EMAIL_RE = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$")
PHONE_RE = re.compile(r"^\+?\d{7,15}$")


@contextmanager
def get_connection():
    """
    Opens a MySQL connection using DB_CONFIG. Raises a clear error if the
    server is unreachable or the database/table hasn't been created yet.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise ConnectionError("MySQL access denied — check DB_USER/DB_PASSWORD.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise ConnectionError(
                f"Database '{DB_CONFIG['database']}' doesn't exist — run schema.sql first."
            )
        else:
            raise ConnectionError(f"Could not connect to MySQL: {err}")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """
    No-op placeholder: the table is created by schema.sql against the
    server, not by the app itself. Kept so app.py can call init_db()
    the same way regardless of backend.
    """
    pass


class ValidationError(Exception):
    """Raised when submitted volunteer data fails validation."""
    pass


def validate_volunteer(data: dict):
    required = ["name", "age", "gender", "email", "phone",
                "area_of_interest", "availability"]
    for field in required:
        if not str(data.get(field, "")).strip():
            raise ValidationError(f"'{field.replace('_', ' ').title()}' is required.")

    if not str(data["name"]).strip().replace(" ", "").isalpha():
        raise ValidationError("Name should contain letters only.")

    try:
        age = int(data["age"])
    except (ValueError, TypeError):
        raise ValidationError("Age must be a whole number.")
    if not (15 <= age <= 100):
        raise ValidationError("Age must be between 15 and 100.")

    if not EMAIL_RE.match(str(data["email"]).strip()):
        raise ValidationError("Enter a valid email address.")

    if not PHONE_RE.match(str(data["phone"]).strip()):
        raise ValidationError("Enter a valid phone number (7–15 digits).")


def is_duplicate(email: str, phone: str):
    """Returns a message if email or phone is already registered, else None."""
    with get_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT email, phone FROM volunteers WHERE email = %s OR phone = %s",
            (email.strip(), phone.strip())
        )
        row = cur.fetchone()
        cur.close()
    if row:
        if row["email"] == email.strip():
            return "This email is already registered."
        return "This phone number is already registered."
    return None


def add_volunteer(data: dict):
    """
    Validates and inserts a volunteer record.
    Raises ValidationError if the data is invalid or a duplicate.
    """
    validate_volunteer(data)
    dup_msg = is_duplicate(data["email"], data["phone"])
    if dup_msg:
        raise ValidationError(dup_msg)

    with get_connection() as conn:
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO volunteers
                    (name, age, gender, email, phone, address,
                     area_of_interest, skills, availability, registered_on)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data["name"].strip(),
                int(data["age"]),
                data["gender"].strip(),
                data["email"].strip().lower(),
                data["phone"].strip(),
                data.get("address", "").strip(),
                data["area_of_interest"].strip(),
                data.get("skills", "").strip(),
                data["availability"].strip(),
                datetime.now().isoformat(timespec="seconds"),
            ))
        except mysql.connector.IntegrityError:
            # Safety net in case of a race between the duplicate check and insert
            raise ValidationError("Email or phone is already registered.")
        finally:
            cur.close()


def get_all_volunteers():
    """Returns all volunteer rows as a list of dicts."""
    with get_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM volunteers ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
    return rows


def get_stats():
    """Returns summary counts used by the dashboard."""
    with get_connection() as conn:
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT COUNT(*) AS c FROM volunteers")
        total = cur.fetchone()["c"]

        cur.execute("""
            SELECT area_of_interest, COUNT(*) AS c FROM volunteers
            GROUP BY area_of_interest ORDER BY c DESC
        """)
        by_interest = cur.fetchall()

        cur.execute("""
            SELECT gender, COUNT(*) AS c FROM volunteers GROUP BY gender
        """)
        by_gender = cur.fetchall()

        cur.close()

    return {"total": total, "by_interest": by_interest, "by_gender": by_gender}
def delete_all_volunteers():
    """Deletes all volunteer registration records."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM volunteers")
        cur.close()
