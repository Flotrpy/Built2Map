import sqlite3

def run_migration():
    conn = sqlite3.connect('network_scanner.db')
    c = conn.cursor()
    try:
        c.execute("ALTER TABLE devices ADD COLUMN hostname TEXT DEFAULT 'Unknown'")
        print("[*] Successfully added 'hostname' column to database.")
    except sqlite3.OperationalError as e:
        print(f"[-] Migration skipped or failed: {e}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    run_migration()
