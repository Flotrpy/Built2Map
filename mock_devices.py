import time
from db import upsert_device

def inject_mock_devices():
    print("Injecting mock devices into the database...")
    
    # Device 1: Apple iPhone
    is_new = upsert_device("00:1A:2B:3C:4D:5E", "192.168.1.15", "Apple, Inc.")
    print(f"Injected Apple Device. Was it new? {is_new}")
    time.sleep(1)
    
    # Device 2: Samsung TV
    is_new = upsert_device("11:22:33:44:55:66", "192.168.1.42", "Samsung Electronics")
    print(f"Injected Samsung TV. Was it new? {is_new}")
    time.sleep(1)
    
    # Device 3: Unknown Smart Plug
    is_new = upsert_device("AA:BB:CC:DD:EE:FF", "192.168.1.100", "Unknown")
    print(f"Injected Unknown Device. Was it new? {is_new}")

if __name__ == "__main__":
    inject_mock_devices()
    print("Check your dashboard at http://127.0.0.1:5000 ! (It refreshes every 10 seconds)")
