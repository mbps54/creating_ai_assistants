import ipaddress

SWITCHES = {
    "192.168.1.10": {
        "name": "asw1",
        "ports": ["Gi0/" + str(i) for i in range(1, 25)],
        "vlans": [10, 20, 30, 40, 50]
    },
    "192.168.1.11": {
        "name": "asw2",
        "ports": ["Gi0/" + str(i) for i in range(1, 25)],
        "vlans": [10, 20, 30, 40, 50]
    },
    "192.168.1.12": {
        "name": "asw3",
        "ports": ["Gi0/" + str(i) for i in range(1, 25)],
        "vlans": [10, 20, 30, 40, 50]
    },
    "192.168.2.1": {
        "name": "dsw1",
        "ports": ["Gi1/0/" + str(i) for i in range(1, 25)],
        "vlans": [10, 20, 30, 100, 200]
    },
    "192.168.2.2": {
        "name": "dsw2",
        "ports": ["Gi1/0/" + str(i) for i in range(1, 25)],
        "vlans": [10, 20, 30, 100, 200]
    },
    "192.168.3.1": {
        "name": "core1",
        "ports": ["Ten0/" + str(i) for i in range(1, 9)],
        "vlans": [10, 20, 30, 100, 200, 300]
    }
}


# Simulation of VLAN configuration on a device port
def change_vlan(ip: str, port: str, vlan: int) -> str:
    """
    Simulates changing the VLAN on a specified port of a network switch.

    Checks the validity of the IP address, existence of the device in the database,
    presence of the port, and support for the specified VLAN.
    Returns the result as a text message.

    Arguments:
        ip (str): IPv4 address of the switch.
        port (str): Port name (for example, “Gi0/1”).
        vlan (int): VLAN to be assigned.

    Returns:
        str: Execution status or error message.

    Exceptions:
        ValueError: If the IP address format is invalid.
    """
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        raise ValueError("change_vlan() accepts only a valid IPv4 address.")

    if ip not in SWITCHES:
        return f"Device with IP {ip} not found."

    switch = SWITCHES[ip]

    if port not in switch["ports"]:
        return f"Port {port} not found on device {switch['name']} ({ip})."

    if vlan not in switch["vlans"]:
        return f"VLAN {vlan} is not configured on device {switch['name']} ({ip})."

    return f"VLAN on port {port} of device {switch['name']} ({ip}) successfully changed to VLAN {vlan}."