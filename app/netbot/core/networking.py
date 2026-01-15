from pythonping import ping
from typing import Dict, List
import subprocess
import socket
import re
import ipaddress


def ping_host(host: str, count: int = 4, timeout: int = 2) -> Dict[str, str]:
    """
    Ping a host and return status and average latency.
    """
    try:
        response_list = ping(host, count=count, timeout=timeout)
        avg_latency = round(response_list.rtt_avg_ms, 2)
        success = response_list.success()
        return {
            "host": host,
            "status": "online" if success else "offline",
            "avg_latency_ms": str(avg_latency) if success else None
        }
    except Exception as e:
        return {
            "host": host,
            "status": "error",
            "error": str(e)
        }


def get_local_ip() -> Dict[str, str]:
    """
    Get the local IP address of this machine.
    """
    try:
        # Connect to an external host to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        try:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        finally:
            s.close()
        
        return {
            "status": "success",
            "ip": local_ip,
            "interface": "Primary"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def get_default_gateway() -> Dict[str, str]:
    """
    Get the default gateway using Windows route command.
    More reliable than ipconfig on Windows 11.
    """
    try:
        result = subprocess.run(
            ["route", "print", "0.0.0.0"],
            capture_output=True,
            text=True,
            timeout=5,
            encoding='utf-8',
            errors='ignore'
        )
        
        # Parse route output for default gateway
        lines = result.stdout.split('\n')
        for line in lines:
            # Look for line with 0.0.0.0 (default route)
            if '0.0.0.0' in line and 'On-link' not in line:
                # Extract IP addresses from the line
                ips = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                # The gateway is typically the 3rd IP in the route output
                if len(ips) >= 3:
                    return {
                        "status": "success",
                        "gateway": ips[2]
                    }
        
        return {
            "status": "error",
            "error": "Could not find default gateway"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def scan_local_network() -> Dict[str, any]:
    """
    Scan the local network for active devices using ARP.
    Windows 11 compatible - uses 'arp -a' command.
    """
    try:
        # Get local network info first
        local_info = get_local_ip()
        if local_info["status"] != "success":
            return {
                "status": "error",
                "error": "Could not determine local IP"
            }
        
        # Run arp -a to get ARP cache
        result = subprocess.run(
            ["arp", "-a"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='ignore'
        )
        
        devices = []
        lines = result.stdout.split('\n')
        
        for line in lines:
            # Match lines with IP addresses in ARP table
            # Format: "  192.168.1.1           b0-a7-b9-63-f6-b8     dynamic"
            match = re.search(r'\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+([\w-]+)\s+(\w+)', line)
            if match:
                ip = match.group(1)
                mac = match.group(2)
                entry_type = match.group(3)
                
                # Skip multicast and broadcast addresses
                if ip.startswith('224.') or ip.startswith('239.') or ip.endswith('.255'):
                    continue
                
                # Try to get hostname (with timeout)
                hostname = "Unknown"
                try:
                    socket.setdefaulttimeout(0.5)
                    hostname = socket.gethostbyaddr(ip)[0]
                except:
                    pass
                finally:
                    socket.setdefaulttimeout(None)
                
                devices.append({
                    "ip": ip,
                    "mac": mac,
                    "hostname": hostname,
                    "status": "online"
                })
        
        return {
            "status": "success",
            "devices": devices,
            "network": local_info.get("ip", "unknown")
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def check_port(host: str, port: int, timeout: int = 1) -> bool:
    """
    Check if a specific port is open on a host.
    Reduced timeout for faster scanning.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def check_ports(host: str, ports: List[int]) -> Dict[str, any]:
    """
    Check multiple ports on a host.
    """
    try:
        results = []
        
        # Common service names for ports
        service_names = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            8080: "HTTP-Alt"
        }
        
        for port in ports:
            is_open = check_port(host, port)
            results.append({
                "port": port,
                "open": is_open,
                "service": service_names.get(port, "Unknown")
            })
        
        return {
            "status": "success",
            "host": host,
            "ports": results
        }
    except Exception as e:
        return {
            "status": "error",
            "host": host,
            "error": str(e)
        }


def dns_lookup(hostname: str) -> Dict[str, any]:
    """
    Perform DNS lookup for a hostname.
    """
    try:
        addresses = socket.gethostbyname_ex(hostname)[2]
        return {
            "status": "success",
            "hostname": hostname,
            "addresses": addresses
        }
    except Exception as e:
        return {
            "status": "error",
            "hostname": hostname,
            "error": str(e)
        }


def traceroute(host: str, max_hops: int = 30) -> Dict[str, any]:
    """
    Perform traceroute to a host using Windows tracert command.
    """
    try:
        result = subprocess.run(
            ["tracert", "-h", str(max_hops), "-w", "1000", host],
            capture_output=True,
            text=True,
            timeout=90,
            encoding='utf-8',
            errors='ignore'
        )
        
        hops = []
        lines = result.stdout.split('\n')
        hop_num = 0
        
        for line in lines:
            # Skip header lines
            if 'Tracing route' in line or 'over a maximum' in line or not line.strip():
                continue
                
            # Match tracert output lines - more flexible pattern
            # Format: "  1    <1 ms    <1 ms    <1 ms  192.168.1.1"
            # Or:     "  2     *        *        *     Request timed out."
            if re.match(r'\s*\d+', line):
                hop_num += 1
                
                # Extract IP or hostname
                ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                hostname_match = re.search(r'([\w\.\-]+\.\w{2,})\s*(?:\[|$)', line)
                
                if 'timed out' in line.lower() or '*' in line:
                    destination = "*"
                    avg_time = "*"
                elif ip_match:
                    destination = ip_match.group(1)
                    # Extract timing info
                    times = re.findall(r'(\d+)\s*ms', line)
                    avg_time = round(sum(int(t) for t in times) / len(times), 1) if times else "*"
                elif hostname_match:
                    destination = hostname_match.group(1)
                    times = re.findall(r'(\d+)\s*ms', line)
                    avg_time = round(sum(int(t) for t in times) / len(times), 1) if times else "*"
                else:
                    continue
                
                hops.append({
                    "hop": hop_num,
                    "ip": destination,
                    "rtt": f"{avg_time}ms" if avg_time != "*" else "*"
                })
        
        return {
            "status": "success",
            "host": host,
            "hops": hops
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "host": host,
            "error": "Traceroute timed out - destination may be unreachable"
        }
    except Exception as e:
        return {
            "status": "error",
            "host": host,
            "error": str(e)
        }
