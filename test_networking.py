from netbot.core.networking import (
    scan_local_network,
    ping_host,
    check_ports,
    dns_lookup
)
import json

print("Testing Network Functions\n" + "="*50)

# Test 1: Ping google.com
print("\n1. Testing ping_host('google.com')...")
result = ping_host('google.com')
print(json.dumps(result, indent=2))

# Test 2: Get default gateway
from netbot.core.networking import get_default_gateway
print("\n2. Testing get_default_gateway()...")
result = get_default_gateway()
print(json.dumps(result, indent=2))

# Test 3: Scan network
print("\n3. Testing scan_local_network()...")
result = scan_local_network()
print(f"Found {len(result.get('devices', []))} devices")
for device in result.get('devices', [])[:5]:
    print(f"  - {device['ip']} ({device['hostname']}) - {device['mac']}")

# Test 4: DNS lookup
print("\n4. Testing dns_lookup('google.com')...")
result = dns_lookup('google.com')
print(json.dumps(result, indent=2))

# Test 5: Port check
print("\n5. Testing check_ports('google.com', [80, 443])...")
result = check_ports('google.com', [80, 443])
print(json.dumps(result, indent=2))

print("\n" + "="*50)
print("All tests completed!")
