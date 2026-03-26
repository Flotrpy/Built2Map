import asyncio
from mac_vendor_lookup import AsyncMacLookup, MacLookup

def init_mac_lookup():
    """
    Downloads the latest OUI database if not found locally.
    In a real scenario, this runs once to populate the cache.
    """
    mac = MacLookup()
    try:
        mac.update_vendors()
        print("[*] MAC Vendor DB updated successfully.")
    except Exception as e:
        print(f"[!] Warning: Could not download latest MAC Vendors: {e}. Using bundled/cached.")

def get_vendor_sync(mac_address):
    """
    Looks up the manufacturer asynchronously to avoid blocking the main server threads.
    Checks for locally administered (randomized) MAC addresses first.
    """
    try:
        # Secondary character of MAC determines if it's locally administered
        # e.g. x2:xx:xx:xx:xx:xx, x6, xA, xE
        if len(mac_address) >= 2:
            second_char = mac_address[1].upper()
            if second_char in ['2', '6', 'A', 'E']:
                return "Randomized (Private MAC)"

        mac = MacLookup()
        vendor = mac.lookup(mac_address)
        return vendor
    except KeyError:
        return "Unknown"
    except Exception as e:
        return "Unknown"

if __name__ == "__main__":
    init_mac_lookup()
    # Test lookup
    test_macs = ["00:1A:2B:3C:4D:5E", "FF:FF:FF:FF:FF:FF"]
    for m in test_macs:
        print(f"{m} -> {get_vendor_sync(m)}")
