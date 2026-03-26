import time
import threading
from flask import Flask, render_template, jsonify
from scanner import get_local_subnet, arp_sweep
from mac_lookup import init_mac_lookup, get_vendor_sync
from db import init_db, upsert_device, get_all_devices

app = Flask(__name__)

# Cache the subnet globally for the background thread
SUBNET = None

def get_hostname(ip):
    import socket
    try:
        # socket.gethostbyaddr often queries local mDNS/LLMNR to resolve the name on Windows/Linux
        host, _, _ = socket.gethostbyaddr(ip)
        return host
    except Exception:
        return "Unknown"

def background_scan_worker():
    """Runs continuously in the background to scan the network."""
    global SUBNET
    while True:
        if SUBNET:
            print(f"[Worker] Starting scan on {SUBNET}...")
            devices = arp_sweep(SUBNET)
            for d in devices:
                vendor = get_vendor_sync(d['mac'])
                hostname = get_hostname(d['ip'])
                is_new = upsert_device(d['mac'], d['ip'], vendor, hostname=hostname)
                if is_new:
                    from db import add_event
                    add_event(f"New Device Discovered: {d['ip']} ({vendor})", "discovery")
                    print(f"*** NEW DEVICE FOUND: {d['mac']} ({d['ip']}) - {vendor} [{hostname}] ***")
            print("[Worker] Scan complete. Sleeping for 30 seconds.")
        else:
            print("[Worker] No subnet detected. Retrying in 30s...")
            SUBNET = get_local_subnet()
            
        time.sleep(30)

@app.route("/")
def index():
    """Renders the main dashboard."""
    return render_template("index.html")

@app.route("/api/devices")
def api_devices():
    """Returns JSON of all tracked devices."""
    devices = get_all_devices()
    return jsonify(devices)

from flask import request
from db import update_device_status, get_recent_events

@app.route("/api/device/status", methods=['POST'])
def update_status():
    """Updates the status of a specific device."""
    data = request.json
    mac = data.get('mac')
    status = data.get('status')
    if mac and status:
        update_device_status(mac, status)
        # Log this event
        from db import add_event
        add_event(f"Device {mac} status manually set to {status}.", "user")
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route("/api/notifications")
def api_notifications():
    """Returns the event log."""
    return jsonify(get_recent_events())

@app.route("/api/topology")
def api_topology():
    """Returns network nodes and edges for vis.js map."""
    devices = get_all_devices()
    nodes = [{"id": "router", "label": "Network Gateway", "group": "router", "title": f"Gateway: {SUBNET}"}]
    edges = []
    
    for idx, d in enumerate(devices):
        node_id = f"dev_{idx}"
        label = d['hostname'] if d['hostname'] != 'Unknown' else d['ip']
        nodes.append({
            "id": node_id,
            "label": label,
            "title": f"MAC: {d['mac']}<br>IP: {d['ip']}<br>Vendor: {d['vendor']}",
            "group": d['status']
        })
        # Connect everything to the router for a classic star topology
        edges.append({"from": "router", "to": node_id})
        
    return jsonify({"nodes": nodes, "edges": edges})

if __name__ == "__main__":
    # Initialize components
    init_db()
    init_mac_lookup()
    SUBNET = get_local_subnet()
    
    # Start background scanner thread
    thread = threading.Thread(target=background_scan_worker, daemon=True)
    thread.start()
    
    # Run Flask application
    app.run(host="0.0.0.0", port=5000, debug=False)
