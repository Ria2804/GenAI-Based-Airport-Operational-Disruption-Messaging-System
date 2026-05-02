import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "disruptions.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disruptions (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at          TEXT,
            flight_number       TEXT,
            airline             TEXT,
            origin              TEXT,
            destination         TEXT,
            scheduled_departure TEXT,
            delay_minutes       INTEGER,
            disruption_type     TEXT,
            severity            INTEGER,
            notes               TEXT,
            passenger_msg       TEXT,
            pilot_msg           TEXT,
            staff_msg           TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_disruption(payload, messages: dict):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO disruptions (
                created_at, flight_number, airline, origin, destination,
                scheduled_departure, delay_minutes, disruption_type, severity,
                notes, passenger_msg, pilot_msg, staff_msg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.utcnow().isoformat(),
            payload.flight_number,
            payload.airline,
            payload.origin,
            payload.destination,
            payload.scheduled_departure,
            payload.delay_minutes,
            payload.disruption_type,
            payload.severity,
            payload.notes,
            messages.get("passenger", ""),
            messages.get("pilot", ""),
            messages.get("staff", ""),
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB] Failed to save disruption: {e}")


def get_all_disruptions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM disruptions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows