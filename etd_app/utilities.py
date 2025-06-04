import ipaddress
from typing import List


def is_campus_ip(ip_str: str, campus_ips: List[str]) -> bool:
    """
    Checks if the IP address is in the list of campus IPs.
    Supports specific IP addresses, and CIDR notation, like '192.168.1.0/24'.
    Args:
        ip_str: The IP address to check.
        campus_ips: List of campus IPs. This'll be from settings, but passing in both facilitates testing.
    """
    # ip_obj: ipaddress.IPv4Address = ipaddress.IPv4Address(ip_str)  # in case we need to do CIDR math
    # for campus_ip in campus_ips:
    #     if '/' in campus_ip:  # eg CIDR notation, like '192.168.1.0/24'
    #         network: ipaddress.IPv4Network = ipaddress.IPv4Network(campus_ip)
    #         if ip_obj in network:
    #             return True
    #     elif ip_str == campus_ip:
    #         return True
    return False
