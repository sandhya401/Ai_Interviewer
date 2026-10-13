
import os
import re
import hmac
import hashlib
import secrets
import sqlite3
from pathlib import Path


# Project root is the parent of the services directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = Path(
    os.getenv(
        "AUTH_DATABASE_PATH",
        str(PROJECT_ROOT / "data" / "ai_interviewer.db"),
    )
)


def get_connection():
    """Create a SQLite connection and ensure the data directory exists."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        str(DATABASE_PATH),
        timeout=10,
    )
    connection.row_factory = sqlite3.Row
    return connection


def init_auth_db():
    """Create the users table if it does not already exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS auth_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def validate_username(username):
    username = (username or "").strip()

    if not 3 <= len(username) <= 30:
        return False, "Username must contain 3–30 characters."

    if not re.fullmatch(r"[A-Za-z0-9_.-]+", username):
        return (
            False,
            "Username can contain letters, numbers, dots, underscores, and hyphens.",
        )

    return True, ""


def validate_email(email):
    email = (email or "").strip()

    if len(email) > 254:
        return False, "Email address is too long."

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.fullmatch(pattern, email):
        return False, "Enter a valid email address."

    return True, ""


def validate_password(password):
    if not isinstance(password, str) or len(password) < 10:
        return False, "Password must contain at least 10 characters."

    if len(password) > 128:
        return False, "Password must contain no more than 128 characters."

    if not any(character.isalpha() for character in password):
        return False, "Password must contain at least one letter."

    if not any(character.isdigit() for character in password):
        return False, "Password must contain at least one number."

    return True, ""


def hash_password(password):
    """Return a salted PBKDF2 password hash, never the original password."""
    salt = secrets.token_bytes(16)

    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600_000,
    )

    return f"pbkdf2_sha256$600000${salt.hex()}${derived_key.hex()}"


def verify_password(password, stored_hash):
    """Verify a password against its saved PBKDF2 hash."""
    try:
        algorithm, iterations_text, salt_hex, expected_hex = (
            stored_hash.split("$")
        )

        if algorithm != "pbkdf2_sha256":
            return False

        iterations = int(iterations_text)

        # Reject malformed or unexpectedly expensive stored parameters.
        if not 100_000 <= iterations <= 1_000_000:
            return False

        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(expected_hex)

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )

        return hmac.compare_digest(actual, expected)

    except (ValueError, TypeError, AttributeError):
        return False


def register_user(username, email, password):
    """
    Register a user.

    Returns:
        (True, message) when registration succeeds.
        (False, message) when validation fails or the account exists.
    """
    init_auth_db()

    username = (username or "").strip()
    email = (email or "").strip().lower()

    valid, message = validate_username(username)
    if not valid:
        return False, message

    valid, message = validate_email(email)
    if not valid:
        return False, message

    valid, message = validate_password(password)
    if not valid:
        return False, message

    password_hash = hash_password(password)

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO auth_users (
                    username,
                    email,
                    password_hash
                )
                VALUES (?, ?, ?)
                """,
                (username, email, password_hash),
            )

        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        return (
            False,
            "That username or email address is already registered.",
        )


def authenticate_user(username_or_email, password):
    """
    Authenticate using either username or email.

    Returns a public user dictionary on success, or None on failure.
    The password hash is never returned.
    """
    init_auth_db()

    identifier = (username_or_email or "").strip()

    if not identifier or not isinstance(password, str) or not password:
        return None

    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT id, username, email, password_hash, created_at
            FROM auth_users
            WHERE username = ? OR email = ?
            LIMIT 1
            """,
            (identifier, identifier),
        ).fetchone()

    if user is None:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"],
    }


def get_user_by_id(user_id):
    """Retrieve safe, non-secret user information by ID."""
    init_auth_db()

    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT id, username, email, created_at
            FROM auth_users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()

    return dict(user) if user else None
