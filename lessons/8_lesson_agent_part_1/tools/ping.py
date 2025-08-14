import subprocess


def ping(host: str) -> bool:
    """
    Checks host availability via ICMP (ping)

    Arguments:
        host (str): IP address or domain name of the host.

    Returns:
        bool: True if the host responds, otherwise False.
    """
    try:
        # Ping the host 2 times (for Unix systems)
        command = ["ping", "-c", "2", host]
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return result.returncode == 0
    except Exception:
        # In case of error — consider the host unavailable
        return False
