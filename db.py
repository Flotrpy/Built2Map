import sqlite3
from datetime import datetime
import os

DB_FILE = 'network_scanner.db'


def init_db():
    """Initialize the SQLite database schema."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            mac_address TEXT PRIMARY KEY,
            ip_address TEXT,
            vendor TEXT,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP,
            status TEXT DEFAULT 'unknown',
            hostname TEXT DEFAULT 'Unknown'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP,
            message TEXT,
            type TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_event(message, event_type="info"):
    """Log a system or network event for the Notifications tab."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.now()
    c.execute("INSERT INTO events (timestamp, message, type) VALUES (?, ?, ?)", (now, message, event_type))
    conn.commit()
    conn.close()

def get_recent_events(limit=50):
    """Retrieve chronologically sorted events."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Check if events table exists; if not, return empty list (prevents crashes before re-migration)
    try:
        c.execute("SELECT timestamp, message, type FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = c.fetchall()
    except sqlite3.OperationalError:
        rows = []
    conn.close()
    
    return [ {"timestamp": r[0], "message": r[1], "type": r[2]} for r in rows ]

def upsert_device(mac, ip, vendor, hostname="Unknown"):
    """
    Inserts a newly seen device or updates its last_seen timestamp and IP/hostname.
    Returns True if the device is newly discovered, False if it already existed.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    now = datetime.now()
    c.execute("SELECT status FROM devices WHERE mac_address=?", (mac,))
    row = c.fetchone()
    
    is_new = False
    if row is None:
        # Automatically determine initial status based on vendor recognition
        if vendor == "Unknown" or "Randomized" in vendor:
            auto_status = "unknown"
        else:
            auto_status = "trusted"
            
        # New device
        c.execute('''
            INSERT INTO devices (mac_address, ip_address, vendor, first_seen, last_seen, status, hostname)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (mac, ip, vendor, now, now, auto_status, hostname))
        is_new = True
    else:
        # Existing device, update IP, hostname and last seen
        c.execute('''
            UPDATE devices
            SET ip_address = ?, hostname = ?, last_seen = ?
            WHERE mac_address = ?
        ''', (ip, hostname, now, mac))
        
    conn.commit()
    conn.close()
    return is_new

def get_all_devices():
    """Retrieve all tracked devices."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Check if hostname column exists (graceful degradation)
    try:
        c.execute("SELECT mac_address, ip_address, vendor, first_seen, last_seen, status, hostname FROM devices")
        rows = c.fetchall()
    except sqlite3.OperationalError:
        c.execute("SELECT mac_address, ip_address, vendor, first_seen, last_seen, status FROM devices")
        old_rows = c.fetchall()
        rows = [r + ("Unknown",) for r in old_rows]
        
    conn.close()
    
    devices = []
    for r in rows:
        devices.append({
            "mac": r[0],
            "ip": r[1],
            "vendor": r[2],
            "first_seen": r[3],
            "last_seen": r[4],
            "status": r[5],
            "hostname": r[6] if len(r) > 6 else "Unknown"
        })
    return devices

def update_device_status(mac, status):
    """Manually update the status of a device (e.g. 'trusted', 'blocked')."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE devices SET status=? WHERE mac_address=?", (status, mac))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("[*] Database initialized!")
