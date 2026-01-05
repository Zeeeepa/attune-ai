"""Authentication database using SQLite.

Provides secure user storage with bcrypt password hashing.
Thread-safe operations with connection pooling.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import bcrypt


class AuthDatabase:
    """SQLite database for user authentication.

    Features:
    - Bcrypt password hashing (cost factor 12)
    - Thread-safe connection handling
    - Failed login attempt tracking
    - Automatic schema initialization
    """

    def __init__(self, db_path: str | None = None):
        """Initialize authentication database.

        Args:
            db_path: Path to SQLite database file.
                    Defaults to backend/data/auth.db
        """
        if db_path is None:
            # Default to backend/data/auth.db
            backend_dir = Path(__file__).parent.parent.parent
            data_dir = backend_dir / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "auth.db")

        self.db_path = db_path
        self._init_schema()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection with automatic cleanup."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        """Initialize database schema if not exists."""
        with self._get_connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    license_key TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS login_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    success INTEGER NOT NULL,  -- 0=failed, 1=success
                    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_login_attempts_email ON login_attempts(email, attempted_at);
                """
            )

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Bcrypt hash string
        """
        # Encode password to bytes
        password_bytes = password.encode("utf-8")
        # Generate salt and hash (cost factor 12)
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password_bytes, salt)
        # Return as string for database storage
        return password_hash.decode("utf-8")

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash.

        Args:
            password: Plain text password to verify
            password_hash: Stored bcrypt hash

        Returns:
            True if password matches hash
        """
        password_bytes = password.encode("utf-8")
        hash_bytes = password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)

    def create_user(
        self, email: str, password: str, name: str, license_key: str | None = None
    ) -> int:
        """Create new user with hashed password.

        Args:
            email: User email (must be unique)
            password: Plain text password (will be hashed)
            name: User's full name
            license_key: Optional license key

        Returns:
            User ID of created user

        Raises:
            sqlite3.IntegrityError: If email already exists
        """
        password_hash = self._hash_password(password)

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users (email, password_hash, name, license_key)
                VALUES (?, ?, ?, ?)
                """,
                (email, password_hash, name, license_key),
            )
            return cursor.lastrowid

    def verify_user(self, email: str, password: str) -> dict | None:
        """Verify user credentials.

        Args:
            email: User email
            password: Plain text password to verify

        Returns:
            User dict if credentials valid, None otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, email, password_hash, name, license_key FROM users WHERE email = ?",
                (email,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            # Verify password hash
            if not self._verify_password(password, row["password_hash"]):
                return None

            # Update last login
            conn.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (row["id"],),
            )

            return {
                "id": row["id"],
                "email": row["email"],
                "name": row["name"],
                "license_key": row["license_key"],
            }

    def record_login_attempt(
        self, email: str, success: bool, ip_address: str | None = None
    ) -> None:
        """Record login attempt for rate limiting.

        Args:
            email: Email attempted
            success: Whether login succeeded
            ip_address: Optional IP address
        """
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO login_attempts (email, success, ip_address) VALUES (?, ?, ?)",
                (email, 1 if success else 0, ip_address),
            )

    def get_failed_attempts(self, email: str, minutes: int = 15) -> int:
        """Count recent failed login attempts.

        Args:
            email: Email to check
            minutes: Time window to check (default 15 minutes)

        Returns:
            Number of failed attempts in time window
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT COUNT(*) as count FROM login_attempts
                WHERE email = ?
                  AND success = 0
                  AND attempted_at > datetime('now', '-' || ? || ' minutes')
                """,
                (email, minutes),
            )
            row = cursor.fetchone()
            return row["count"] if row else 0

    def user_exists(self, email: str) -> bool:
        """Check if user exists.

        Args:
            email: Email to check

        Returns:
            True if user exists
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT 1 FROM users WHERE email = ? LIMIT 1", (email,))
            return cursor.fetchone() is not None
