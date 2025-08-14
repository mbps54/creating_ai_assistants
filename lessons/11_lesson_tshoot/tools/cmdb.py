# CMDB Example

device_inventory = {
    "asw1": "192.168.1.10",      # Access Switch 1
    "asw2": "192.168.1.11",      # Access Switch 2
    "asw3": "192.168.1.12",      # Access Switch 3
    "dsw1": "192.168.2.1",       # Distribution Switch 1
    "dsw2": "192.168.2.2",       # Distribution Switch 2
    "core1": "192.168.3.1",      # Core Switch
    "fw1": "192.168.254.1",      # Firewall 1
    "vpn-gw": "192.168.100.1",   # VPN Gateway
    "rtr-edge": "10.0.0.1",      # Edge Router
    "wlc1": "192.168.200.10"     # Wireless LAN Controller
}


def cmdb(name: str) -> str:
    """
    Searches for a device’s IP address by its name in the CMDB database.

    Arguments:
        name (str): Device name (for example, “asw1”)..

    Returns:
        str: The device’s IP address if found, otherwise an error message.
    """
    ip = device_inventory.get(name)
    if ip:
        return ip
    else:
        return f"Device with name {name} not found."