# Simulation of VLAN state on switch ports
VLAN_STATE = {
    "192.168.1.10": {
        f"Gi0/{i}": 10 if i <= 8 else 20 if i <= 16 else 30
        for i in range(1, 25)
    },
    "192.168.1.11": {
        f"Gi0/{i}": 1 if i % 2 == 0 else 40
        for i in range(1, 25)
    },
    "192.168.1.12": {
        f"Gi0/{i}": 50 if i <= 12 else 60
        for i in range(1, 25)
    },
    "192.168.2.1": {
        f"Gi1/0/{i}": 99 if i in [1, 2] else 10
        for i in range(1, 25)
    },
    "192.168.2.2": {
        f"Gi1/0/{i}": 20 if i <= 12 else 30
        for i in range(1, 25)
    },
    "192.168.3.1": {
        f"Ten0/{i}": 1 if i in [1, 4] else 99
        for i in range(1, 9)
    },
    "192.168.254.1": {
        f"Gi0/{i}": 1 if i <= 4 else 100
        for i in range(0, 8)
    },
    "192.168.100.1": {
        f"Gi0/{i}": 100 if i <= 4 else 1
        for i in range(0, 8)
    },
    "10.0.0.1": {
        f"Gi0/{i}": 1 if i % 2 == 0 else 99
        for i in range(0, 8)
    },
    "10.0.0.2": {
        f"Gi0/{i}": 100
        for i in range(0, 8)
    },
}


def show_vlan_port(ip: str, port: str) -> str:
    """
    Shows the VLAN assigned to a specific device port

    Arguments:
        ip (str): IP address of the device.
        port (str): Port name (for example, “Gi0/5”).

    Returns:
        str: A string with VLAN information or an error message.
    """
    if ip not in VLAN_STATE:
        return f"Device with IP {ip} not found in the database"

    device_ports = VLAN_STATE[ip]

    if port not in device_ports:
        return f"Port {port} not found on device {ip}."

    vlan = device_ports[port]
    return f"Port {port} on device {ip} is configured in VLAN {vlan}."