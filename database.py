
import sqlite3
from datetime import datetime

DB_NAME = "parksmart.db"


def connect():
    return sqlite3.connect(DB_NAME)


# INITIALIZE DATABASE
def initialize_database():
    conn = connect()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS slots (
                slot_number TEXT PRIMARY KEY,
                distance INTEGER,
                status TEXT DEFAULT 'Available'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_number TEXT,
                slot_number TEXT,
                entry_time TEXT,
                exit_time TEXT,
                status TEXT
            )
        """)

        default_slots = [
            ("A1", 10, "Available"),
            ("A2", 15, "Available"),
            ("A3", 20, "Available"),
            ("B1", 15, "Available"),
            ("B2", 20, "Available"),
            ("B3", 25, "Available"),
            ("C1", 25, "Available"),
            ("C2", 30, "Available")
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO slots
            (slot_number, distance, status)
            VALUES (?, ?, ?)
        """, default_slots)

        conn.commit()

    finally:
        conn.close()


# GET ALL PARKING SLOTS
def get_slots():
    conn = connect()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT slot_number, distance, status
            FROM slots
            ORDER BY slot_number
        """)

        rows = cursor.fetchall()

        return [
            {
                "slot_number": row[0],
                "distance": row[1],
                "status": row[2]
            }
            for row in rows
        ]

    finally:
        conn.close()


# ALLOCATE A PARKING SLOT
def allocate_parking(vehicle, slot):
    vehicle = vehicle.strip().upper()
    slot = slot.strip().upper()

    if not vehicle or not slot:
        return False

    conn = connect()

    try:
        cursor = conn.cursor()

        # Lock the write transaction before checking availability.
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT status
            FROM slots
            WHERE slot_number = ?
        """, (slot,))

        result = cursor.fetchone()

        if not result or result[0] != "Available":
            conn.rollback()
            return False

        # Prevent the same vehicle from having two active bookings.
        cursor.execute("""
            SELECT id
            FROM records
            WHERE UPPER(vehicle_number) = ?
            AND status = 'Parked'
            LIMIT 1
        """, (vehicle,))

        if cursor.fetchone():
            conn.rollback()
            return False

        entry_time = datetime.now().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )

        cursor.execute("""
            UPDATE slots
            SET status = 'Occupied'
            WHERE slot_number = ?
        """, (slot,))

        cursor.execute("""
            INSERT INTO records
            (vehicle_number, slot_number, entry_time, exit_time, status)
            VALUES (?, ?, ?, ?, ?)
        """, (vehicle, slot, entry_time, "", "Parked"))

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# RELEASE A PARKING SLOT
def release_parking(vehicle):
    vehicle = vehicle.strip().upper()

    if not vehicle:
        return None

    conn = connect()

    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")

        cursor.execute("""
            SELECT id, slot_number
            FROM records
            WHERE UPPER(vehicle_number) = ?
            AND status = 'Parked'
            ORDER BY id DESC
            LIMIT 1
        """, (vehicle,))

        record = cursor.fetchone()

        if not record:
            conn.rollback()
            return None

        record_id, slot = record

        exit_time = datetime.now().strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )

        cursor.execute("""
            UPDATE records
            SET exit_time = ?, status = 'Exited'
            WHERE id = ?
        """, (exit_time, record_id))

        cursor.execute("""
            UPDATE slots
            SET status = 'Available'
            WHERE slot_number = ?
        """, (slot,))

        conn.commit()
        return slot

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# GET ALL PARKING RECORDS
def get_records():
    conn = connect()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, vehicle_number, slot_number,
                   entry_time, exit_time, status
            FROM records
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    finally:
        conn.close()


# GET DASHBOARD STATISTICS
def get_parking_stats():
    slots = get_slots()

    total = len(slots)
    occupied = sum(
        1 for slot in slots
        if slot["status"] == "Occupied"
    )
    available = total - occupied

    occupancy = (
        (occupied / total) * 100
        if total > 0 else 0
    )

    return {
        "total": total,
        "occupied": occupied,
        "available": available,
        "occupancy": occupancy
    }


# SEARCH FOR A VEHICLE
def search_vehicle(vehicle):
    vehicle = vehicle.strip().upper()

    if not vehicle:
        return None

    conn = connect()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, vehicle_number, slot_number,
                   entry_time, exit_time, status
            FROM records
            WHERE UPPER(vehicle_number) = ?
            ORDER BY id DESC
            LIMIT 1
        """, (vehicle,))

        return cursor.fetchone()

    finally:
        conn.close()


# GET RECENT PARKING ACTIVITY
def get_recent_records(limit=5):
    conn = connect()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, vehicle_number, slot_number,
                   entry_time, exit_time, status
            FROM records
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        return cursor.fetchall()

    finally:
        conn.close()
