import sqlite3

def update_all():
    conn = sqlite3.connect('network_scanner.db')
    c = conn.cursor()
    c.execute("UPDATE devices SET status='unknown' WHERE vendor='Unknown' OR vendor LIKE '%Randomized%'")
    c.execute("UPDATE devices SET status='trusted' WHERE status='new_unknown'")
    conn.commit()
    conn.close()
    print("Database updated!")

if __name__ == "__main__":
    update_all()
