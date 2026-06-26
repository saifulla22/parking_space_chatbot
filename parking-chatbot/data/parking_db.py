import sqlite3
from datetime import datetime
from typing import Optional

DB_PATH = "parking.db"


class ParkingDatabase:
    """
    Manages dynamic parking data stored in SQLite:
    - Space availability (updated daily)
    - Current prices
    - Working hours
    - Pending/confirmed reservations
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS availability (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    total_spaces INTEGER DEFAULT 200,
                    available_spaces INTEGER DEFAULT 200,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rate_type TEXT NOT NULL UNIQUE,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS working_hours (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    day_of_week TEXT NOT NULL UNIQUE,
                    open_time TEXT NOT NULL,
                    close_time TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reservations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    surname TEXT NOT NULL,
                    car_number TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            self._seed_data(cursor, conn)

    def _seed_data(self, cursor, conn):
        cursor.execute("SELECT COUNT(*) FROM prices")
        if cursor.fetchone()[0] == 0:
            prices = [
                ("hourly", 3.00),
                ("daily", 20.00),
                ("weekly", 100.00),
                ("monthly", 250.00),
            ]
            cursor.executemany(
                "INSERT INTO prices (rate_type, amount) VALUES (?, ?)", prices
            )

        cursor.execute("SELECT COUNT(*) FROM working_hours")
        if cursor.fetchone()[0] == 0:
            hours = [
                ("Monday", "06:00", "23:00"),
                ("Tuesday", "06:00", "23:00"),
                ("Wednesday", "06:00", "23:00"),
                ("Thursday", "06:00", "23:00"),
                ("Friday", "06:00", "23:00"),
                ("Saturday", "07:00", "22:00"),
                ("Sunday", "08:00", "20:00"),
            ]
            cursor.executemany(
                "INSERT INTO working_hours (day_of_week, open_time, close_time) VALUES (?, ?, ?)",
                hours,
            )
        conn.commit()

    # -------------------------------------------------------------------------
    # Read methods
    # -------------------------------------------------------------------------

    def get_availability(self, date: Optional[str] = None) -> dict:
        """Return space availability for a given date (defaults to today)."""
        date = date or datetime.now().strftime("%Y-%m-%d")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT total_spaces, available_spaces FROM availability WHERE date = ?",
                (date,),
            )
            row = cursor.fetchone()
            if row:
                return {"date": date, "total": row[0], "available": row[1]}
            # No record for this date means no bookings yet
            return {"date": date, "total": 200, "available": 200}

    def get_prices(self) -> list:
        """Return all current pricing rates."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT rate_type, amount, currency FROM prices")
            return [
                {"rate_type": r[0], "amount": r[1], "currency": r[2]}
                for r in cursor.fetchall()
            ]

    def get_working_hours(self) -> list:
        """Return working hours for all days."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT day_of_week, open_time, close_time FROM working_hours"
            )
            return [
                {"day": r[0], "open": r[1], "close": r[2]}
                for r in cursor.fetchall()
            ]

    # -------------------------------------------------------------------------
    # Write methods
    # -------------------------------------------------------------------------

    def save_reservation(
        self, name: str, surname: str, car_number: str, start_date: str, end_date: str
    ) -> int:
        """Save a pending reservation and return its ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO reservations (name, surname, car_number, start_date, end_date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, surname, car_number, start_date, end_date),
            )
            conn.commit()
            return cursor.lastrowid

    def update_reservation_status(self, reservation_id: int, status: str):
        """Update the status of a reservation (e.g., 'approved', 'rejected')."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE reservations SET status = ? WHERE id = ?",
                (status, reservation_id),
            )
            conn.commit()
