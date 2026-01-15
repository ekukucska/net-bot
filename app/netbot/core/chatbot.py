import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Intent:
    """Represents a parsed user intent"""
    action: str
    parameters: Dict[str, any]
    confidence: float


class ChatBot:
    """
    Rule-based chatbot for network diagnostics.
    Uses regex patterns to identify user intents.
    """
    
    def __init__(self):
        # Define intent patterns (order matters - more specific first)
        self.patterns = [
            # Ping specific host
            {
                "regex": r"(?:ping|check|test)\s+(?:connection\s+to\s+)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[\w\.-]+)",
                "action": "ping",
                "extractor": self._extract_host
            },
            # Scan network / list devices
            {
                "regex": r"(?:scan|find|list|show|discover)\s+(?:all\s+)?(?:devices?|hosts?|computers?|network|lan)",
                "action": "scan_network",
                "extractor": lambda m: {}
            },
            # Check ports on a host
            {
                "regex": r"(?:check|test|scan)\s+ports?\s+(?:on\s+)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[\w\.-]+)(?:\s+(\d+(?:,\d+)*))?",
                "action": "check_ports",
                "extractor": self._extract_host_and_ports
            },
            # Get local IP
            {
                "regex": r"(?:what(?:'s| is)|show|get)\s+(?:my\s+)?(?:local\s+)?ip(?:\s+address)?",
                "action": "get_local_ip",
                "extractor": lambda m: {}
            },
            # Get gateway
            {
                "regex": r"(?:what(?:'s| is)|show|get)\s+(?:my\s+)?(?:default\s+)?gateway",
                "action": "get_gateway",
                "extractor": lambda m: {}
            },
            # Trace route
            {
                "regex": r"(?:trace|traceroute|tracert)\s+(?:to\s+)?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[\w\.-]+)",
                "action": "traceroute",
                "extractor": self._extract_host
            },
            # DNS lookup
            {
                "regex": r"(?:lookup|resolve|dns|nslookup)\s+(\S+)",
                "action": "dns_lookup",
                "extractor": self._extract_host
            },
            # Help
            {
                "regex": r"(?:help|what can you do|commands?|capabilities)",
                "action": "help",
                "extractor": lambda m: {}
            },
        ]
    
    def parse_message(self, message: str) -> Intent:
        """
        Parse user message and extract intent.
        Returns Intent object with action and parameters.
        """
        message = message.lower().strip()
        
        # Try to match each pattern
        for pattern in self.patterns:
            match = re.search(pattern["regex"], message, re.IGNORECASE)
            if match:
                params = pattern["extractor"](match)
                return Intent(
                    action=pattern["action"],
                    parameters=params,
                    confidence=1.0
                )
        
        # No match found
        return Intent(
            action="unknown",
            parameters={"original_message": message},
            confidence=0.0
        )
    
    def _extract_host(self, match: re.Match) -> Dict[str, str]:
        """Extract host from regex match"""
        return {"host": match.group(1)}
    
    def _extract_host_and_ports(self, match: re.Match) -> Dict[str, any]:
        """Extract host and optional ports from regex match"""
        host = match.group(1)
        ports_str = match.group(2) if len(match.groups()) > 1 and match.group(2) else "22,80,443"
        ports = [int(p.strip()) for p in ports_str.split(",")]
        return {"host": host, "ports": ports}
    
    def get_help_text(self) -> str:
        """Return help text with available commands"""
        return """I can help you with network diagnostics! Here's what I can do:

🔹 **Ping a device**: "ping 192.168.1.1" or "check connection to google.com"
🔹 **Scan network**: "scan network" or "list all devices"
🔹 **Check ports**: "check ports on 192.168.1.1" or "scan ports 192.168.1.10 22,80,443"
🔹 **Get local IP**: "what's my IP address?"
🔹 **Get gateway**: "what's my default gateway?"
🔹 **Trace route**: "traceroute to google.com"
🔹 **DNS lookup**: "lookup google.com"

Just type your question naturally, and I'll help you diagnose your network!"""
    
    def format_response(self, action: str, result: Dict) -> str:
        """
        Format technical results into friendly, human-readable responses.
        """
        if action == "help":
            return self.get_help_text()
        
        elif action == "unknown":
            return ("I'm not sure what you're asking. Type 'help' to see what I can do! "
                   "Try asking things like 'ping 192.168.1.1' or 'scan network'.")
        
        elif action == "ping":
            return self._format_ping_response(result)
        
        elif action == "scan_network":
            return self._format_scan_response(result)
        
        elif action == "check_ports":
            return self._format_ports_response(result)
        
        elif action == "get_local_ip":
            return self._format_local_ip_response(result)
        
        elif action == "get_gateway":
            return self._format_gateway_response(result)
        
        elif action == "traceroute":
            return self._format_traceroute_response(result)
        
        elif action == "dns_lookup":
            return self._format_dns_response(result)
        
        else:
            return f"Action completed: {action}"
    
    def _format_ping_response(self, result: Dict) -> str:
        """Format ping results"""
        if result.get("status") == "online":
            latency = result.get("avg_latency_ms", "N/A")
            return f"✅ **{result['host']}** is online! Average response time: {latency}ms"
        elif result.get("status") == "offline":
            return f"❌ **{result['host']}** is not responding. The device might be offline or blocking pings."
        else:
            error = result.get("error", "Unknown error")
            return f"⚠️ Error pinging **{result.get('host', 'host')}**: {error}"
    
    def _format_scan_response(self, result: Dict) -> str:
        """Format network scan results"""
        if result.get("status") == "error":
            return f"⚠️ Scan error: {result.get('error', 'Unknown error')}"
        
        devices = result.get("devices", [])
        if not devices:
            return "🔍 No devices found on the network."
        
        response = f"🔍 Found **{len(devices)}** device(s) on the network:\n\n"
        for device in devices:
            ip = device.get("ip", "unknown")
            hostname = device.get("hostname", "N/A")
            mac = device.get("mac", "N/A")
            status = "✅" if device.get("status") == "online" else "❌"
            response += f"{status} **{ip}** - {hostname} (MAC: {mac})\n"
        
        return response
    
    def _format_ports_response(self, result: Dict) -> str:
        """Format port scan results"""
        if result.get("status") == "error":
            return f"⚠️ Port scan error: {result.get('error', 'Unknown error')}"
        
        host = result.get("host", "unknown")
        ports = result.get("ports", [])
        
        response = f"🔍 Port scan results for **{host}**:\n\n"
        for port_info in ports:
            port = port_info.get("port")
            is_open = port_info.get("open", False)
            service = port_info.get("service", "unknown")
            status = "✅ OPEN" if is_open else "❌ CLOSED"
            response += f"{status} - Port **{port}** ({service})\n"
        
        return response
    
    def _format_local_ip_response(self, result: Dict) -> str:
        """Format local IP response"""
        if result.get("status") == "error":
            return f"⚠️ Error: {result.get('error', 'Could not determine local IP')}"
        
        ip = result.get("ip", "unknown")
        interface = result.get("interface", "N/A")
        return f"🌐 Your local IP address is **{ip}** (Interface: {interface})"
    
    def _format_gateway_response(self, result: Dict) -> str:
        """Format gateway response"""
        if result.get("status") == "error":
            return f"⚠️ Error: {result.get('error', 'Could not determine gateway')}"
        
        gateway = result.get("gateway", "unknown")
        return f"🌐 Your default gateway is **{gateway}**"
    
    def _format_traceroute_response(self, result: Dict) -> str:
        """Format traceroute response"""
        if result.get("status") == "error":
            return f"⚠️ Traceroute error: {result.get('error', 'Unknown error')}"
        
        host = result.get("host", "unknown")
        hops = result.get("hops", [])
        
        response = f"🛤️ Route to **{host}**:\n\n"
        for hop in hops:
            num = hop.get("hop")
            ip = hop.get("ip", "*")
            rtt = hop.get("rtt", "*")
            response += f"{num}. {ip} ({rtt})\n"
        
        return response
    
    def _format_dns_response(self, result: Dict) -> str:
        """Format DNS lookup response"""
        if result.get("status") == "error":
            return f"⚠️ DNS lookup error: {result.get('error', 'Unknown error')}"
        
        hostname = result.get("hostname", "unknown")
        addresses = result.get("addresses", [])
        
        if not addresses:
            return f"⚠️ No DNS records found for **{hostname}**"
        
        response = f"🌐 DNS records for **{hostname}**:\n\n"
        for addr in addresses:
            response += f"• {addr}\n"
        
        return response
