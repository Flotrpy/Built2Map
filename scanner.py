import socket
import ipaddress
import platform
import subprocess
from scapy.all import conf

def get_local_subnet():
    """
    Attempts to identify the local subnet dynamically by examining Scapy's routing table.
    """
    # Scapy's conf.route holds the routing table
    # We look for a route that is not multicast or loopback and has a valid interface IP
    routes = conf.route.routes
    for route in routes:
        network, netmask, gateway, interface, output_ip, _ = route
        
        # Skip loopback (127.0.0.0/8), multicast (224.0.0.0/4), and 0.0.0.0 (default route usually)
        if output_ip == '127.0.0.1' or network == 0:
            continue
            
        # Convert network and netmask (which are integers in scapy < 2.5 or strings sometimes) to IP string
        # Scapy conf.route has methods to help with this in newer versions or we can use ipaddress
        # Actually, it's safer to just get the IP and use the netmask.
        # Let's write a simple helper using socket instead for reliability if Scapy's routing is complex
        pass
        
    # Standard fallback using socket to get our own IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # isn't actually making a connection
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()

    if IP == '127.0.0.1':
        return None

    # Construct the subnet dynamically using regex to handle extra characters if any
    import re
    match = re.search(r'^(\d+\.\d+\.\d+)\.\d+', IP)
    if match:
        subnet = f"{match.group(1)}.0/24"
    else:
        subnet = "192.168.1.0/24"
    return subnet

def arp_sweep(subnet):
    """
    Performs an ARP ping sweep on the given subnet.
    """
    from scapy.all import ARP, Ether, srp
    import logging
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR) # suppress warnings

    print(f"[*] Starting ARP sweep on {subnet}")
    # Construct an ARP request to the broadcast MAC
    arp_request = ARP(pdst=subnet)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request

    try:
        # Send packets and receive answered ones
        answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    except Exception as e:
        print(f"[!] Error during ARP sweep: {e}")
        return []

    devices = []
    for element in answered_list:
        client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        devices.append(client_dict)
        print(f"    Discovered: IP {client_dict['ip']} \t MAC {client_dict['mac']}")

    return devices

if __name__ == "__main__":
    subnet = get_local_subnet()
    if subnet:
        arp_sweep(subnet)
    else:
        print("Could not detect local subnet.")
