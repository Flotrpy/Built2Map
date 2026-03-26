# Built2Map - Network Device Scanner

Built2Map is a foundational network scanner that maps your local home layout. It utilizes Scapy to craft targeted ARP requests, identifies device manufacturers via MAC address OUI lookup, flags newly discovered and unknown devices, and presents a responsive web dashboard utilizing Flask.

## Prerequisites
- Python 3.8+
- Scapy requires Npcap on Windows or `libpcap` on Linux to craft Layer 2 frames.
- **Administrative Privileges** are required to send raw packets on most operating systems.

## Setup Instructions
1. Install requirements into a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install scapy flask mac-vendor-lookup
   ```
2. Run database initialization and OUI downloads (if needed):
   ```bash
   python db.py
   python mac_lookup.py
   ```

## Running the Application
Since Scapy requires root/administrator access, launch the application via the provided helper scripts or prepend `sudo` on Linux.

**Windows:**
Right-click `run_admin.bat` and select `Run as Administrator`.

**Linux:**
```bash
sudo ./venv/bin/python app.py
```

Once started, the backend API and web interface will be available at `http://localhost:5000`. 
The background worker will automatically scan the current subnet every 30 seconds and update the local SQLite database. Refresh the page to see live updates.
